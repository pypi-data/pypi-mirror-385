"""Inspecting, authoring and editing foundational tools for the pipeline.

.. data:: Repository

    :class:`contextvars.ContextVar` for the global asset repository location.

    Its value must always be set to a :class:`pathlib.Path`.

    .. attention::
        By default, no value has been set. Ensure to set it before performing any creation operation.

    Example:
        >>> Repository.get()  # not set
        Traceback (most recent call last):
          File "<input>", line 1, in <module>
        LookupError: <ContextVar name='Repository' at 0x00000207F0A12B88>
        >>> import tempfile
        >>> from pathlib import Path
        >>> Repository.set(Path(tempfile.mkdtemp()))
        <Token var=<ContextVar name='Repository' at 0x00000213A46FF900> at 0x00000213C6A9F0C0>
        >>> Repository.get()
        WindowsPath('C:/Users/CHRIST~1/AppData/Local/Temp/tmp767wqaya')

"""
from __future__ import annotations

import types
import logging
import functools
import itertools
import contextlib
import contextvars
from pathlib import Path
from pprint import pformat
from collections import abc

import networkx as nx
from pxr import UsdGeom, Usd, Sdf, Kind, Ar

try:
    from grill.tokens import ids
    from grill.names import UsdAsset
except ImportError as exc:
    raise ImportError("In order to use the 'grill.cook' module, the 'grill-names' package mustbe installed") from exc

from .. import usd as _usd

logger = logging.getLogger(__name__)

Repository = contextvars.ContextVar('Repository')

_TAXA_KEY = 'taxa'
_FIELDS_KEY = 'fields'
_ASSETINFO_KEY = 'grill'
_ASSETINFO_TAXA_KEY = f'{_ASSETINFO_KEY}:{_TAXA_KEY}'
_ASSETINFO_FIELDS_KEY = f'{_ASSETINFO_KEY}:{_FIELDS_KEY}'

# Taxonomy rank handles the grill classification and grouping of assets.
_TAXONOMY_NAME = 'Taxonomy'
_TAXONOMY_ROOT_PATH = Sdf.Path.absoluteRootPath.AppendChild(_TAXONOMY_NAME)
_TAXONOMY_UNIQUE_ID = ids.CGAsset.cluster  # High level organization of our assets.
_TAXONOMY_FIELDS = types.MappingProxyType({_TAXONOMY_UNIQUE_ID.name: _TAXONOMY_NAME})
_ASSETINFO_TAXON_KEY = f'{_ASSETINFO_FIELDS_KEY}:{_TAXONOMY_UNIQUE_ID.name}'

_CATALOGUE_NAME = 'Catalogue'
_CATALOGUE_ROOT_PATH = Sdf.Path.absoluteRootPath.AppendChild(_CATALOGUE_NAME)
_CATALOGUE_ID = ids.CGAsset.kingdom  # where all existing units will be "discoverable"
_CATALOGUE_FIELDS = types.MappingProxyType({_CATALOGUE_ID.name: _CATALOGUE_NAME})

_INHERITED_ROOT_PATH = Sdf.Path.absoluteRootPath.AppendChild('Inherited')
_SPECIALIZED_ROOT_PATH = Sdf.Path.absoluteRootPath.AppendChild('Specialized')
_BROADCAST_METHOD_RELPATHS = {Usd.Inherits: _INHERITED_ROOT_PATH, Usd.Specializes: _SPECIALIZED_ROOT_PATH}

_UNIT_UNIQUE_ID = ids.CGAsset.item  # Entry point for meaningful composed assets.
_UNIT_ORIGIN_PATH = Sdf.Path.absoluteRootPath.AppendChild("Origin")

# Composition filters for asset edits
_ASSET_UNIT_QUERY_FILTER = Usd.PrimCompositionQuery.Filter()
_ASSET_UNIT_QUERY_FILTER.dependencyTypeFilter = Usd.PrimCompositionQuery.DependencyTypeFilter.Direct
_ASSET_UNIT_QUERY_FILTER.hasSpecsFilter = Usd.PrimCompositionQuery.HasSpecsFilter.HasSpecs


