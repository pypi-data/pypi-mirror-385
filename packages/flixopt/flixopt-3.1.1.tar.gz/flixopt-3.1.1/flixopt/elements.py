"""
This module contains the basic elements of the flixopt framework.
"""

from __future__ import annotations

import logging
import warnings
from typing import TYPE_CHECKING

import numpy as np
import xarray as xr

from .config import CONFIG
from .core import PlausibilityError, Scalar, TemporalData, TemporalDataUser
from .features import InvestmentModel, OnOffModel
from .interface import InvestParameters, OnOffParameters
from .modeling import BoundingPatterns, ModelingPrimitives, ModelingUtilitiesAbstract
from .structure import Element, ElementModel, FlowSystemModel, register_class_for_io

if TYPE_CHECKING:
    import linopy

    from .effects import TemporalEffectsUser
    from .flow_system import FlowSystem

logger = logging.getLogger('flixopt')


@register_class_for_io
class Component(Element):
    """
    Base class for all system components that transform, convert, or process flows.

    Components are the active elements in energy systems that define how input and output
    Flows interact with each other. They represent equipment, processes, or logical
    operations that transform energy or materials between different states, carriers,
    or locations.

    Components serve as connection points between Buses through their associated Flows,
    enabling the modeling of complex energy system topologies and operational constraints.

    Args:
        label: The label of the Element. Used to identify it in the FlowSystem.
        inputs: list of input Flows feeding into the component. These represent
            energy/material consumption by the component.
        outputs: list of output Flows leaving the component. These represent
            energy/material production by the component.
        on_off_parameters: Defines binary operation constraints and costs when the
            component has discrete on/off states. Creates binary variables for all
            connected Flows. For better performance, prefer defining OnOffParameters
            on individual Flows when possible.
        prevent_simultaneous_flows: list of Flows that cannot be active simultaneously.
            Creates binary variables to enforce mutual exclusivity. Use sparingly as
            it increases computational complexity.
        meta_data: Used to store additional information. Not used internally but saved
            in results. Only use Python native types.

    Note:
        Component operational state is determined by its connected Flows:
        - Component is "on" if ANY of its Flows is active (flow_rate > 0)
        - Component is "off" only when ALL Flows are inactive (flow_rate = 0)

        Binary variables and constraints:
        - on_off_parameters creates binary variables for ALL connected Flows
        - prevent_simultaneous_flows creates binary variables for specified Flows
        - For better computational performance, prefer Flow-level OnOffParameters

        Component is an abstract base class. In practice, use specialized subclasses:
        - LinearConverter: Linear input/output relationships
        - Storage: Temporal energy/material storage
        - Transmission: Transport between locations
        - Source/Sink: System boundaries

    """

    def __init__(
        self,
        label: str,
        inputs: list[Flow] | None = None,
        outputs: list[Flow] | None = None,
        on_off_parameters: OnOffParameters | None = None,
        prevent_simultaneous_flows: list[Flow] | None = None,
        meta_data: dict | None = None,
    ):
        super().__init__(label, meta_data=meta_data)
        self.inputs: list[Flow] = inputs or []
        self.outputs: list[Flow] = outputs or []
        self._check_unique_flow_labels()
        self.on_off_parameters = on_off_parameters
        self.prevent_simultaneous_flows: list[Flow] = prevent_simultaneous_flows or []

        self.flows: dict[str, Flow] = {flow.label: flow for flow in self.inputs + self.outputs}

    def create_model(self, model: FlowSystemModel) -> ComponentModel:
        self._plausibility_checks()
        self.submodel = ComponentModel(model, self)
        return self.submodel

    def transform_data(self, flow_system: FlowSystem, name_prefix: str = '') -> None:
        prefix = '|'.join(filter(None, [name_prefix, self.label_full]))
        if self.on_off_parameters is not None:
            self.on_off_parameters.transform_data(flow_system, prefix)

        for flow in self.inputs + self.outputs:
            flow.transform_data(flow_system)  # Flow doesnt need the name_prefix

    def _check_unique_flow_labels(self):
        all_flow_labels = [flow.label for flow in self.inputs + self.outputs]

        if len(set(all_flow_labels)) != len(all_flow_labels):
            duplicates = {label for label in all_flow_labels if all_flow_labels.count(label) > 1}
            raise ValueError(f'Flow names must be unique! "{self.label_full}" got 2 or more of: {duplicates}')

    def _plausibility_checks(self) -> None:
        self._check_unique_flow_labels()


