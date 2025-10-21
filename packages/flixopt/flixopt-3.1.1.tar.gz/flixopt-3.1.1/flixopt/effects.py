"""
This module contains the effects of the flixopt framework.
Furthermore, it contains the EffectCollection, which is used to collect all effects of a system.
Different Datatypes are used to represent the effects with assigned values by the user,
which are then transformed into the internal data structure.
"""

from __future__ import annotations

import logging
import warnings
from collections import deque
from typing import TYPE_CHECKING, Literal

import linopy
import numpy as np
import xarray as xr

from .core import PeriodicDataUser, Scalar, TemporalData, TemporalDataUser
from .features import ShareAllocationModel
from .structure import Element, ElementModel, FlowSystemModel, Submodel, register_class_for_io

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .flow_system import FlowSystem

logger = logging.getLogger('flixopt')


@register_class_for_io
class Effect(Element):
    """
    Represents system-wide impacts like costs, emissions, resource consumption, or other effects.

    Effects capture the broader impacts of system operation and investment decisions beyond
    the primary energy/material flows. Each Effect accumulates contributions from Components,
    Flows, and other system elements. One Effect is typically chosen as the optimization
    objective, while others can serve as constraints or tracking metrics.

    Effects support comprehensive modeling including operational and investment contributions,
    cross-effect relationships (e.g., carbon pricing), and flexible constraint formulation.

    Args:
        label: The label of the Element. Used to identify it in the FlowSystem.
        unit: The unit of the effect (e.g., '€', 'kg_CO2', 'kWh_primary', 'm²').
            This is informative only and does not affect optimization calculations.
        description: Descriptive name explaining what this effect represents.
        is_standard: If True, this is a standard effect allowing direct value input
            without effect dictionaries. Used for simplified effect specification (and less boilerplate code).
        is_objective: If True, this effect serves as the optimization objective function.
            Only one effect can be marked as objective per optimization.
        share_from_temporal: Temporal cross-effect contributions.
            Maps temporal contributions from other effects to this effect
        share_from_periodic: Periodic cross-effect contributions.
            Maps periodic contributions from other effects to this effect.
        minimum_temporal: Minimum allowed total contribution across all timesteps.
        maximum_temporal: Maximum allowed total contribution across all timesteps.
        minimum_per_hour: Minimum allowed contribution per hour.
        maximum_per_hour: Maximum allowed contribution per hour.
        minimum_periodic: Minimum allowed total periodic contribution.
        maximum_periodic: Maximum allowed total periodic contribution.
        minimum_total: Minimum allowed total effect (temporal + periodic combined).
        maximum_total: Maximum allowed total effect (temporal + periodic combined).
        meta_data: Used to store additional information. Not used internally but saved
            in results. Only use Python native types.

    **Deprecated Parameters** (for backwards compatibility):
        minimum_operation: Use `minimum_temporal` instead.
        maximum_operation: Use `maximum_temporal` instead.
        minimum_invest: Use `minimum_periodic` instead.
        maximum_invest: Use `maximum_periodic` instead.
        minimum_operation_per_hour: Use `minimum_per_hour` instead.
        maximum_operation_per_hour: Use `maximum_per_hour` instead.

    Examples:
        Basic cost objective:

        ```python
        cost_effect = Effect(
            label='system_costs',
            unit='€',
            description='Total system costs',
            is_objective=True,
        )
        ```

        CO2 emissions:

        ```python
        co2_effect = Effect(
            label='CO2',
            unit='kg_CO2',
            description='Carbon dioxide emissions',
            maximum_total=1_000_000,  # 1000 t CO2 annual limit
        )
        ```

        Land use constraint:

        ```python
        land_use = Effect(
            label='land_usage',
            unit='m²',
            description='Land area requirement',
            maximum_total=50_000,  # Maximum 5 hectares available
        )
        ```

        Primary energy tracking:

        ```python
        primary_energy = Effect(
            label='primary_energy',
            unit='kWh_primary',
            description='Primary energy consumption',
        )
        ```

       Cost objective with carbon and primary energy pricing:

        ```python
        cost_effect = Effect(
            label='system_costs',
            unit='€',
            description='Total system costs',
            is_objective=True,
            share_from_temporal={
                'primary_energy': 0.08,  # 0.08 €/kWh_primary
                'CO2': 0.2,  # Carbon pricing: 0.2 €/kg_CO2 into costs if used on a cost effect
            },
        )
        ```

        Water consumption with tiered constraints:

        ```python
        water_usage = Effect(
            label='water_consumption',
            unit='m³',
            description='Industrial water usage',
            minimum_per_hour=10,  # Minimum 10 m³/h for process stability
            maximum_per_hour=500,  # Maximum 500 m³/h capacity limit
            maximum_total=100_000,  # Annual permit limit: 100,000 m³
        )
        ```

    Note:
        Effect bounds can be None to indicate no constraint in that direction.

        Cross-effect relationships enable sophisticated modeling like carbon pricing,
        resource valuation, or multi-criteria optimization with weighted objectives.

        The unit field is purely informational - ensure dimensional consistency
        across all contributions to each effect manually.

        Effects are accumulated as:
        - Total = Σ(temporal contributions) + Σ(periodic contributions)

    """

    def __init__(
        self,
        label: str,
        unit: str,
        description: str,
        meta_data: dict | None = None,
        is_standard: bool = False,
        is_objective: bool = False,
        share_from_temporal: TemporalEffectsUser | None = None,
        share_from_periodic: PeriodicEffectsUser | None = None,
        minimum_temporal: PeriodicEffectsUser | None = None,
        maximum_temporal: PeriodicEffectsUser | None = None,
        minimum_periodic: PeriodicEffectsUser | None = None,
        maximum_periodic: PeriodicEffectsUser | None = None,
        minimum_per_hour: TemporalDataUser | None = None,
        maximum_per_hour: TemporalDataUser | None = None,
        minimum_total: Scalar | None = None,
        maximum_total: Scalar | None = None,
        **kwargs,
    ):
        super().__init__(label, meta_data=meta_data)
        self.unit = unit
        self.description = description
        self.is_standard = is_standard
        self.is_objective = is_objective
        self.share_from_temporal: TemporalEffectsUser = share_from_temporal if share_from_temporal is not None else {}
        self.share_from_periodic: PeriodicEffectsUser = share_from_periodic if share_from_periodic is not None else {}

        # Handle backwards compatibility for deprecated parameters using centralized helper
        minimum_temporal = self._handle_deprecated_kwarg(
            kwargs, 'minimum_operation', 'minimum_temporal', minimum_temporal
        )
        maximum_temporal = self._handle_deprecated_kwarg(
            kwargs, 'maximum_operation', 'maximum_temporal', maximum_temporal
        )
        minimum_periodic = self._handle_deprecated_kwarg(kwargs, 'minimum_invest', 'minimum_periodic', minimum_periodic)
        maximum_periodic = self._handle_deprecated_kwarg(kwargs, 'maximum_invest', 'maximum_periodic', maximum_periodic)
        minimum_per_hour = self._handle_deprecated_kwarg(
            kwargs, 'minimum_operation_per_hour', 'minimum_per_hour', minimum_per_hour
        )
        maximum_per_hour = self._handle_deprecated_kwarg(
            kwargs, 'maximum_operation_per_hour', 'maximum_per_hour', maximum_per_hour
        )

        # Validate any remaining unexpected kwargs
        self._validate_kwargs(kwargs)

        # Set attributes directly
        self.minimum_temporal = minimum_temporal
        self.maximum_temporal = maximum_temporal
        self.minimum_periodic = minimum_periodic
        self.maximum_periodic = maximum_periodic
        self.minimum_per_hour = minimum_per_hour
        self.maximum_per_hour = maximum_per_hour
        self.minimum_total = minimum_total
        self.maximum_total = maximum_total

    # Backwards compatible properties (deprecated)
    @property
    def minimum_operation(self):
        """DEPRECATED: Use 'minimum_temporal' property instead."""
        warnings.warn(
            "Property 'minimum_operation' is deprecated. Use 'minimum_temporal' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.minimum_temporal

    @minimum_operation.setter
    def minimum_operation(self, value):
        """DEPRECATED: Use 'minimum_temporal' property instead."""
        warnings.warn(
            "Property 'minimum_operation' is deprecated. Use 'minimum_temporal' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.minimum_temporal = value

    @property
    def maximum_operation(self):
        """DEPRECATED: Use 'maximum_temporal' property instead."""
        warnings.warn(
            "Property 'maximum_operation' is deprecated. Use 'maximum_temporal' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.maximum_temporal

    @maximum_operation.setter
    def maximum_operation(self, value):
        """DEPRECATED: Use 'maximum_temporal' property instead."""
        warnings.warn(
            "Property 'maximum_operation' is deprecated. Use 'maximum_temporal' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.maximum_temporal = value

    @property
    def minimum_invest(self):
        """DEPRECATED: Use 'minimum_periodic' property instead."""
        warnings.warn(
            "Property 'minimum_invest' is deprecated. Use 'minimum_periodic' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.minimum_periodic

    @minimum_invest.setter
    def minimum_invest(self, value):
        """DEPRECATED: Use 'minimum_periodic' property instead."""
        warnings.warn(
            "Property 'minimum_invest' is deprecated. Use 'minimum_periodic' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.minimum_periodic = value

    @property
    def maximum_invest(self):
        """DEPRECATED: Use 'maximum_periodic' property instead."""
        warnings.warn(
            "Property 'maximum_invest' is deprecated. Use 'maximum_periodic' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.maximum_periodic

    @maximum_invest.setter
    def maximum_invest(self, value):
        """DEPRECATED: Use 'maximum_periodic' property instead."""
        warnings.warn(
            "Property 'maximum_invest' is deprecated. Use 'maximum_periodic' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.maximum_periodic = value

    @property
    def minimum_operation_per_hour(self):
        """DEPRECATED: Use 'minimum_per_hour' property instead."""
        warnings.warn(
            "Property 'minimum_operation_per_hour' is deprecated. Use 'minimum_per_hour' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.minimum_per_hour

    @minimum_operation_per_hour.setter
    def minimum_operation_per_hour(self, value):
        """DEPRECATED: Use 'minimum_per_hour' property instead."""
        warnings.warn(
            "Property 'minimum_operation_per_hour' is deprecated. Use 'minimum_per_hour' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.minimum_per_hour = value

    @property
    def maximum_operation_per_hour(self):
        """DEPRECATED: Use 'maximum_per_hour' property instead."""
        warnings.warn(
            "Property 'maximum_operation_per_hour' is deprecated. Use 'maximum_per_hour' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.maximum_per_hour

    @maximum_operation_per_hour.setter
    def maximum_operation_per_hour(self, value):
        """DEPRECATED: Use 'maximum_per_hour' property instead."""
        warnings.warn(
            "Property 'maximum_operation_per_hour' is deprecated. Use 'maximum_per_hour' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.maximum_per_hour = value

    def transform_data(self, flow_system: FlowSystem, name_prefix: str = '') -> None:
        prefix = '|'.join(filter(None, [name_prefix, self.label_full]))
        self.minimum_per_hour = flow_system.fit_to_model_coords(f'{prefix}|minimum_per_hour', self.minimum_per_hour)

        self.maximum_per_hour = flow_system.fit_to_model_coords(f'{prefix}|maximum_per_hour', self.maximum_per_hour)

        self.share_from_temporal = flow_system.fit_effects_to_model_coords(
            label_prefix=None,
            effect_values=self.share_from_temporal,
            label_suffix=f'(temporal)->{prefix}(temporal)',
            dims=['time', 'period', 'scenario'],
        )
        self.share_from_periodic = flow_system.fit_effects_to_model_coords(
            label_prefix=None,
            effect_values=self.share_from_periodic,
            label_suffix=f'(periodic)->{prefix}(periodic)',
            dims=['period', 'scenario'],
        )

        self.minimum_temporal = flow_system.fit_to_model_coords(
            f'{prefix}|minimum_temporal', self.minimum_temporal, dims=['period', 'scenario']
        )
        self.maximum_temporal = flow_system.fit_to_model_coords(
            f'{prefix}|maximum_temporal', self.maximum_temporal, dims=['period', 'scenario']
        )
        self.minimum_periodic = flow_system.fit_to_model_coords(
            f'{prefix}|minimum_periodic', self.minimum_periodic, dims=['period', 'scenario']
        )
        self.maximum_periodic = flow_system.fit_to_model_coords(
            f'{prefix}|maximum_periodic', self.maximum_periodic, dims=['period', 'scenario']
        )
        self.minimum_total = flow_system.fit_to_model_coords(
            f'{prefix}|minimum_total',
            self.minimum_total,
            dims=['period', 'scenario'],
        )
        self.maximum_total = flow_system.fit_to_model_coords(
            f'{prefix}|maximum_total', self.maximum_total, dims=['period', 'scenario']
        )

    def create_model(self, model: FlowSystemModel) -> EffectModel:
        self._plausibility_checks()
        self.submodel = EffectModel(model, self)
        return self.submodel

    def _plausibility_checks(self) -> None:
        # TODO: Check for plausibility
        pass


class EffectModel(ElementModel):
    element: Effect  # Type hint

    def __init__(self, model: FlowSystemModel, element: Effect):
        super().__init__(model, element)

    def _do_modeling(self):
        self.total: linopy.Variable | None = None
        self.periodic: ShareAllocationModel = self.add_submodels(
            ShareAllocationModel(
                model=self._model,
                dims=('period', 'scenario'),
                label_of_element=self.label_of_element,
                label_of_model=f'{self.label_of_model}(periodic)',
                total_max=self.element.maximum_periodic,
                total_min=self.element.minimum_periodic,
            ),
            short_name='periodic',
        )

        self.temporal: ShareAllocationModel = self.add_submodels(
            ShareAllocationModel(
                model=self._model,
                dims=('time', 'period', 'scenario'),
                label_of_element=self.label_of_element,
                label_of_model=f'{self.label_of_model}(temporal)',
                total_max=self.element.maximum_temporal,
                total_min=self.element.minimum_temporal,
                min_per_hour=self.element.minimum_per_hour if self.element.minimum_per_hour is not None else None,
                max_per_hour=self.element.maximum_per_hour if self.element.maximum_per_hour is not None else None,
            ),
            short_name='temporal',
        )

        self.total = self.add_variables(
            lower=self.element.minimum_total if self.element.minimum_total is not None else -np.inf,
            upper=self.element.maximum_total if self.element.maximum_total is not None else np.inf,
            coords=self._model.get_coords(['period', 'scenario']),
            name=self.label_full,
        )

        self.add_constraints(
            self.total == self.temporal.total + self.periodic.total, name=self.label_full, short_name='total'
        )


TemporalEffectsUser = TemporalDataUser | dict[str, TemporalDataUser]  # User-specified Shares to Effects
""" This datatype is used to define a temporal share to an effect by a certain attribute. """

PeriodicEffectsUser = PeriodicDataUser | dict[str, PeriodicDataUser]  # User-specified Shares to Effects
""" This datatype is used to define a scalar share to an effect by a certain attribute. """

TemporalEffects = dict[str, TemporalData]  # User-specified Shares to Effects
""" This datatype is used internally to handle temporal shares to an effect. """

PeriodicEffects = dict[str, Scalar]
""" This datatype is used internally to handle scalar shares to an effect. """

EffectExpr = dict[str, linopy.LinearExpression]  # Used to create Shares


class EffectCollection:
    """
    Handling all Effects
    """

    def __init__(self, *effects: Effect):
        self._effects = {}
        self._standard_effect: Effect | None = None
        self._objective_effect: Effect | None = None

        self.submodel: EffectCollectionModel | None = None
        self.add_effects(*effects)

    def create_model(self, model: FlowSystemModel) -> EffectCollectionModel:
        self._plausibility_checks()
        self.submodel = EffectCollectionModel(model, self)
        return self.submodel

    def add_effects(self, *effects: Effect) -> None:
        for effect in list(effects):
            if effect in self:
                raise ValueError(f'Effect with label "{effect.label=}" already added!')
            if effect.is_standard:
                self.standard_effect = effect
            if effect.is_objective:
                self.objective_effect = effect
            self._effects[effect.label] = effect
            logger.info(f'Registered new Effect: {effect.label}')

    def create_effect_values_dict(
        self, effect_values_user: PeriodicEffectsUser | TemporalEffectsUser
    ) -> dict[str, Scalar | TemporalDataUser] | None:
        """Converts effect values into a dictionary. If a scalar is provided, it is associated with a default effect type.

        Examples:
            ```python
            effect_values_user = 20                               -> {'<standard_effect_label>': 20}
            effect_values_user = {None: 20}                       -> {'<standard_effect_label>': 20}
            effect_values_user = None                             -> None
            effect_values_user = {'effect1': 20, 'effect2': 0.3}  -> {'effect1': 20, 'effect2': 0.3}
            ```

        Returns:
            A dictionary keyed by effect label, or None if input is None.
            Note: a standard effect must be defined when passing scalars or None labels.
        """

        def get_effect_label(eff: Effect | str) -> str:
            """Temporary function to get the label of an effect and warn for deprecation"""
            if isinstance(eff, Effect):
                warnings.warn(
                    f'The use of effect objects when specifying EffectValues is deprecated. '
                    f'Use the label of the effect instead. Used effect: {eff.label_full}',
                    UserWarning,
                    stacklevel=2,
                )
                return eff.label
            elif eff is None:
                return self.standard_effect.label
            else:
                return eff

        if effect_values_user is None:
            return None
        if isinstance(effect_values_user, dict):
            return {get_effect_label(effect): value for effect, value in effect_values_user.items()}
        return {self.standard_effect.label: effect_values_user}

    def _plausibility_checks(self) -> None:
        # Check circular loops in effects:
        temporal, periodic = self.calculate_effect_share_factors()

        # Validate all referenced sources exist
        unknown = {src for src, _ in list(temporal.keys()) + list(periodic.keys()) if src not in self.effects}
        if unknown:
            raise KeyError(f'Unknown effects used in in effect share mappings: {sorted(unknown)}')

        temporal_cycles = detect_cycles(tuples_to_adjacency_list([key for key in temporal]))
        periodic_cycles = detect_cycles(tuples_to_adjacency_list([key for key in periodic]))

        if temporal_cycles:
            cycle_str = '\n'.join([' -> '.join(cycle) for cycle in temporal_cycles])
            raise ValueError(f'Error: circular temporal-shares detected:\n{cycle_str}')

        if periodic_cycles:
            cycle_str = '\n'.join([' -> '.join(cycle) for cycle in periodic_cycles])
            raise ValueError(f'Error: circular periodic-shares detected:\n{cycle_str}')

    def __getitem__(self, effect: str | Effect | None) -> Effect:
        """
        Get an effect by label, or return the standard effect if None is passed

        Raises:
            KeyError: If no effect with the given label is found.
            KeyError: If no standard effect is specified.
        """
        if effect is None:
            return self.standard_effect
        if isinstance(effect, Effect):
            if effect in self:
                return effect
            else:
                raise KeyError(f'Effect {effect} not found!')
        try:
            return self.effects[effect]
        except KeyError as e:
            raise KeyError(f'Effect "{effect}" not found! Add it to the FlowSystem first!') from e

    def __iter__(self) -> Iterator[Effect]:
        return iter(self._effects.values())

    def __len__(self) -> int:
        return len(self._effects)

    def __contains__(self, item: str | Effect) -> bool:
        """Check if the effect exists. Checks for label or object"""
        if isinstance(item, str):
            return item in self.effects  # Check if the label exists
        elif isinstance(item, Effect):
            if item.label_full in self.effects:
                return True
            if item in self.effects.values():  # Check if the object exists
                return True
        return False

    @property
    def effects(self) -> dict[str, Effect]:
        return self._effects

    @property
    def standard_effect(self) -> Effect:
        if self._standard_effect is None:
            raise KeyError(
                'No standard-effect specified! Either set an effect through is_standard=True '
                'or pass a mapping when specifying effect values: {effect_label: value}.'
            )
        return self._standard_effect

    @standard_effect.setter
    def standard_effect(self, value: Effect) -> None:
        if self._standard_effect is not None:
            raise ValueError(f'A standard-effect already exists! ({self._standard_effect.label=})')
        self._standard_effect = value

    @property
    def objective_effect(self) -> Effect:
        if self._objective_effect is None:
            raise KeyError('No objective-effect specified!')
        return self._objective_effect

    @objective_effect.setter
    def objective_effect(self, value: Effect) -> None:
        if self._objective_effect is not None:
            raise ValueError(f'An objective-effect already exists! ({self._objective_effect.label=})')
        self._objective_effect = value

    def calculate_effect_share_factors(
        self,
    ) -> tuple[
        dict[tuple[str, str], xr.DataArray],
        dict[tuple[str, str], xr.DataArray],
    ]:
        shares_periodic = {}
        for name, effect in self.effects.items():
            if effect.share_from_periodic:
                for source, data in effect.share_from_periodic.items():
                    if source not in shares_periodic:
                        shares_periodic[source] = {}
                    shares_periodic[source][name] = data
        shares_periodic = calculate_all_conversion_paths(shares_periodic)

        shares_temporal = {}
        for name, effect in self.effects.items():
            if effect.share_from_temporal:
                for source, data in effect.share_from_temporal.items():
                    if source not in shares_temporal:
                        shares_temporal[source] = {}
                    shares_temporal[source][name] = data
        shares_temporal = calculate_all_conversion_paths(shares_temporal)

        return shares_temporal, shares_periodic


class EffectCollectionModel(Submodel):
    """
    Handling all Effects
    """

    def __init__(self, model: FlowSystemModel, effects: EffectCollection):
        self.effects = effects
        self.penalty: ShareAllocationModel | None = None
        super().__init__(model, label_of_element='Effects')

    def add_share_to_effects(
        self,
        name: str,
        expressions: EffectExpr,
        target: Literal['temporal', 'periodic'],
    ) -> None:
        for effect, expression in expressions.items():
            if target == 'temporal':
                self.effects[effect].submodel.temporal.add_share(
                    name,
                    expression,
                    dims=('time', 'period', 'scenario'),
                )
            elif target == 'periodic':
                self.effects[effect].submodel.periodic.add_share(
                    name,
                    expression,
                    dims=('period', 'scenario'),
                )
            else:
                raise ValueError(f'Target {target} not supported!')

    def add_share_to_penalty(self, name: str, expression: linopy.LinearExpression) -> None:
        if expression.ndim != 0:
            raise TypeError(f'Penalty shares must be scalar expressions! ({expression.ndim=})')
        self.penalty.add_share(name, expression, dims=())

    def _do_modeling(self):
        super()._do_modeling()
        for effect in self.effects:
            effect.create_model(self._model)
        self.penalty = self.add_submodels(
            ShareAllocationModel(self._model, dims=(), label_of_element='Penalty'),
            short_name='penalty',
        )

        self._add_share_between_effects()

        self._model.add_objective(
            (self.effects.objective_effect.submodel.total * self._model.weights).sum() + self.penalty.total.sum()
        )

    def _add_share_between_effects(self):
        for target_effect in self.effects:
            # 1. temporal: <- receiving temporal shares from other effects
            for source_effect, time_series in target_effect.share_from_temporal.items():
                target_effect.submodel.temporal.add_share(
                    self.effects[source_effect].submodel.temporal.label_full,
                    self.effects[source_effect].submodel.temporal.total_per_timestep * time_series,
                    dims=('time', 'period', 'scenario'),
                )
            # 2. periodic: <- receiving periodic shares from other effects
            for source_effect, factor in target_effect.share_from_periodic.items():
                target_effect.submodel.periodic.add_share(
                    self.effects[source_effect].submodel.periodic.label_full,
                    self.effects[source_effect].submodel.periodic.total * factor,
                    dims=('period', 'scenario'),
                )


def calculate_all_conversion_paths(
    conversion_dict: dict[str, dict[str, Scalar | xr.DataArray]],
) -> dict[tuple[str, str], xr.DataArray]:
    """
    Calculates all possible direct and indirect conversion factors between units/domains.
    This function uses Breadth-First Search (BFS) to find all possible conversion paths
    between different units or domains in a conversion graph. It computes both direct
    conversions (explicitly provided in the input) and indirect conversions (derived
    through intermediate units).
    Args:
        conversion_dict: A nested dictionary where:
            - Outer keys represent origin units/domains
            - Inner dictionaries map target units/domains to their conversion factors
            - Conversion factors can be integers, floats, or numpy arrays
    Returns:
        A dictionary mapping (origin, target) tuples to their respective conversion factors.
        Each key is a tuple of strings representing the origin and target units/domains.
        Each value is the conversion factor (int, float, or numpy array) from origin to target.
    """
    # Initialize the result dictionary to accumulate all paths
    result = {}

    # Add direct connections to the result first
    for origin, targets in conversion_dict.items():
        for target, factor in targets.items():
            result[(origin, target)] = factor

    # Track all paths by keeping path history to avoid cycles
    # Iterate over each domain in the dictionary
    for origin in conversion_dict:
        # Keep track of visited paths to avoid repeating calculations
        processed_paths = set()
        # Use a queue with (current_domain, factor, path_history)
        queue = deque([(origin, 1, [origin])])

        while queue:
            current_domain, factor, path = queue.popleft()

            # Skip if we've processed this exact path before
            path_key = tuple(path)
            if path_key in processed_paths:
                continue
            processed_paths.add(path_key)

            # Iterate over the neighbors of the current domain
            for target, conversion_factor in conversion_dict.get(current_domain, {}).items():
                # Skip if target would create a cycle
                if target in path:
                    continue

                # Calculate the indirect conversion factor
                indirect_factor = factor * conversion_factor
                new_path = path + [target]

                # Only consider paths starting at origin and ending at some target
                if len(new_path) > 2 and new_path[0] == origin:
                    # Update the result dictionary - accumulate factors from different paths
                    if (origin, target) in result:
                        result[(origin, target)] = result[(origin, target)] + indirect_factor
                    else:
                        result[(origin, target)] = indirect_factor

                # Add new path to queue for further exploration
                queue.append((target, indirect_factor, new_path))

    # Convert all values to DataArrays
    result = {key: value if isinstance(value, xr.DataArray) else xr.DataArray(value) for key, value in result.items()}

    return result


def detect_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """
    Detects cycles in a directed graph using DFS.

    Args:
        graph: Adjacency list representation of the graph

    Returns:
        List of cycles found, where each cycle is a list of nodes
    """
    # Track nodes in current recursion stack
    visiting = set()
    # Track nodes that have been fully explored
    visited = set()
    # Store all found cycles
    cycles = []

    def dfs_find_cycles(node, path=None):
        if path is None:
            path = []

        # Current path to this node
        current_path = path + [node]
        # Add node to current recursion stack
        visiting.add(node)

        # Check all neighbors
        for neighbor in graph.get(node, []):
            # If neighbor is in current path, we found a cycle
            if neighbor in visiting:
                # Get the cycle by extracting the relevant portion of the path
                cycle_start = current_path.index(neighbor)
                cycle = current_path[cycle_start:] + [neighbor]
                cycles.append(cycle)
            # If neighbor hasn't been fully explored, check it
            elif neighbor not in visited:
                dfs_find_cycles(neighbor, current_path)

        # Remove node from current path and mark as fully explored
        visiting.remove(node)
        visited.add(node)

    # Check each unvisited node
    for node in graph:
        if node not in visited:
            dfs_find_cycles(node)

    return cycles


def tuples_to_adjacency_list(edges: list[tuple[str, str]]) -> dict[str, list[str]]:
    """
    Converts a list of edge tuples (source, target) to an adjacency list representation.

    Args:
        edges: List of (source, target) tuples representing directed edges

    Returns:
        Dictionary mapping each source node to a list of its target nodes
    """
    graph = {}

    for source, target in edges:
        if source not in graph:
            graph[source] = []
        graph[source].append(target)

        # Ensure target nodes with no outgoing edges are in the graph
        if target not in graph:
            graph[target] = []

    return graph


# Backward compatibility aliases
NonTemporalEffectsUser = PeriodicEffectsUser
NonTemporalEffects = PeriodicEffects