def _fetch_layer(identifier: str, context: Ar.ResolverContext) -> Sdf.Layer:
    """Retrieve `layer <https://graphics.pixar.com/usd/docs/api/class_sdf_layer.html>`_ for the given ``identifier``.

     If the `layer <https://graphics.pixar.com/usd/docs/api/class_sdf_layer.html>`_ does not exist, it is created in the repository.
     """
    if not (layer := Sdf.Layer.Find(identifier) or Sdf.Layer.FindOrOpen(identifier)):
        # TODO: see how to make this repo_path better, seems very experimental atm.
        if context.IsEmpty():
            raise ValueError(f"Empty {context=} while fetching {identifier=}")
        repo_path = Path(context.Get()[0].GetSearchPath()[0])  # or just Repository.get()?
        # CreateNew adds overhead vs CreateAnonymous but already provides an identifier and ability to call layer.Save()
        return Sdf.Layer.CreateNew(str(repo_path / identifier))

    return layer


def asset_identifier(path: Path | str):
    """Since identifiers from relative paths can become absolute when opening existing assets, this function ensures to return the value expected to be authored in layers."""
    # TODO: temporary public. mmm
    # Expect identifiers to not have folders in between.
    if not path:
        raise ValueError("Can not extract asset identifier from empty path.")
    path = Path(path)
    if not path.is_absolute():
        return str(path)
    else:
        return str(path.relative_to(Repository.get()))


def fetch_stage(identifier: str | UsdAsset, context: Ar.ResolverContext = None, load: Usd.Stage.InitialLoadSet = Usd.Stage.LoadAll) -> Usd.Stage:
    """Retrieve the `stage <https://graphics.pixar.com/usd/docs/api/class_usd_stage.html>`_ whose root `layer <https://graphics.pixar.com/usd/docs/api/class_sdf_layer.html>`_ matches the given ``identifier``.

    If the `layer <https://graphics.pixar.com/usd/docs/api/class_sdf_layer.html>`_ does not exist, it is created in the repository.

    .. attention::
        ``identifier`` must be a valid :class:`grill.names.UsdAsset` name.

    """
    if isinstance(identifier, UsdAsset):
        identifier = identifier.name

    if not context:
        context = Ar.ResolverContext(Ar.DefaultResolverContext([str(Repository.get())]))

    with Ar.ResolverContextBinder(context):
        layer = _fetch_layer(identifier, context)
        return Usd.Stage.Open(layer, load=load)


def define_taxon(stage: Usd.Stage, name: str, *, references: tuple[Usd.Prim] = tuple(), id_fields: abc.Mapping[str, str] = types.MappingProxyType({})) -> Usd.Prim:
    """:ref:`Define <glossary:def>` a new `taxon group <https://en.wikipedia.org/wiki/Taxon>`_ for asset `taxonomy <https://en.wikipedia.org/wiki/Taxonomy>`_ and return it.

    If an existing ``taxon`` with the provided name already exists in the :usdcpp:`stage <UsdStage>`, it is used.

    The new ``taxon`` can extend from existing ``taxa`` via the ``references`` argument.

    Optional ``field=value`` items can be provided for identification purposes through ``id_fields``.

    """
    # This could create a new schema in the future if codeless schemas are allowed to be registered at runtime
    if name == _TAXONOMY_NAME:
        # TODO: prevent upper case lower case mismatch handle between multiple OS?
        #  (e.g. Windows considers both the same but Linux does not)
        raise ValueError(f"Can not define a taxon with reserved name: '{_TAXONOMY_NAME}'.")

    if not Sdf.Path.IsValidNamespacedIdentifier(name):
        raise ValueError(f"{name=} must be a valid identifier for a prim")
    reserved_fields = {_TAXONOMY_UNIQUE_ID, _UNIT_UNIQUE_ID}
    reserved_fields.update([i.name for i in reserved_fields])
    if intersection:=reserved_fields.intersection(id_fields):
        raise ValueError(f"Can not provide reserved id fields: {', '.join(map(str, intersection))}. Got fields: {', '.join(map(str, id_fields))}")

    fields = {
        (token.name if isinstance(token, ids.CGAsset) else token): value
        for token, value in id_fields.items()
    }
    if invalid_fields:=set(fields).difference(ids.CGAsset.__members__):
        raise ValueError(f"Got invalid id_field keys: {', '.join(invalid_fields)}. Allowed: {', '.join(ids.CGAsset.__members__)}")

    with taxonomy_context(stage):
        prim = stage.DefinePrim(_TAXONOMY_ROOT_PATH.AppendChild(name))
        with Sdf.ChangeBlock():
            prim_references = prim.GetReferences()
            for reference in references:
                prim_references.AddInternalReference(reference.GetPath())
            prim.GetInherits().AddInherit(prim.GetPath().ReplacePrefix(Sdf.Path.absoluteRootPath, _INHERITED_ROOT_PATH))  # TODO: needed?
            taxon_fields = {**fields, _TAXONOMY_UNIQUE_ID.name: name}
            prim.SetAssetInfoByKey(_ASSETINFO_KEY, {_FIELDS_KEY: taxon_fields, _TAXA_KEY: {name: 0}})

    return prim