@register_class_for_io
class Bus(Element):
    """
    Buses represent nodal balances between flow rates, serving as connection points.

    A Bus enforces energy or material balance constraints where the sum of all incoming
    flows must equal the sum of all outgoing flows at each time step. Buses represent
    physical or logical connection points for energy carriers (electricity, heat, gas)
    or material flows between different Components.

    Mathematical Formulation:
        See the complete mathematical model in the documentation:
        [Bus](../user-guide/mathematical-notation/elements/Bus.md)

    Args:
        label: The label of the Element. Used to identify it in the FlowSystem.
        excess_penalty_per_flow_hour: Penalty costs for bus balance violations.
            When None, no excess/deficit is allowed (hard constraint). When set to a
            value > 0, allows bus imbalances at penalty cost. Default is 1e5 (high penalty).
        meta_data: Used to store additional information. Not used internally but saved
            in results. Only use Python native types.

    Examples:
        Electrical bus with strict balance:

        ```python
        electricity_bus = Bus(
            label='main_electrical_bus',
            excess_penalty_per_flow_hour=None,  # No imbalance allowed
        )
        ```

        Heat network with penalty for imbalances:

        ```python
        heat_network = Bus(
            label='district_heating_network',
            excess_penalty_per_flow_hour=1000,  # €1000/MWh penalty for imbalance
        )
        ```

        Material flow with time-varying penalties:

        ```python
        material_hub = Bus(
            label='material_processing_hub',
            excess_penalty_per_flow_hour=waste_disposal_costs,  # Time series
        )
        ```

    Note:
        The bus balance equation enforced is: Σ(inflows) = Σ(outflows) + excess - deficit

        When excess_penalty_per_flow_hour is None, excess and deficit are forced to zero.
        When a penalty cost is specified, the optimization can choose to violate the
        balance if economically beneficial, paying the penalty.
        The penalty is added to the objective directly.

        Empty `inputs` and `outputs` lists are initialized and populated automatically
        by the FlowSystem during system setup.
    """

    def __init__(
        self,
        label: str,
        excess_penalty_per_flow_hour: TemporalDataUser | None = 1e5,
        meta_data: dict | None = None,
    ):
        super().__init__(label, meta_data=meta_data)
        self.excess_penalty_per_flow_hour = excess_penalty_per_flow_hour
        self.inputs: list[Flow] = []
        self.outputs: list[Flow] = []

    def create_model(self, model: FlowSystemModel) -> BusModel:
        self._plausibility_checks()
        self.submodel = BusModel(model, self)
        return self.submodel

    def transform_data(self, flow_system: FlowSystem, name_prefix: str = '') -> None:
        prefix = '|'.join(filter(None, [name_prefix, self.label_full]))
        self.excess_penalty_per_flow_hour = flow_system.fit_to_model_coords(
            f'{prefix}|excess_penalty_per_flow_hour', self.excess_penalty_per_flow_hour
        )

    def _plausibility_checks(self) -> None:
        if self.excess_penalty_per_flow_hour is not None:
            zero_penalty = np.all(np.equal(self.excess_penalty_per_flow_hour, 0))
            if zero_penalty:
                logger.warning(
                    f'In Bus {self.label_full}, the excess_penalty_per_flow_hour is 0. Use "None" or a value > 0.'
                )
        if len(self.inputs) == 0 and len(self.outputs) == 0:
            raise ValueError(
                f'Bus "{self.label_full}" has no Flows connected to it. Please remove it from the FlowSystem'
            )

    @property
    def with_excess(self) -> bool:
        return False if self.excess_penalty_per_flow_hour is None else True


