"""
This module contains the Calculation functionality for the flixopt framework.
It is used to calculate a FlowSystemModel for a given FlowSystem through a solver.
There are three different Calculation types:
    1. FullCalculation: Calculates the FlowSystemModel for the full FlowSystem
    2. AggregatedCalculation: Calculates the FlowSystemModel for the full FlowSystem, but aggregates the TimeSeriesData.
        This simplifies the mathematical model and usually speeds up the solving process.
    3. SegmentedCalculation: Solves a FlowSystemModel for each individual Segment of the FlowSystem.
"""

from __future__ import annotations

import logging
import math
import pathlib
import timeit
import warnings
from collections import Counter
from typing import TYPE_CHECKING, Annotated, Any

import numpy as np
import yaml

from . import io as fx_io
from . import utils as utils
from .aggregation import Aggregation, AggregationModel, AggregationParameters
from .components import Storage
from .config import CONFIG
from .core import DataConverter, Scalar, TimeSeriesData, drop_constant_arrays
from .features import InvestmentModel
from .flow_system import FlowSystem
from .results import CalculationResults, SegmentedCalculationResults

if TYPE_CHECKING:
    import pandas as pd
    import xarray as xr

    from .elements import Component
    from .solvers import _Solver
    from .structure import FlowSystemModel

logger = logging.getLogger('flixopt')