def itaxa(stage: Usd.Stage) -> abc.Iterator[Usd.Prim]:
    """For the given stage, iterate existing taxa under the taxonomy hierarchy."""
    return filter(
        lambda prim: prim.GetAssetInfoByKey(_ASSETINFO_TAXA_KEY),
        _usd.iprims(stage, root_paths={_TAXONOMY_ROOT_PATH}, traverse_predicate=Usd.PrimAllPrimsPredicate)
    )


def _catalogue_path(taxon: Usd.Prim) -> Sdf.Path:
    taxon_fields = _get_id_fields(taxon)
    # Check if we need to enforce _CATALOGUE_ID to be on taxon fields
    relpath = taxon_fields[_TAXONOMY_UNIQUE_ID.name]
    if _CATALOGUE_ID.name in taxon_fields:  # TODO: ensure this can't be overwritten
        relpath = f"{taxon_fields[_CATALOGUE_ID.name]}{Sdf.Path.childDelimiter}{relpath}"
    return _CATALOGUE_ROOT_PATH.AppendPath(relpath)


def _broadcast_root_path(taxon, broadcast_method, scope_path=None):
    scope_path = scope_path or _catalogue_path(taxon)  # TODO: this feels strange, avoid the "or" later.
    return scope_path.ReplacePrefix(_CATALOGUE_ROOT_PATH, _BROADCAST_METHOD_RELPATHS[broadcast_method])