@register_class_for_io
class Connection:
    # input/output-dock (TODO:
    # -> wäre cool, damit Komponenten auch auch ohne Knoten verbindbar
    # input wären wie Flow,aber statt bus: connectsTo -> hier andere Connection oder aber Bus (dort keine Connection, weil nicht notwendig)

    def __init__(self):
        """
        This class is not yet implemented!
        """
        raise NotImplementedError()


@register_class_for_io
class Flow(Element):
    """Define a directed flow of energy or material between bus and component.

    A Flow represents the transfer of energy (electricity, heat, fuel) or material
    between a Bus and a Component in a specific direction. The flow rate is the
    primary optimization variable, with constraints and costs defined through
    various parameters. Flows can have fixed or variable sizes, operational
    constraints, and complex on/off behavior.

    Key Concepts:
        **Flow Rate**: The instantaneous rate of energy/material transfer (optimization variable) [kW, m³/h, kg/h]
        **Flow Hours**: Amount of energy/material transferred per timestep. [kWh, m³, kg]
        **Flow Size**: The maximum capacity or nominal rating of the flow [kW, m³/h, kg/h]
        **Relative Bounds**: Flow rate limits expressed as fractions of flow size

    Integration with Parameter Classes:
        - **InvestParameters**: Used for `size` when flow Size is an investment decision
        - **OnOffParameters**: Used for `on_off_parameters` when flow has discrete states

    Mathematical Formulation:
        See the complete mathematical model in the documentation:
        [Flow](../user-guide/mathematical-notation/elements/Flow.md)

    Args:
        label: Unique flow identifier within its component.
        bus: Bus label this flow connects to.
        size: Flow capacity. Scalar, InvestParameters, or None (uses CONFIG.Modeling.big).
        relative_minimum: Minimum flow rate as fraction of size (0-1). Default: 0.
        relative_maximum: Maximum flow rate as fraction of size. Default: 1.
        load_factor_min: Minimum average utilization (0-1). Default: 0.
        load_factor_max: Maximum average utilization (0-1). Default: 1.
        effects_per_flow_hour: Operational costs/impacts per flow-hour.
            Dict mapping effect names to values (e.g., {'cost': 45, 'CO2': 0.8}).
        on_off_parameters: Binary operation constraints (OnOffParameters). Default: None.
        flow_hours_total_max: Maximum cumulative flow-hours. Alternative to load_factor_max.
        flow_hours_total_min: Minimum cumulative flow-hours. Alternative to load_factor_min.
        fixed_relative_profile: Predetermined pattern as fraction of size.
            Flow rate = size × fixed_relative_profile(t).
        previous_flow_rate: Initial flow state for on/off dynamics. Default: None (off).
        meta_data: Additional info stored in results. Python native types only.

    Examples:
        Basic power flow with fixed capacity:

        ```python
        generator_output = Flow(
            label='electricity_out',
            bus='electricity_grid',
            size=100,  # 100 MW capacity
            relative_minimum=0.4,  # Cannot operate below 40 MW
            effects_per_flow_hour={'fuel_cost': 45, 'co2_emissions': 0.8},
        )
        ```

        Investment decision for battery capacity:

        ```python
        battery_flow = Flow(
            label='electricity_storage',
            bus='electricity_grid',
            size=InvestParameters(
                minimum_size=10,  # Minimum 10 MWh
                maximum_size=100,  # Maximum 100 MWh
                specific_effects={'cost': 150_000},  # €150k/MWh annualized
            ),
        )
        ```

        Heat pump with startup costs and minimum run times:

        ```python
        heat_pump = Flow(
            label='heat_output',
            bus='heating_network',
            size=50,  # 50 kW thermal
            relative_minimum=0.3,  # Minimum 15 kW output when on
            effects_per_flow_hour={'electricity_cost': 25, 'maintenance': 2},
            on_off_parameters=OnOffParameters(
                effects_per_switch_on={'startup_cost': 100, 'wear': 0.1},
                consecutive_on_hours_min=2,  # Must run at least 2 hours
                consecutive_off_hours_min=1,  # Must stay off at least 1 hour
                switch_on_total_max=200,  # Maximum 200 starts per period
            ),
        )
        ```

        Fixed renewable generation profile:

        ```python
        solar_generation = Flow(
            label='solar_power',
            bus='electricity_grid',
            size=25,  # 25 MW installed capacity
            fixed_relative_profile=np.array([0, 0.1, 0.4, 0.8, 0.9, 0.7, 0.3, 0.1, 0]),
            effects_per_flow_hour={'maintenance_costs': 5},  # €5/MWh maintenance
        )
        ```

        Industrial process with annual utilization limits:

        ```python
        production_line = Flow(
            label='product_output',
            bus='product_market',
            size=1000,  # 1000 units/hour capacity
            load_factor_min=0.6,  # Must achieve 60% annual utilization
            load_factor_max=0.85,  # Cannot exceed 85% for maintenance
            effects_per_flow_hour={'variable_cost': 12, 'quality_control': 0.5},
        )
        ```

    Design Considerations:
        **Size vs Load Factors**: Use `flow_hours_total_min/max` for absolute limits,
        `load_factor_min/max` for utilization-based constraints.

        **Relative Bounds**: Set `relative_minimum > 0` only when equipment cannot
        operate below that level. Use `on_off_parameters` for discrete on/off behavior.

        **Fixed Profiles**: Use `fixed_relative_profile` for known exact patterns,
        `relative_maximum` for upper bounds on optimization variables.

    Notes:
        - Default size (CONFIG.Modeling.big) is used when size=None
        - list inputs for previous_flow_rate are converted to NumPy arrays
        - Flow direction is determined by component input/output designation

    Deprecated:
        Passing Bus objects to `bus` parameter. Use bus label strings instead.

    """

    def __init__(
        self,
        label: str,
        bus: str,
        size: Scalar | InvestParameters = None,
        fixed_relative_profile: TemporalDataUser | None = None,
        relative_minimum: TemporalDataUser = 0,
        relative_maximum: TemporalDataUser = 1,
        effects_per_flow_hour: TemporalEffectsUser | None = None,
        on_off_parameters: OnOffParameters | None = None,
        flow_hours_total_max: Scalar | None = None,
        flow_hours_total_min: Scalar | None = None,
        load_factor_min: Scalar | None = None,
        load_factor_max: Scalar | None = None,
        previous_flow_rate: Scalar | list[Scalar] | None = None,
        meta_data: dict | None = None,
    ):
        super().__init__(label, meta_data=meta_data)
        self.size = CONFIG.Modeling.big if size is None else size
        self.relative_minimum = relative_minimum
        self.relative_maximum = relative_maximum
        self.fixed_relative_profile = fixed_relative_profile

        self.load_factor_min = load_factor_min
        self.load_factor_max = load_factor_max
        # self.positive_gradient = TimeSeries('positive_gradient', positive_gradient, self)
        self.effects_per_flow_hour = effects_per_flow_hour if effects_per_flow_hour is not None else {}
        self.flow_hours_total_max = flow_hours_total_max
        self.flow_hours_total_min = flow_hours_total_min
        self.on_off_parameters = on_off_parameters

        self.previous_flow_rate = previous_flow_rate

        self.component: str = 'UnknownComponent'
        self.is_input_in_component: bool | None = None
        if isinstance(bus, Bus):
            self.bus = bus.label_full
            warnings.warn(
                f'Bus {bus.label} is passed as a Bus object to {self.label}. This is deprecated and will be removed '
                f'in the future. Add the Bus to the FlowSystem instead and pass its label to the Flow.',
                UserWarning,
                stacklevel=1,
            )
            self._bus_object = bus
        else:
            self.bus = bus
            self._bus_object = None

    def create_model(self, model: FlowSystemModel) -> FlowModel:
        self._plausibility_checks()
        self.submodel = FlowModel(model, self)
        return self.submodel

    def transform_data(self, flow_system: FlowSystem, name_prefix: str = '') -> None:
        prefix = '|'.join(filter(None, [name_prefix, self.label_full]))
        self.relative_minimum = flow_system.fit_to_model_coords(f'{prefix}|relative_minimum', self.relative_minimum)
        self.relative_maximum = flow_system.fit_to_model_coords(f'{prefix}|relative_maximum', self.relative_maximum)
        self.fixed_relative_profile = flow_system.fit_to_model_coords(
            f'{prefix}|fixed_relative_profile', self.fixed_relative_profile
        )
        self.effects_per_flow_hour = flow_system.fit_effects_to_model_coords(
            prefix, self.effects_per_flow_hour, 'per_flow_hour'
        )
        self.flow_hours_total_max = flow_system.fit_to_model_coords(
            f'{prefix}|flow_hours_total_max', self.flow_hours_total_max, dims=['period', 'scenario']
        )
        self.flow_hours_total_min = flow_system.fit_to_model_coords(
            f'{prefix}|flow_hours_total_min', self.flow_hours_total_min, dims=['period', 'scenario']
        )
        self.load_factor_max = flow_system.fit_to_model_coords(
            f'{prefix}|load_factor_max', self.load_factor_max, dims=['period', 'scenario']
        )
        self.load_factor_min = flow_system.fit_to_model_coords(
            f'{prefix}|load_factor_min', self.load_factor_min, dims=['period', 'scenario']
        )

        if self.on_off_parameters is not None:
            self.on_off_parameters.transform_data(flow_system, prefix)
        if isinstance(self.size, InvestParameters):
            self.size.transform_data(flow_system, prefix)
        else:
            self.size = flow_system.fit_to_model_coords(f'{prefix}|size', self.size, dims=['period', 'scenario'])

    def _plausibility_checks(self) -> None:
        # TODO: Incorporate into Variable? (Lower_bound can not be greater than upper bound
        if (self.relative_minimum > self.relative_maximum).any():
            raise PlausibilityError(self.label_full + ': Take care, that relative_minimum <= relative_maximum!')

        if not isinstance(self.size, InvestParameters) and (
            np.any(self.size == CONFIG.Modeling.big) and self.fixed_relative_profile is not None
        ):  # Default Size --> Most likely by accident
            logger.warning(
                f'Flow "{self.label_full}" has no size assigned, but a "fixed_relative_profile". '
                f'The default size is {CONFIG.Modeling.big}. As "flow_rate = size * fixed_relative_profile", '
                f'the resulting flow_rate will be very high. To fix this, assign a size to the Flow {self}.'
            )

        if self.fixed_relative_profile is not None and self.on_off_parameters is not None:
            logger.warning(
                f'Flow {self.label_full} has both a fixed_relative_profile and an on_off_parameters.'
                f'This will allow the flow to be switched on and off, effectively differing from the fixed_flow_rate.'
            )

        if np.any(self.relative_minimum > 0) and self.on_off_parameters is None:
            logger.warning(
                f'Flow {self.label_full} has a relative_minimum of {self.relative_minimum} and no on_off_parameters. '
                f'This prevents the flow_rate from switching off (flow_rate = 0). '
                f'Consider using on_off_parameters to allow the flow to be switched on and off.'
            )

        if self.previous_flow_rate is not None:
            if not any(
                [
                    isinstance(self.previous_flow_rate, np.ndarray) and self.previous_flow_rate.ndim == 1,
                    isinstance(self.previous_flow_rate, (int, float, list)),
                ]
            ):
                raise TypeError(
                    f'previous_flow_rate must be None, a scalar, a list of scalars or a 1D-numpy-array. Got {type(self.previous_flow_rate)}. '
                    f'Different values in different periods or scenarios are not yet supported.'
                )

    @property
    def label_full(self) -> str:
        return f'{self.component}({self.label})'

    @property
    def size_is_fixed(self) -> bool:
        # Wenn kein InvestParameters existiert --> True; Wenn Investparameter, den Wert davon nehmen
        return False if (isinstance(self.size, InvestParameters) and self.size.fixed_size is None) else True