class Calculation:
    """
    class for defined way of solving a flow_system optimization

    Args:
        name: name of calculation
        flow_system: flow_system which should be calculated
        folder: folder where results should be saved. If None, then the current working directory is used.
        normalize_weights: Whether to automatically normalize the weights (periods and scenarios) to sum up to 1 when solving.
        active_timesteps: Deprecated. Use FlowSystem.sel(time=...) or FlowSystem.isel(time=...) instead.
    """

    def __init__(
        self,
        name: str,
        flow_system: FlowSystem,
        active_timesteps: Annotated[
            pd.DatetimeIndex | None,
            'DEPRECATED: Use flow_system.sel(time=...) or flow_system.isel(time=...) instead',
        ] = None,
        folder: pathlib.Path | None = None,
        normalize_weights: bool = True,
    ):
        self.name = name
        if flow_system.used_in_calculation:
            logger.warning(
                f'This FlowSystem is already used in a calculation:\n{flow_system}\n'
                f'Creating a copy of the FlowSystem for Calculation "{self.name}".'
            )
            flow_system = flow_system.copy()

        if active_timesteps is not None:
            warnings.warn(
                "The 'active_timesteps' parameter is deprecated and will be removed in a future version. "
                'Use flow_system.sel(time=timesteps) or flow_system.isel(time=indices) before passing '
                'the FlowSystem to the Calculation instead.',
                DeprecationWarning,
                stacklevel=2,
            )
            flow_system = flow_system.sel(time=active_timesteps)
        self._active_timesteps = active_timesteps  # deprecated
        self.normalize_weights = normalize_weights

        flow_system._used_in_calculation = True

        self.flow_system = flow_system
        self.model: FlowSystemModel | None = None

        self.durations = {'modeling': 0.0, 'solving': 0.0, 'saving': 0.0}
        self.folder = pathlib.Path.cwd() / 'results' if folder is None else pathlib.Path(folder)
        self.results: CalculationResults | None = None

        if self.folder.exists() and not self.folder.is_dir():
            raise NotADirectoryError(f'Path {self.folder} exists and is not a directory.')
        self.folder.mkdir(parents=False, exist_ok=True)

        self._modeled = False

    @property
    def main_results(self) -> dict[str, Scalar | dict]:
        from flixopt.features import InvestmentModel

        main_results = {
            'Objective': self.model.objective.value,
            'Penalty': self.model.effects.penalty.total.solution.values,
            'Effects': {
                f'{effect.label} [{effect.unit}]': {
                    'temporal': effect.submodel.temporal.total.solution.values,
                    'periodic': effect.submodel.periodic.total.solution.values,
                    'total': effect.submodel.total.solution.values,
                }
                for effect in self.flow_system.effects
            },
            'Invest-Decisions': {
                'Invested': {
                    model.label_of_element: model.size.solution
                    for component in self.flow_system.components.values()
                    for model in component.submodel.all_submodels
                    if isinstance(model, InvestmentModel) and model.size.solution.max() >= CONFIG.Modeling.epsilon
                },
                'Not invested': {
                    model.label_of_element: model.size.solution
                    for component in self.flow_system.components.values()
                    for model in component.submodel.all_submodels
                    if isinstance(model, InvestmentModel) and model.size.solution.max() < CONFIG.Modeling.epsilon
                },
            },
            'Buses with excess': [
                {
                    bus.label_full: {
                        'input': bus.submodel.excess_input.solution.sum('time'),
                        'output': bus.submodel.excess_output.solution.sum('time'),
                    }
                }
                for bus in self.flow_system.buses.values()
                if bus.with_excess
                and (
                    bus.submodel.excess_input.solution.sum() > 1e-3 or bus.submodel.excess_output.solution.sum() > 1e-3
                )
            ],
        }

        return utils.round_nested_floats(main_results)

    @property
    def summary(self):
        return {
            'Name': self.name,
            'Number of timesteps': len(self.flow_system.timesteps),
            'Calculation Type': self.__class__.__name__,
            'Constraints': self.model.constraints.ncons,
            'Variables': self.model.variables.nvars,
            'Main Results': self.main_results,
            'Durations': self.durations,
            'Config': CONFIG.to_dict(),
        }

    @property
    def active_timesteps(self) -> pd.DatetimeIndex:
        warnings.warn(
            'active_timesteps is deprecated. Use flow_system.sel(time=...) or flow_system.isel(time=...) instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        return self._active_timesteps

    @property
    def modeled(self) -> bool:
        return True if self.model is not None else False


class FullCalculation(Calculation):
    """
    FullCalculation solves the complete optimization problem using all time steps.

    This is the most comprehensive calculation type that considers every time step
    in the optimization, providing the most accurate but computationally intensive solution.

    Args:
        name: name of calculation
        flow_system: flow_system which should be calculated
        folder: folder where results should be saved. If None, then the current working directory is used.
        normalize_weights: Whether to automatically normalize the weights (periods and scenarios) to sum up to 1 when solving.
        active_timesteps: Deprecated. Use FlowSystem.sel(time=...) or FlowSystem.isel(time=...) instead.
    """

    def do_modeling(self) -> FullCalculation:
        t_start = timeit.default_timer()
        self.flow_system.connect_and_transform()

        self.model = self.flow_system.create_model(self.normalize_weights)
        self.model.do_modeling()

        self.durations['modeling'] = round(timeit.default_timer() - t_start, 2)
        return self

    def fix_sizes(self, ds: xr.Dataset, decimal_rounding: int | None = 5) -> FullCalculation:
        """Fix the sizes of the calculations to specified values.

        Args:
            ds: The dataset that contains the variable names mapped to their sizes. If None, the dataset is loaded from the results.
            decimal_rounding: The number of decimal places to round the sizes to. If no rounding is applied, numerical errors might lead to infeasibility.
        """
        if not self.modeled:
            raise RuntimeError('Model was not created. Call do_modeling() first.')
        if decimal_rounding is not None:
            ds = ds.round(decimal_rounding)

        for name, da in ds.data_vars.items():
            if '|size' not in name:
                continue
            if name not in self.model.variables:
                logger.debug(f'Variable {name} not found in calculation model. Skipping.')
                continue

            con = self.model.add_constraints(
                self.model[name] == da,
                name=f'{name}-fixed',
            )
            logger.debug(f'Fixed "{name}":\n{con}')

        return self

    def solve(
        self, solver: _Solver, log_file: pathlib.Path | None = None, log_main_results: bool = True
    ) -> FullCalculation:
        t_start = timeit.default_timer()

        self.model.solve(
            log_fn=pathlib.Path(log_file) if log_file is not None else self.folder / f'{self.name}.log',
            solver_name=solver.name,
            **solver.options,
        )
        self.durations['solving'] = round(timeit.default_timer() - t_start, 2)

        if self.model.status == 'warning':
            # Save the model and the flow_system to file in case of infeasibility
            paths = fx_io.CalculationResultsPaths(self.folder, self.name)
            from .io import document_linopy_model

            document_linopy_model(self.model, paths.model_documentation)
            self.flow_system.to_netcdf(paths.flow_system)
            raise RuntimeError(
                f'Model was infeasible. Please check {paths.model_documentation=} and {paths.flow_system=} for more information.'
            )

        # Log the formatted output
        if log_main_results:
            logger.info(
                f'{" Main Results ":#^80}\n'
                + yaml.dump(
                    utils.round_nested_floats(self.main_results),
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                    indent=4,
                )
            )

        self.results = CalculationResults.from_calculation(self)

        return self


class AggregatedCalculation(FullCalculation):
    """
    AggregatedCalculation reduces computational complexity by clustering time series into typical periods.

    This calculation approach aggregates time series data using clustering techniques (tsam) to identify
    representative time periods, significantly reducing computation time while maintaining solution accuracy.

    Note:
        The quality of the solution depends on the choice of aggregation parameters.
        The optimal parameters depend on the specific problem and the characteristics of the time series data.
        For more information, refer to the [tsam documentation](https://tsam.readthedocs.io/en/latest/).

    Args:
        name: Name of the calculation
        flow_system: FlowSystem to be optimized
        aggregation_parameters: Parameters for aggregation. See AggregationParameters class documentation
        components_to_clusterize: list of Components to perform aggregation on. If None, all components are aggregated.
            This equalizes variables in the components according to the typical periods computed in the aggregation
        active_timesteps: DatetimeIndex of timesteps to use for calculation. If None, all timesteps are used
        folder: Folder where results should be saved. If None, current working directory is used

    Attributes:
        aggregation (Aggregation | None): Contains the clustered time series data
        aggregation_model (AggregationModel | None): Contains Variables and Constraints that equalize clusters of the time series data
    """

    def __init__(
        self,
        name: str,
        flow_system: FlowSystem,
        aggregation_parameters: AggregationParameters,
        components_to_clusterize: list[Component] | None = None,
        active_timesteps: Annotated[
            pd.DatetimeIndex | None,
            'DEPRECATED: Use flow_system.sel(time=...) or flow_system.isel(time=...) instead',
        ] = None,
        folder: pathlib.Path | None = None,
    ):
        if flow_system.scenarios is not None:
            raise ValueError('Aggregation is not supported for scenarios yet. Please use FullCalculation instead.')
        super().__init__(name, flow_system, active_timesteps, folder=folder)
        self.aggregation_parameters = aggregation_parameters
        self.components_to_clusterize = components_to_clusterize
        self.aggregation: Aggregation | None = None
        self.aggregation_model: AggregationModel | None = None

    def do_modeling(self) -> AggregatedCalculation:
        t_start = timeit.default_timer()
        self.flow_system.connect_and_transform()
        self._perform_aggregation()

        # Model the System
        self.model = self.flow_system.create_model(self.normalize_weights)
        self.model.do_modeling()
        # Add Aggregation Submodel after modeling the rest
        self.aggregation_model = AggregationModel(
            self.model, self.aggregation_parameters, self.flow_system, self.aggregation, self.components_to_clusterize
        )
        self.aggregation_model.do_modeling()
        self.durations['modeling'] = round(timeit.default_timer() - t_start, 2)
        return self

    def _perform_aggregation(self):
        from .aggregation import Aggregation

        t_start_agg = timeit.default_timer()

        # Validation
        dt_min = float(self.flow_system.hours_per_timestep.min().item())
        dt_max = float(self.flow_system.hours_per_timestep.max().item())
        if not dt_min == dt_max:
            raise ValueError(
                f'Aggregation failed due to inconsistent time step sizes:'
                f'delta_t varies from {dt_min} to {dt_max} hours.'
            )
        ratio = self.aggregation_parameters.hours_per_period / dt_max
        if not np.isclose(ratio, round(ratio), atol=1e-9):
            raise ValueError(
                f'The selected {self.aggregation_parameters.hours_per_period=} does not match the time '
                f'step size of {dt_max} hours. It must be an integer multiple of {dt_max} hours.'
            )

        logger.info(f'{"":#^80}')
        logger.info(f'{" Aggregating TimeSeries Data ":#^80}')

        ds = self.flow_system.to_dataset()

        temporaly_changing_ds = drop_constant_arrays(ds, dim='time')

        # Aggregation - creation of aggregated timeseries:
        self.aggregation = Aggregation(
            original_data=temporaly_changing_ds.to_dataframe(),
            hours_per_time_step=float(dt_min),
            hours_per_period=self.aggregation_parameters.hours_per_period,
            nr_of_periods=self.aggregation_parameters.nr_of_periods,
            weights=self.calculate_aggregation_weights(temporaly_changing_ds),
            time_series_for_high_peaks=self.aggregation_parameters.labels_for_high_peaks,
            time_series_for_low_peaks=self.aggregation_parameters.labels_for_low_peaks,
        )

        self.aggregation.cluster()
        self.aggregation.plot(show=True, save=self.folder / 'aggregation.html')
        if self.aggregation_parameters.aggregate_data_and_fix_non_binary_vars:
            ds = self.flow_system.to_dataset()
            for name, series in self.aggregation.aggregated_data.items():
                da = (
                    DataConverter.to_dataarray(series, self.flow_system.coords)
                    .rename(name)
                    .assign_attrs(ds[name].attrs)
                )
                if TimeSeriesData.is_timeseries_data(da):
                    da = TimeSeriesData.from_dataarray(da)

                ds[name] = da

            self.flow_system = FlowSystem.from_dataset(ds)
        self.flow_system.connect_and_transform()
        self.durations['aggregation'] = round(timeit.default_timer() - t_start_agg, 2)

    @classmethod
    def calculate_aggregation_weights(cls, ds: xr.Dataset) -> dict[str, float]:
        """Calculate weights for all datavars in the dataset. Weights are pulled from the attrs of the datavars."""

        groups = [da.attrs['aggregation_group'] for da in ds.data_vars.values() if 'aggregation_group' in da.attrs]
        group_counts = Counter(groups)

        # Calculate weight for each group (1/count)
        group_weights = {group: 1 / count for group, count in group_counts.items()}

        weights = {}
        for name, da in ds.data_vars.items():
            group_weight = group_weights.get(da.attrs.get('aggregation_group'))
            if group_weight is not None:
                weights[name] = group_weight
            else:
                weights[name] = da.attrs.get('aggregation_weight', 1)

        if np.all(np.isclose(list(weights.values()), 1, atol=1e-6)):
            logger.info('All Aggregation weights were set to 1')

        return weights


class SegmentedCalculation(Calculation):
    """Solve large optimization problems by dividing time horizon into (overlapping) segments.

    This class addresses memory and computational limitations of large-scale optimization
    problems by decomposing the time horizon into smaller overlapping segments that are
    solved sequentially. Each segment uses final values from the previous segment as
    initial conditions, ensuring dynamic continuity across the solution.

    Key Concepts:
        **Temporal Decomposition**: Divides long time horizons into manageable segments
        **Overlapping Windows**: Segments share timesteps to improve storage dynamics
        **Value Transfer**: Final states of one segment become initial states of the next
        **Sequential Solving**: Each segment solved independently but with coupling

    Limitations and Constraints:
        **Investment Parameters**: InvestParameters are not supported in segmented calculations
        as investment decisions must be made for the entire time horizon, not per segment.

        **Global Constraints**: Time-horizon-wide constraints (flow_hours_total_min/max,
        load_factor_min/max) may produce suboptimal results as they cannot be enforced
        globally across segments.

        **Storage Dynamics**: While overlap helps, storage optimization may be suboptimal
        compared to full-horizon solutions due to limited foresight in each segment.

    Args:
        name: Unique identifier for the calculation, used in result files and logging.
        flow_system: The FlowSystem to optimize, containing all components, flows, and buses.
        timesteps_per_segment: Number of timesteps in each segment (excluding overlap).
            Must be > 2 to avoid internal side effects. Larger values provide better
            optimization at the cost of memory and computation time.
        overlap_timesteps: Number of additional timesteps added to each segment.
            Improves storage optimization by providing lookahead. Higher values
            improve solution quality but increase computational cost.
        nr_of_previous_values: Number of previous timestep values to transfer between
            segments for initialization. Typically 1 is sufficient.
        folder: Directory for saving results. Defaults to current working directory + 'results'.

    Examples:
        Annual optimization with monthly segments:

        ```python
        # 8760 hours annual data with monthly segments (730 hours) and 48-hour overlap
        segmented_calc = SegmentedCalculation(
            name='annual_energy_system',
            flow_system=energy_system,
            timesteps_per_segment=730,  # ~1 month
            overlap_timesteps=48,  # 2 days overlap
            folder=Path('results/segmented'),
        )
        segmented_calc.do_modeling_and_solve(solver='gurobi')
        ```

        Weekly optimization with daily overlap:

        ```python
        # Weekly segments for detailed operational planning
        weekly_calc = SegmentedCalculation(
            name='weekly_operations',
            flow_system=industrial_system,
            timesteps_per_segment=168,  # 1 week (hourly data)
            overlap_timesteps=24,  # 1 day overlap
            nr_of_previous_values=1,
        )
        ```

        Large-scale system with minimal overlap:

        ```python
        # Large system with minimal overlap for computational efficiency
        large_calc = SegmentedCalculation(
            name='large_scale_grid',
            flow_system=grid_system,
            timesteps_per_segment=100,  # Shorter segments
            overlap_timesteps=5,  # Minimal overlap
        )
        ```

    Design Considerations:
        **Segment Size**: Balance between solution quality and computational efficiency.
        Larger segments provide better optimization but require more memory and time.

        **Overlap Duration**: More overlap improves storage dynamics and reduces
        end-effects but increases computational cost. Typically 5-10% of segment length.

        **Storage Systems**: Systems with large storage components benefit from longer
        overlaps to capture charge/discharge cycles effectively.

        **Investment Decisions**: Use FullCalculation for problems requiring investment
        optimization, as SegmentedCalculation cannot handle investment parameters.

    Common Use Cases:
        - **Annual Planning**: Long-term planning with seasonal variations
        - **Large Networks**: Spatially or temporally large energy systems
        - **Memory-Limited Systems**: When full optimization exceeds available memory
        - **Operational Planning**: Detailed short-term optimization with limited foresight
        - **Sensitivity Analysis**: Quick approximate solutions for parameter studies

    Performance Tips:
        - Start with FullCalculation and use this class if memory issues occur
        - Use longer overlaps for systems with significant storage
        - Monitor solution quality at segment boundaries for discontinuities

    Warning:
        The evaluation of the solution is a bit more complex than FullCalculation or AggregatedCalculation
        due to the overlapping individual solutions.

    """

    def __init__(
        self,
        name: str,
        flow_system: FlowSystem,
        timesteps_per_segment: int,
        overlap_timesteps: int,
        nr_of_previous_values: int = 1,
        folder: pathlib.Path | None = None,
    ):
        super().__init__(name, flow_system, folder=folder)
        self.timesteps_per_segment = timesteps_per_segment
        self.overlap_timesteps = overlap_timesteps
        self.nr_of_previous_values = nr_of_previous_values
        self.sub_calculations: list[FullCalculation] = []

        self.segment_names = [
            f'Segment_{i + 1}' for i in range(math.ceil(len(self.all_timesteps) / self.timesteps_per_segment))
        ]
        self._timesteps_per_segment = self._calculate_timesteps_per_segment()

        assert timesteps_per_segment > 2, 'The Segment length must be greater 2, due to unwanted internal side effects'
        assert self.timesteps_per_segment_with_overlap <= len(self.all_timesteps), (
            f'{self.timesteps_per_segment_with_overlap=} cant be greater than the total length {len(self.all_timesteps)}'
        )

        self.flow_system._connect_network()  # Connect network to ensure that all Flows know their Component
        # Storing all original start values
        self._original_start_values = {
            **{flow.label_full: flow.previous_flow_rate for flow in self.flow_system.flows.values()},
            **{
                comp.label_full: comp.initial_charge_state
                for comp in self.flow_system.components.values()
                if isinstance(comp, Storage)
            },
        }
        self._transfered_start_values: list[dict[str, Any]] = []

    def _create_sub_calculations(self):
        for i, (segment_name, timesteps_of_segment) in enumerate(
            zip(self.segment_names, self._timesteps_per_segment, strict=True)
        ):
            calc = FullCalculation(f'{self.name}-{segment_name}', self.flow_system.sel(time=timesteps_of_segment))
            calc.flow_system._connect_network()  # Connect to have Correct names of Flows!

            self.sub_calculations.append(calc)
            logger.info(
                f'{segment_name} [{i + 1:>2}/{len(self.segment_names):<2}] '
                f'({timesteps_of_segment[0]} -> {timesteps_of_segment[-1]}):'
            )

    def do_modeling_and_solve(
        self, solver: _Solver, log_file: pathlib.Path | None = None, log_main_results: bool = False
    ) -> SegmentedCalculation:
        logger.info(f'{"":#^80}')
        logger.info(f'{" Segmented Solving ":#^80}')
        self._create_sub_calculations()

        for i, calculation in enumerate(self.sub_calculations):
            logger.info(
                f'{self.segment_names[i]} [{i + 1:>2}/{len(self.segment_names):<2}] '
                f'({calculation.flow_system.timesteps[0]} -> {calculation.flow_system.timesteps[-1]}):'
            )

            if i > 0 and self.nr_of_previous_values > 0:
                self._transfer_start_values(i)

            calculation.do_modeling()

            # Warn about Investments, but only in fist run
            if i == 0:
                invest_elements = [
                    model.label_full
                    for component in calculation.flow_system.components.values()
                    for model in component.submodel.all_submodels
                    if isinstance(model, InvestmentModel)
                ]
                if invest_elements:
                    logger.critical(
                        f'Investments are not supported in Segmented Calculation! '
                        f'Following InvestmentModels were found: {invest_elements}'
                    )

            calculation.solve(
                solver,
                log_file=pathlib.Path(log_file) if log_file is not None else self.folder / f'{self.name}.log',
                log_main_results=log_main_results,
            )

        for calc in self.sub_calculations:
            for key, value in calc.durations.items():
                self.durations[key] += value

        self.results = SegmentedCalculationResults.from_calculation(self)

        return self

    def _transfer_start_values(self, i: int):
        """
        This function gets the last values of the previous solved segment and
        inserts them as start values for the next segment
        """
        timesteps_of_prior_segment = self.sub_calculations[i - 1].flow_system.timesteps_extra

        start = self.sub_calculations[i].flow_system.timesteps[0]
        start_previous_values = timesteps_of_prior_segment[self.timesteps_per_segment - self.nr_of_previous_values]
        end_previous_values = timesteps_of_prior_segment[self.timesteps_per_segment - 1]

        logger.debug(
            f'Start of next segment: {start}. Indices of previous values: {start_previous_values} -> {end_previous_values}'
        )
        current_flow_system = self.sub_calculations[i - 1].flow_system
        next_flow_system = self.sub_calculations[i].flow_system

        start_values_of_this_segment = {}

        for current_flow in current_flow_system.flows.values():
            next_flow = next_flow_system.flows[current_flow.label_full]
            next_flow.previous_flow_rate = current_flow.submodel.flow_rate.solution.sel(
                time=slice(start_previous_values, end_previous_values)
            ).values
            start_values_of_this_segment[current_flow.label_full] = next_flow.previous_flow_rate

        for current_comp in current_flow_system.components.values():
            next_comp = next_flow_system.components[current_comp.label_full]
            if isinstance(next_comp, Storage):
                next_comp.initial_charge_state = current_comp.submodel.charge_state.solution.sel(time=start).item()
                start_values_of_this_segment[current_comp.label_full] = next_comp.initial_charge_state

        self._transfered_start_values.append(start_values_of_this_segment)

    def _calculate_timesteps_per_segment(self) -> list[pd.DatetimeIndex]:
        timesteps_per_segment = []
        for i, _ in enumerate(self.segment_names):
            start = self.timesteps_per_segment * i
            end = min(start + self.timesteps_per_segment_with_overlap, len(self.all_timesteps))
            timesteps_per_segment.append(self.all_timesteps[start:end])
        return timesteps_per_segment

    @property
    def timesteps_per_segment_with_overlap(self):
        return self.timesteps_per_segment + self.overlap_timesteps

    @property
    def start_values_of_segments(self) -> list[dict[str, Any]]:
        """Gives an overview of the start values of all Segments"""
        return [{name: value for name, value in self._original_start_values.items()}] + [
            start_values for start_values in self._transfered_start_values
        ]

    @property
    def all_timesteps(self) -> pd.DatetimeIndex:
        return self.flow_system.timesteps