def create_many(taxon: Usd.Prim, names: abc.Iterable[str], labels: abc.Iterable[str] = tuple()) -> list[Usd.Prim]:
    """Create a new taxon member for each of the provided names.

    When creating hundreds or thousands of members, this provides a considerable performance improvement over :func:`create_unit`.

    The new members will be created as `prims <https://graphics.pixar.com/usd/docs/api/class_usd_prim.html>`_ on the given ``taxon``'s `stage <https://graphics.pixar.com/usd/docs/api/class_usd_stage.html>`_.

    .. seealso:: :func:`define_taxon` :func:`create_unit`
    """
    stage = taxon.GetStage()
    taxon_path = taxon.GetPath()
    taxon_fields = _get_id_fields(taxon)
    scope_path = _catalogue_path(taxon)
    specialized_path = _broadcast_root_path(taxon, Usd.Specializes, scope_path=scope_path)
    inherited_path = _broadcast_root_path(taxon, Usd.Inherits, scope_path=scope_path)

    current_asset_name, root_layer = _root_asset(stage)
    new_asset_name = UsdAsset(current_asset_name.get(**taxon_fields))
    # Edits will go to the first layer that matches a valid pipeline identifier
    # TODO: Evaluate if this agreement is robust enough for different workflows.

    # existing = {i.GetName() for i in _iter_taxa(taxon.GetStage(), *taxon.GetCustomDataByKey(_ASSETINFO_TAXA_KEY))}
    taxonomy_layer = _find_layer_matching(_TAXONOMY_FIELDS, stage.GetLayerStack())
    taxonomy_id = asset_identifier(taxonomy_layer.identifier)
    context = stage.GetPathResolverContext()
    if context.IsEmpty():  # Use a resolver context that is populated with the repository only when the context is empty.
        context = Ar.ResolverContext(Ar.DefaultResolverContext([str(Repository.get())]))

    try:
        catalogue_layer = _find_layer_matching(_CATALOGUE_FIELDS, stage.GetLayerStack())
    except ValueError:  # first time adding the catalogue layer
        catalogue_asset = current_asset_name.get(**_CATALOGUE_FIELDS)
        with Ar.ResolverContextBinder(context):
            catalogue_layer = _fetch_layer(str(catalogue_asset), context)
        catalogue_id = asset_identifier(catalogue_layer.identifier)
        root_layer.subLayerPaths.insert(0, catalogue_id)
        # TODO: try setting this on session layer?

    # Some workflows like houdini might load layers without permissions to edit
    # Since we know we are in a valid pipeline layer, temporarily allow edits
    # for our operations, then restore original permissions.
    current_permission = catalogue_layer.permissionToEdit
    catalogue_layer.SetPermissionToEdit(True)

    scope = stage.GetPrimAtPath(scope_path)

    def _fetch_layer_for_unit(name):
        layer_id = str(new_asset_name.get(**{_UNIT_UNIQUE_ID.name: name}))
        layer = _fetch_layer(layer_id, context)
        origin = Sdf.CreatePrimInLayer(layer, _UNIT_ORIGIN_PATH)
        origin.specifier = Sdf.SpecifierDef
        origin.specializesList.Prepend(specialized_path.AppendChild(name))
        origin.inheritPathList.Prepend(inherited_path.AppendChild(name))
        origin.referenceList.Prepend(Sdf.Reference(taxonomy_id, taxon_path))
        layer.defaultPrim = origin.name
        return layer

    labels = itertools.chain(labels, itertools.repeat(""))
    with Usd.EditContext(stage, catalogue_layer), Ar.ResolverContextBinder(context):
        # Scope collecting all units based on taxon
        if not scope:
            scope = stage.DefinePrim(scope_path)
        if not scope.IsModel():
            # We use groups to ensure our scope is part of a valid model hierarchy
            for path in scope.GetPath().GetPrefixes():
                Usd.ModelAPI(stage.GetPrimAtPath(path)).SetKind(Kind.Tokens.group)

        # Place "homogeneus" operations under SdfChangeBlock to let composition notifications be sent only when needed.
        with Sdf.ChangeBlock():
            prims_info = []
            for name, label in zip(names, labels):
                if not stage.GetPrimAtPath(path:=scope_path.AppendChild(name)):
                    stage.OverridePrim(path)
                layer = _fetch_layer_for_unit(name)
                layer_id = asset_identifier(layer.identifier)
                prims_info.append((name, label or name, path, layer, Sdf.Reference(layer_id)))

        prims_info = {stage.GetPrimAtPath(info[2]): info for info in prims_info}
        with Sdf.ChangeBlock():
            for prim, (name, label, *__, layer, reference) in prims_info.items():
                prim.GetReferences().AddReference(reference)
                with _usd.edit_context(reference, prim):
                    if hasattr(prim, "SetDisplayName"):  # USD-23.02+
                        prim.SetDisplayName(label)
                    UsdGeom.ModelAPI.Apply(prim)
                    modelAPI = Usd.ModelAPI(prim)
                    modelAPI.SetKind(Kind.Tokens.component)
                    modelAPI.SetAssetName(name)
                    modelAPI.SetAssetIdentifier(asset_identifier(layer.identifier))

    catalogue_layer.SetPermissionToEdit(current_permission)
    return list(prims_info)