class FlowModel(ElementModel):
    element: Flow  # Type hint

    def __init__(self, model: FlowSystemModel, element: Flow):
        super().__init__(model, element)

    def _do_modeling(self):
        super()._do_modeling()
        # Main flow rate variable
        self.add_variables(
            lower=self.absolute_flow_rate_bounds[0],
            upper=self.absolute_flow_rate_bounds[1],
            coords=self._model.get_coords(),
            short_name='flow_rate',
        )

        self._constraint_flow_rate()

        # Total flow hours tracking
        ModelingPrimitives.expression_tracking_variable(
            model=self,
            name=f'{self.label_full}|total_flow_hours',
            tracked_expression=(self.flow_rate * self._model.hours_per_step).sum('time'),
            bounds=(
                self.element.flow_hours_total_min if self.element.flow_hours_total_min is not None else 0,
                self.element.flow_hours_total_max if self.element.flow_hours_total_max is not None else None,
            ),
            coords=['period', 'scenario'],
            short_name='total_flow_hours',
        )

        # Load factor constraints
        self._create_bounds_for_load_factor()

        # Effects
        self._create_shares()

    def _create_on_off_model(self):
        on = self.add_variables(binary=True, short_name='on', coords=self._model.get_coords())
        self.add_submodels(
            OnOffModel(
                model=self._model,
                label_of_element=self.label_of_element,
                parameters=self.element.on_off_parameters,
                on_variable=on,
                previous_states=self.previous_states,
                label_of_model=self.label_of_element,
            ),
            short_name='on_off',
        )

    def _create_investment_model(self):
        self.add_submodels(
            InvestmentModel(
                model=self._model,
                label_of_element=self.label_of_element,
                parameters=self.element.size,
                label_of_model=self.label_of_element,
            ),
            'investment',
        )

    def _constraint_flow_rate(self):
        if not self.with_investment and not self.with_on_off:
            # Most basic case. Already covered by direct variable bounds
            pass

        elif self.with_on_off and not self.with_investment:
            # OnOff, but no Investment
            self._create_on_off_model()
            bounds = self.relative_flow_rate_bounds
            BoundingPatterns.bounds_with_state(
                self,
                variable=self.flow_rate,
                bounds=(bounds[0] * self.element.size, bounds[1] * self.element.size),
                variable_state=self.on_off.on,
            )

        elif self.with_investment and not self.with_on_off:
            # Investment, but no OnOff
            self._create_investment_model()
            BoundingPatterns.scaled_bounds(
                self,
                variable=self.flow_rate,
                scaling_variable=self.investment.size,
                relative_bounds=self.relative_flow_rate_bounds,
            )

        elif self.with_investment and self.with_on_off:
            # Investment and OnOff
            self._create_investment_model()
            self._create_on_off_model()

            BoundingPatterns.scaled_bounds_with_state(
                model=self,
                variable=self.flow_rate,
                scaling_variable=self._investment.size,
                relative_bounds=self.relative_flow_rate_bounds,
                scaling_bounds=(self.element.size.minimum_or_fixed_size, self.element.size.maximum_or_fixed_size),
                variable_state=self.on_off.on,
            )
        else:
            raise Exception('Not valid')

    @property
    def with_on_off(self) -> bool:
        return self.element.on_off_parameters is not None

    @property
    def with_investment(self) -> bool:
        return isinstance(self.element.size, InvestParameters)

    # Properties for clean access to variables
    @property
    def flow_rate(self) -> linopy.Variable:
        """Main flow rate variable"""
        return self['flow_rate']

    @property
    def total_flow_hours(self) -> linopy.Variable:
        """Total flow hours variable"""
        return self['total_flow_hours']

    def results_structure(self):
        return {
            **super().results_structure(),
            'start': self.element.bus if self.element.is_input_in_component else self.element.component,
            'end': self.element.component if self.element.is_input_in_component else self.element.bus,
            'component': self.element.component,
        }

    def _create_shares(self):
        # Effects per flow hour
        if self.element.effects_per_flow_hour:
            self._model.effects.add_share_to_effects(
                name=self.label_full,
                expressions={
                    effect: self.flow_rate * self._model.hours_per_step * factor
                    for effect, factor in self.element.effects_per_flow_hour.items()
                },
                target='temporal',
            )

    def _create_bounds_for_load_factor(self):
        """Create load factor constraints using current approach"""
        # Get the size (either from element or investment)
        size = self.investment.size if self.with_investment else self.element.size

        # Maximum load factor constraint
        if self.element.load_factor_max is not None:
            flow_hours_per_size_max = self._model.hours_per_step.sum('time') * self.element.load_factor_max
            self.add_constraints(
                self.total_flow_hours <= size * flow_hours_per_size_max,
                short_name='load_factor_max',
            )

        # Minimum load factor constraint
        if self.element.load_factor_min is not None:
            flow_hours_per_size_min = self._model.hours_per_step.sum('time') * self.element.load_factor_min
            self.add_constraints(
                self.total_flow_hours >= size * flow_hours_per_size_min,
                short_name='load_factor_min',
            )

    @property
    def relative_flow_rate_bounds(self) -> tuple[TemporalData, TemporalData]:
        if self.element.fixed_relative_profile is not None:
            return self.element.fixed_relative_profile, self.element.fixed_relative_profile
        return self.element.relative_minimum, self.element.relative_maximum

    @property
    def absolute_flow_rate_bounds(self) -> tuple[TemporalData, TemporalData]:
        """
        Returns the absolute bounds the flow_rate can reach.
        Further constraining might be needed
        """
        lb_relative, ub_relative = self.relative_flow_rate_bounds

        lb = 0
        if not self.with_on_off:
            if not self.with_investment:
                # Basic case without investment and without OnOff
                lb = lb_relative * self.element.size
            elif self.with_investment and self.element.size.mandatory:
                # With mandatory Investment
                lb = lb_relative * self.element.size.minimum_or_fixed_size

        if self.with_investment:
            ub = ub_relative * self.element.size.maximum_or_fixed_size
        else:
            ub = ub_relative * self.element.size

        return lb, ub

    @property
    def on_off(self) -> OnOffModel | None:
        """OnOff feature"""
        if 'on_off' not in self.submodels:
            return None
        return self.submodels['on_off']

    @property
    def _investment(self) -> InvestmentModel | None:
        """Deprecated alias for investment"""
        return self.investment

    @property
    def investment(self) -> InvestmentModel | None:
        """OnOff feature"""
        if 'investment' not in self.submodels:
            return None
        return self.submodels['investment']

    @property
    def previous_states(self) -> TemporalData | None:
        """Previous states of the flow rate"""
        # TODO: This would be nicer to handle in the Flow itself, and allow DataArrays as well.
        previous_flow_rate = self.element.previous_flow_rate
        if previous_flow_rate is None:
            return None

        return ModelingUtilitiesAbstract.to_binary(
            values=xr.DataArray(
                [previous_flow_rate] if np.isscalar(previous_flow_rate) else previous_flow_rate, dims='time'
            ),
            epsilon=CONFIG.Modeling.epsilon,
            dims='time',
        )


class BusModel(ElementModel):
    element: Bus  # Type hint

    def __init__(self, model: FlowSystemModel, element: Bus):
        self.excess_input: linopy.Variable | None = None
        self.excess_output: linopy.Variable | None = None
        super().__init__(model, element)

    def _do_modeling(self) -> None:
        super()._do_modeling()
        # inputs == outputs
        for flow in self.element.inputs + self.element.outputs:
            self.register_variable(flow.submodel.flow_rate, flow.label_full)
        inputs = sum([flow.submodel.flow_rate for flow in self.element.inputs])
        outputs = sum([flow.submodel.flow_rate for flow in self.element.outputs])
        eq_bus_balance = self.add_constraints(inputs == outputs, short_name='balance')

        # Fehlerplus/-minus:
        if self.element.with_excess:
            excess_penalty = np.multiply(self._model.hours_per_step, self.element.excess_penalty_per_flow_hour)

            self.excess_input = self.add_variables(lower=0, coords=self._model.get_coords(), short_name='excess_input')

            self.excess_output = self.add_variables(
                lower=0, coords=self._model.get_coords(), short_name='excess_output'
            )

            eq_bus_balance.lhs -= -self.excess_input + self.excess_output

            self._model.effects.add_share_to_penalty(self.label_of_element, (self.excess_input * excess_penalty).sum())
            self._model.effects.add_share_to_penalty(self.label_of_element, (self.excess_output * excess_penalty).sum())

    def results_structure(self):
        inputs = [flow.submodel.flow_rate.name for flow in self.element.inputs]
        outputs = [flow.submodel.flow_rate.name for flow in self.element.outputs]
        if self.excess_input is not None:
            inputs.append(self.excess_input.name)
        if self.excess_output is not None:
            outputs.append(self.excess_output.name)
        return {
            **super().results_structure(),
            'inputs': inputs,
            'outputs': outputs,
            'flows': [flow.label_full for flow in self.element.inputs + self.element.outputs],
        }