def create_unit(taxon: Usd.Prim, name: str, label: str = "") -> Usd.Prim:
    """Create a unit member of the given ``taxon``, with an optional display label.

    The new member will be created as a `prim <https://graphics.pixar.com/usd/docs/api/class_usd_prim.html>`_ on the given ``taxon``'s `stage <https://graphics.pixar.com/usd/docs/api/class_usd_stage.html>`_.

    .. seealso:: :func:`define_taxon` and :func:`create_many`
    """
    return create_many(taxon, [name], [label])[0]


def taxonomy_context(stage: Usd.Stage) -> Usd.EditContext:
    """Get an `edit context <https://graphics.pixar.com/usd/docs/api/class_usd_edit_context.html>`_ where edits will target this `stage <https://graphics.pixar.com/usd/docs/api/class_usd_stage.html>`_'s taxonomy `layer <https://graphics.pixar.com/usd/docs/api/class_sdf_layer.html>`_.

    .. attention::
        If a valid taxonomy `layer <https://graphics.pixar.com/usd/docs/api/class_sdf_layer.html>`_ is not found on the `layer stack <https://graphics.pixar.com/usd/docs/USD-Glossary.html#USDGlossary-LayerStack>`_, one is added to the `stage <https://graphics.pixar.com/usd/docs/api/class_usd_stage.html>`_.
    """
    # https://en.wikipedia.org/wiki/Taxonomy_(biology)
    try:
        taxonomy_layer = _find_layer_matching(_TAXONOMY_FIELDS, stage.GetLayerStack())
    except ValueError:
        # Our layer is not yet on the current layer stack. Let's bring it.
        # TODO: first valid pipeline layer is ok? or should it be current edit target?
        # TODO: try setting this on session layer?
        root_asset, root_layer = _root_asset(stage)
        taxonomy_asset = root_asset.get(**_TAXONOMY_FIELDS)
        context = stage.GetPathResolverContext()
        if context.IsEmpty():  # Use a resolver context that is populated with the repository only when the context is empty.
            context = Ar.ResolverContext(Ar.DefaultResolverContext([str(Repository.get())]))
        with Ar.ResolverContextBinder(context):
            taxonomy_layer = _fetch_layer(str(taxonomy_asset), context)
        # Use paths relative to our repository to guarantee portability
        # taxonomy_id = str(Path(taxonomy_layer.realPath).relative_to(Repository.get()))
        taxonomy_id = asset_identifier(taxonomy_layer.identifier)
        taxonomy_root = Sdf.CreatePrimInLayer(taxonomy_layer, _TAXONOMY_ROOT_PATH)
        taxonomy_root.specifier = Sdf.SpecifierClass
        taxonomy_layer.defaultPrim = taxonomy_root.name
        root_layer.subLayerPaths.append(taxonomy_id)

    return Usd.EditContext(stage, taxonomy_layer)


def unit_context(prim: Usd.Prim) -> Usd.EditContext:
    """Get an `edit context <https://graphics.pixar.com/usd/docs/api/class_usd_edit_context.html>`_ where edits will target this `prim <https://graphics.pixar.com/usd/docs/api/class_usd_prim.html>`_'s unit root `layer <https://graphics.pixar.com/usd/docs/api/class_sdf_layer.html>`_."""
    # This targets the origin prim spec as the "entry point" edit target for a unit of a taxon.
    # This means some operations like specializes, inherits or internal reference / payloads
    # might not be able to be resolved (you will se an error like:
    # 'Cannot map </Catalogue/OtherPlace/CastleDracula> to current edit target.'
    layer = unit_asset(prim)

    def target_predicate(arc: Usd.CompositionArc):
        node = arc.GetTargetNode()
        return node.path == _UNIT_ORIGIN_PATH and node.layerStack.identifier.rootLayer == layer

    return _usd.edit_context(prim, _ASSET_UNIT_QUERY_FILTER, target_predicate)


def unit_asset(prim: Usd.Prim) -> Sdf.Layer:
    """Get the asset layer that acts as the 'entry point' for the given prim."""
    with Ar.ResolverContextBinder(prim.GetStage().GetPathResolverContext()):
        # Use Layer.Find since layer should have been open for the prim to exist.
        if layer:=Sdf.Layer.Find(Usd.ModelAPI(prim).GetAssetIdentifier().path):
            return layer
    fields = {**_get_id_fields(prim), _UNIT_UNIQUE_ID: Usd.ModelAPI(prim).GetAssetName()}
    return _find_layer_matching(fields, (i.layer for i in prim.GetPrimStack()))


def spawn_unit(parent: Usd.Prim, child: Usd.Prim, path: Sdf.Path = Sdf.Path.emptyPath, label: str = "") -> Usd.Prim:
    """Spawn a unit prim as a descendant of another.

    * Both parent and child must be existing units in the catalogue.
    * If ``path`` is not provided, the name of child will be used.
    * A valid :ref:`glossary:model hierarchy` is preserved by:

      1. Turning parent into an :ref:`glossary:assembly`.
      2. Ensuring intermediate prims between parent and child are also :ref:`glossary:model`.
      3. Setting explicit :ref:`glossary:instanceable`. on spawned children that are components.

    .. seealso:: :func:`spawn_many` and :func:`create_unit`
    """
    return spawn_many(parent, child, [path or child.GetName()], [label])[0]


def spawn_many(parent: Usd.Prim, child: Usd.Prim, paths: list[Sdf.Path], labels: list[str] = ()) -> list[Usd.Prim]:
    """Spawn many instances of a prim unit as descendants of another.

    * Both parent and child must be existing units in the catalogue.
    * ``paths`` can be relative or absolute. If absolute, they must include ``parent``'s `path <https://graphics.pixar.com/usd/docs/USD-Glossary.html#USDGlossary-Path>`_ as a prefix.
    * A valid `Model Hierarchy <https://graphics.pixar.com/usd/docs/USD-Glossary.html#USDGlossary-ModelHierarchy>`_ is preserved by:

      1. Turning parent into an `assembly <https://graphics.pixar.com/usd/docs/USD-Glossary.html#USDGlossary-Assembly>`_ if ``child`` is a Model.
      2. Ensuring intermediate prims between ``parent`` and spawned children are also `models <https://graphics.pixar.com/usd/docs/USD-Glossary.html#USDGlossary-Model>`_.
      3. Setting explicit `instanceable <https://graphics.pixar.com/usd/docs/USD-Glossary.html#USDGlossary-Instanceable>`_. on spawned children that are components.

    Spawned prims and ancestors are `defined <https://openusd.org/release/glossary.html#def>`_.

    .. seealso:: :func:`spawn_unit` and :func:`create_unit`
    """
    if parent == child:
        raise ValueError(f"Can not spawn {parent} on to itself.")
    parent_path = parent.GetPath()
    paths_to_create = []
    for path in paths:
        if isinstance(path, str):
            path = Sdf.Path(path)
        if path.IsAbsolutePath():  # If path is an absolute path, fail if it sits outside of parent's path.
            if not path.HasPrefix(parent_path) or path == parent_path:
                raise ValueError(f"{path=} needs to be a child path of parent path {parent_path}")
        else:
            path = parent_path.AppendPath(path)
        paths_to_create.append(path)
    labels = itertools.chain(labels, itertools.repeat(""))
    try:
        reference = asset_identifier(Usd.ModelAPI(child).GetAssetIdentifier().path)
    except ValueError:
        raise ValueError(f"Could not extract identifier from {child} to spawn under {parent}.")
    parent_stage = parent.GetStage()
    # Ensure prims are defined to spawn units unto (paths might be deep e.g. /world/parent/nested/path/for/child)
    spawned = [parent_stage.DefinePrim(path) for path in paths_to_create]
    child_is_model = child.IsModel()
    checked_parents = set()
    with Sdf.ChangeBlock():
        # Action of bringing a unit from our catalogue turns parent into an assembly only if child is a model.
        if child_is_model and not (parent_model := Usd.ModelAPI(parent)).IsKind(Kind.Tokens.assembly):
            try:
                parent_model.SetKind(Kind.Tokens.assembly)
            except Exception as exc:
                message = (
                    f'Could not set kind to "{Kind.Tokens.assembly}" on parent {parent} with current kind: "{parent_model.GetKind()}" '
                    f'when spawning {child} of kind "{Usd.ModelAPI(child).GetKind()}"'
                )
                edit_target = parent_stage.GetEditTarget()
                if not edit_target.GetSpecForScenePath(parent.GetPath()):
                    message = f"No spec path for {parent} could be found; it might be out of the scope of the current edit target with map {edit_target.GetMapFunction().sourceToTargetMap}. {message}"
                raise RuntimeError(message) from exc

        for spawned_unit, label in zip(spawned, labels):
            # Use reference for the asset to:
            # 1. Make use of instancing as much as possible with fewer prototypes.
            # 2. Let specializes / inherits changes later.
            spawned_unit.GetReferences().AddReference(reference)
            if label and hasattr(spawned_unit, "SetDisplayName"):  # USD-23.02+
                spawned_unit.SetDisplayName(label)
            # Action of bringing a unit from our catalogue turns parent into an assembly only if child is a model.
            if child_is_model:
                # check for all intermediate parents of our spawned unit to ensure valid model hierarchy
                inner_parent = spawned_unit.GetParent()
                while inner_parent != parent and inner_parent not in checked_parents:
                    if not inner_parent.IsModel():
                        Usd.ModelAPI(inner_parent).SetKind(Kind.Tokens.group)
                        checked_parents.add(inner_parent)
                    inner_parent = inner_parent.GetParent()

                if not child.IsGroup():
                    # Sensible defaults: component prims are instanced
                    spawned_unit.SetInstanceable(True)
    return spawned