class ComponentModel(ElementModel):
    element: Component  # Type hint

    def __init__(self, model: FlowSystemModel, element: Component):
        self.on_off: OnOffModel | None = None
        super().__init__(model, element)

    def _do_modeling(self):
        """Initiates all FlowModels"""
        super()._do_modeling()
        all_flows = self.element.inputs + self.element.outputs
        if self.element.on_off_parameters:
            for flow in all_flows:
                if flow.on_off_parameters is None:
                    flow.on_off_parameters = OnOffParameters()

        if self.element.prevent_simultaneous_flows:
            for flow in self.element.prevent_simultaneous_flows:
                if flow.on_off_parameters is None:
                    flow.on_off_parameters = OnOffParameters()

        for flow in all_flows:
            self.add_submodels(flow.create_model(self._model), short_name=flow.label)

        if self.element.on_off_parameters:
            on = self.add_variables(binary=True, short_name='on', coords=self._model.get_coords())
            if len(all_flows) == 1:
                self.add_constraints(on == all_flows[0].submodel.on_off.on, short_name='on')
            else:
                flow_ons = [flow.submodel.on_off.on for flow in all_flows]
                # TODO: Is the EPSILON even necessary?
                self.add_constraints(on <= sum(flow_ons) + CONFIG.Modeling.epsilon, short_name='on|ub')
                self.add_constraints(
                    on >= sum(flow_ons) / (len(flow_ons) + CONFIG.Modeling.epsilon), short_name='on|lb'
                )

            self.on_off = self.add_submodels(
                OnOffModel(
                    model=self._model,
                    label_of_element=self.label_of_element,
                    parameters=self.element.on_off_parameters,
                    on_variable=on,
                    label_of_model=self.label_of_element,
                    previous_states=self.previous_states,
                ),
                short_name='on_off',
            )

        if self.element.prevent_simultaneous_flows:
            # Simultanious Useage --> Only One FLow is On at a time, but needs a Binary for every flow
            ModelingPrimitives.mutual_exclusivity_constraint(
                self,
                binary_variables=[flow.submodel.on_off.on for flow in self.element.prevent_simultaneous_flows],
                short_name='prevent_simultaneous_use',
            )

    def results_structure(self):
        return {
            **super().results_structure(),
            'inputs': [flow.submodel.flow_rate.name for flow in self.element.inputs],
            'outputs': [flow.submodel.flow_rate.name for flow in self.element.outputs],
            'flows': [flow.label_full for flow in self.element.inputs + self.element.outputs],
        }

    @property
    def previous_states(self) -> xr.DataArray | None:
        """Previous state of the component, derived from its flows"""
        if self.element.on_off_parameters is None:
            raise ValueError(f'OnOffModel not present in \n{self}\nCant access previous_states')

        previous_states = [flow.submodel.on_off._previous_states for flow in self.element.inputs + self.element.outputs]
        previous_states = [da for da in previous_states if da is not None]

        if not previous_states:  # Empty list
            return None

        max_len = max(da.sizes['time'] for da in previous_states)

        padded_previous_states = [
            da.assign_coords(time=range(-da.sizes['time'], 0)).reindex(time=range(-max_len, 0), fill_value=0)
            for da in previous_states
        ]
        return xr.concat(padded_previous_states, dim='flow').any(dim='flow').astype(int)