def _root_asset(stage):
    """From a give stage, find the first layer that matches a valid grill identifier.

    This can be useful in situations when a stage's root layer is not a valid identifier (e.g. anonymous) but
    has sublayered a valid one in the pipeline.

    This searches on the root layer first.
    """
    with contextlib.suppress(ValueError):
        root_layer = stage.GetRootLayer()
        return UsdAsset(Path(root_layer.identifier).name), root_layer

    seen = set()
    for layer in stage.GetLayerStack():
        try:
            return UsdAsset(Path(layer.identifier).name), layer
        except ValueError:
            seen.add(layer)
    raise ValueError(f"Could not find a valid pipeline layer for stage {stage}. Searched layer stack: {pformat(seen)}")


def _get_id_fields(prim):
    if not (fields:=prim.GetAssetInfoByKey(_ASSETINFO_FIELDS_KEY)):
        raise ValueError(f"Missing or empty '{_FIELDS_KEY}' on '{_ASSETINFO_KEY}' asset info for {prim}. Got: {pformat(prim.GetAssetInfoByKey(_ASSETINFO_KEY))}")
    if not isinstance(fields, abc.Mapping):
        raise TypeError(f"Expected mapping on key '{_FIELDS_KEY}' from {prim} on custom data key '{_ASSETINFO_KEY}'. Got instead {fields} with type: {type(fields)}")
    return fields


def _find_layer_matching(tokens: abc.Mapping, layers: abc.Iterable[Sdf.Layer]) -> Sdf.Layer:
    """Find the first layer matching the given identifier tokens.

    :raises ValueError: If none of the given layers match the provided tokens.
    """
    tokens = {
        ((token.name if isinstance(token, ids.CGAsset) else token), value)
        for token, value in tokens.items()
    }
    seen = set()
    for layer in layers:
        # anonymous layers realPath defaults to an empty string
        name = UsdAsset(Path(layer.realPath).name)
        if tokens.difference(name.values.items()):
            seen.add(layer)
            continue
        return layer
    raise ValueError(f"Could not find layer matching {tokens}. Searched on:\n{pformat(seen)}")


def specialized_context(prim, context_unit=None):
    return _inherit_or_specialize_unit(prim.GetSpecializes(), context_unit)


def inherited_context(prim, context_unit=None):
    return _inherit_or_specialize_unit(prim.GetInherits(), context_unit)


def _inherit_or_specialize_unit(method, context_unit):
    """This is on cook since it relies on some pipeline knowledge to find proper target. Could request the target
    path as well at the expense of the caller if need arises or enough value is perceived."""
    target_prim = method.GetPrim()
    if not (unit_name:=Usd.ModelAPI(target_prim).GetAssetName()):
        raise ValueError(f"{target_prim} is not a valid unit in the catalogue.")

    context_unit = context_unit or target_prim
    if not (modelAPI:=Usd.ModelAPI(context_unit)).GetAssetName():
        raise ValueError(f"{context_unit=} needs to be a valid unit in the catalogue. Currently it has a kind of '{modelAPI.GetKind()}' and asset info of {modelAPI.GetAssetInfo()}")

    broadcast_method = type(method)
    if not target_prim.GetPath().HasPrefix(context_unit.GetPath()):
        raise ValueError(f"Can not check for {broadcast_method} on {context_unit} since {target_prim} is not a descendant of it.")

    target_path = _broadcast_root_path(target_prim, broadcast_method).AppendPath(unit_name)

    try:
        return _usd.edit_context(method, target_path, (context_asset:=unit_asset(context_unit)))
    except ValueError as exc:
        raise ValueError(
            f"Could not find an appropriate edit target node for a {broadcast_method.__name__}'s arc targeting {target_path} for {target_prim}. "
            f"""Is there a composition arc bringing "{target_prim.GetName()}"'s prim unit into "{context_unit.GetName()}"'s layer stack at {context_asset}?"""
        ) from exc


@functools.singledispatch
def taxonomy_graph(prims: Usd.Prim, url_id_prefix: str) -> nx.DiGraph:
    """Get the hierarchical taxonomy representation of existing prims."""
    graph = nx.DiGraph(tooltip="Taxonomy Graph")
    graph.graph.update(
        graph={'rankdir': 'LR'},
        node={
            'shape': 'box',
            'fillcolor': "#afd7ff",  # lightskyblue1
            'color': "#1E90FF",  # dodgerblue4
            'style': 'filled,rounded',
        },
    )

    # TODO:
    #  - Guarantee taxa will be unique (no duplicated short names), raise here?
    for taxon in prims:
        if not (taxa_key:=taxon.GetAssetInfoByKey(_ASSETINFO_TAXA_KEY)):
            raise ValueError(f"Prim {taxon} is not a taxon. Expected to find asset info in key '{_ASSETINFO_TAXA_KEY}' but found '{taxa_key}'. Complete prim's asset info: {taxon.GetAssetInfo()}")
        graph.add_node(taxon_name:=taxon.GetName(), tooltip=taxon.GetPath(), href=f"{url_id_prefix}{taxon_name}",)
        graph.add_edges_from(itertools.zip_longest(set(taxon.GetAssetInfoByKey(_ASSETINFO_TAXA_KEY)) - {taxon_name}, (), fillvalue=taxon_name))
    return graph


@taxonomy_graph.register(Usd.Stage)
def _(stage: Usd.Stage, url_id_prefix: str) -> nx.DiGraph:
    # Convenience for the stage
    return taxonomy_graph(itaxa(stage), url_id_prefix)


def filter_taxa(prims: abc.Iterable[Usd.Prim], taxon: Usd.Prim | str, *taxa: Usd.Prim) -> abc.Iterator[Usd.Prim]:
    """From the given prims, yield those that are part of the given taxa."""
    taxa_names = {i if isinstance(i, str) else i.GetName() for i in (taxon, *taxa)}
    return (prim for prim in prims if taxa_names.intersection(prim.GetAssetInfoByKey(_ASSETINFO_TAXA_KEY) or {}))
