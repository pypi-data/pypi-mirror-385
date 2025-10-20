import logging

import linopy
import numpy as np
import xarray as xr

from .config import CONFIG
from .core import TemporalData
from .structure import Submodel

logger = logging.getLogger('flixopt')


class ModelingUtilitiesAbstract:
    """Utility functions for modeling calculations - leveraging xarray for temporal data"""

    @staticmethod
    def to_binary(
        values: xr.DataArray,
        epsilon: float | None = None,
        dims: str | list[str] | None = None,
    ) -> xr.DataArray:
        """
        Converts a DataArray to binary {0, 1} values.

        Args:
            values: Input DataArray to convert to binary
            epsilon: Tolerance for zero detection (uses CONFIG.Modeling.epsilon if None)
            dims: Dims to keep. Other dimensions are collapsed using .any() -> If any value is 1, all are 1.

        Returns:
            Binary DataArray with same shape (or collapsed if collapse_non_time=True)
        """
        if not isinstance(values, xr.DataArray):
            values = xr.DataArray(values, dims=['time'], coords={'time': range(len(values))})

        if epsilon is None:
            epsilon = CONFIG.Modeling.epsilon

        if values.size == 0:
            return xr.DataArray(0) if values.item() < epsilon else xr.DataArray(1)

        # Convert to binary states
        binary_states = np.abs(values) >= epsilon

        # Optionally collapse dimensions using .any()
        if dims is not None:
            dims = [dims] if isinstance(dims, str) else dims

            binary_states = binary_states.any(dim=[d for d in binary_states.dims if d not in dims])

        return binary_states.astype(int)

    @staticmethod
    def count_consecutive_states(
        binary_values: xr.DataArray | np.ndarray | list[int, float],
        dim: str = 'time',
        epsilon: float | None = None,
    ) -> float:
        """Count consecutive steps in the final active state of a binary time series.

        This function counts how many consecutive time steps the series remains "on"
        (non-zero) at the end of the time series. If the final state is "off", returns 0.

        Args:
            binary_values: Binary DataArray with values close to 0 (off) or 1 (on).
            dim: Dimension along which to count consecutive states.
            epsilon: Tolerance for zero detection. Uses CONFIG.Modeling.epsilon if None.

        Returns:
            Sum of values in the final consecutive "on" period. Returns 0.0 if the
            final state is "off".

        Examples:
            >>> arr = xr.DataArray([0, 0, 1, 1, 1, 0, 1, 1], dims=['time'])
            >>> ModelingUtilitiesAbstract.count_consecutive_states(arr)
            2.0

            >>> arr = [0, 0, 1, 0, 1, 1, 1, 1]
            >>> ModelingUtilitiesAbstract.count_consecutive_states(arr)
            4.0
        """
        epsilon = epsilon or CONFIG.Modeling.epsilon

        if isinstance(binary_values, xr.DataArray):
            # xarray path
            other_dims = [d for d in binary_values.dims if d != dim]
            if other_dims:
                binary_values = binary_values.any(dim=other_dims)
            arr = binary_values.values
        else:
            # numpy/array-like path
            arr = np.asarray(binary_values)

        # Flatten to 1D if needed
        arr = arr.ravel() if arr.ndim > 1 else arr

        # Handle edge cases
        if arr.size == 0:
            return 0.0
        if arr.size == 1:
            return float(arr[0]) if not np.isclose(arr[0], 0, atol=epsilon) else 0.0

        # Return 0 if final state is off
        if np.isclose(arr[-1], 0, atol=epsilon):
            return 0.0

        # Find the last zero position (treat NaNs as off)
        arr = np.nan_to_num(arr, nan=0.0)
        is_zero = np.isclose(arr, 0, atol=epsilon)
        zero_indices = np.where(is_zero)[0]

        # Calculate sum from last zero to end
        start_idx = zero_indices[-1] + 1 if zero_indices.size > 0 else 0

        return float(np.sum(arr[start_idx:]))


class ModelingUtilities:
    @staticmethod
    def compute_consecutive_hours_in_state(
        binary_values: TemporalData,
        hours_per_timestep: int | float,
        epsilon: float = None,
    ) -> float:
        """
        Computes the final consecutive duration in state 'on' (=1) in hours.

        Args:
            binary_values: Binary DataArray with 'time' dim, or scalar/array
            hours_per_timestep: Duration of each timestep in hours
            epsilon: Tolerance for zero detection (uses CONFIG.Modeling.epsilon if None)

        Returns:
            The duration of the final consecutive 'on' period in hours
        """
        if not isinstance(hours_per_timestep, (int, float)):
            raise TypeError(f'hours_per_timestep must be a scalar, got {type(hours_per_timestep)}')

        return (
            ModelingUtilitiesAbstract.count_consecutive_states(binary_values=binary_values, epsilon=epsilon)
            * hours_per_timestep
        )

    @staticmethod
    def compute_previous_states(previous_values: xr.DataArray | None, epsilon: float | None = None) -> xr.DataArray:
        return ModelingUtilitiesAbstract.to_binary(values=previous_values, epsilon=epsilon, dims='time')

    @staticmethod
    def compute_previous_on_duration(
        previous_values: xr.DataArray, hours_per_step: xr.DataArray | float | int
    ) -> float:
        return (
            ModelingUtilitiesAbstract.count_consecutive_states(ModelingUtilitiesAbstract.to_binary(previous_values))
            * hours_per_step
        )

    @staticmethod
    def compute_previous_off_duration(
        previous_values: xr.DataArray, hours_per_step: xr.DataArray | float | int
    ) -> float:
        """
        Compute previous consecutive 'off' duration.

        Args:
            previous_values: DataArray with 'time' dimension
            hours_per_step: Duration of each timestep in hours

        Returns:
            Previous consecutive off duration in hours
        """
        if previous_values is None or previous_values.size == 0:
            return 0.0

        previous_states = ModelingUtilities.compute_previous_states(previous_values)
        previous_off_states = 1 - previous_states
        return ModelingUtilities.compute_consecutive_hours_in_state(previous_off_states, hours_per_step)

    @staticmethod
    def get_most_recent_state(previous_values: xr.DataArray | None) -> int:
        """
        Get the most recent binary state from previous values.

        Args:
            previous_values: DataArray with 'time' dimension

        Returns:
            Most recent binary state (0 or 1)
        """
        if previous_values is None or previous_values.size == 0:
            return 0

        previous_states = ModelingUtilities.compute_previous_states(previous_values)
        return int(previous_states.isel(time=-1).item())


class ModelingPrimitives:
    """Mathematical modeling primitives returning (variables, constraints) tuples"""

    @staticmethod
    def expression_tracking_variable(
        model: Submodel,
        tracked_expression,
        name: str = None,
        short_name: str = None,
        bounds: tuple[TemporalData, TemporalData] = None,
        coords: str | list[str] | None = None,
    ) -> tuple[linopy.Variable, linopy.Constraint]:
        """
        Creates variable that equals a given expression.

        Mathematical formulation:
            tracker = expression
            lower ≤ tracker ≤ upper (if bounds provided)

        Returns:
            variables: {'tracker': tracker_var}
            constraints: {'tracking': constraint}
        """
        if not isinstance(model, Submodel):
            raise ValueError('ModelingPrimitives.expression_tracking_variable() can only be used with a Submodel')

        if not bounds:
            tracker = model.add_variables(name=name, coords=model.get_coords(coords), short_name=short_name)
        else:
            tracker = model.add_variables(
                lower=bounds[0] if bounds[0] is not None else -np.inf,
                upper=bounds[1] if bounds[1] is not None else np.inf,
                name=name,
                coords=model.get_coords(coords),
                short_name=short_name,
            )

        # Constraint: tracker = expression
        tracking = model.add_constraints(tracker == tracked_expression, name=name, short_name=short_name)

        return tracker, tracking

    @staticmethod
    def consecutive_duration_tracking(
        model: Submodel,
        state_variable: linopy.Variable,
        name: str = None,
        short_name: str = None,
        minimum_duration: TemporalData | None = None,
        maximum_duration: TemporalData | None = None,
        duration_dim: str = 'time',
        duration_per_step: int | float | TemporalData = None,
        previous_duration: TemporalData = 0,
    ) -> tuple[linopy.Variable, tuple[linopy.Constraint, linopy.Constraint, linopy.Constraint]]:
        """
        Creates consecutive duration tracking for a binary state variable.

        Mathematical formulation:
            duration[t] ≤ state[t] * M  ∀t
            duration[t+1] ≤ duration[t] + duration_per_step[t]  ∀t
            duration[t+1] ≥ duration[t] + duration_per_step[t] + (state[t+1] - 1) * M  ∀t
            duration[0] = (duration_per_step[0] + previous_duration) * state[0]

            If minimum_duration provided:
                duration[t] ≥ (state[t-1] - state[t]) * minimum_duration[t-1]  ∀t > 0

        Args:
            name: Name of the duration variable
            state_variable: Binary state variable to track duration for
            minimum_duration: Optional minimum consecutive duration
            maximum_duration: Optional maximum consecutive duration
            previous_duration: Duration from before first timestep

        Returns:
            variables: {'duration': duration_var}
            constraints: {'ub': constraint, 'forward': constraint, 'backward': constraint, ...}
        """
        if not isinstance(model, Submodel):
            raise ValueError('ModelingPrimitives.consecutive_duration_tracking() can only be used with a Submodel')

        mega = duration_per_step.sum(duration_dim) + previous_duration  # Big-M value

        # Duration variable
        duration = model.add_variables(
            lower=0,
            upper=maximum_duration if maximum_duration is not None else mega,
            coords=state_variable.coords,
            name=name,
            short_name=short_name,
        )

        constraints = {}

        # Upper bound: duration[t] ≤ state[t] * M
        constraints['ub'] = model.add_constraints(duration <= state_variable * mega, name=f'{duration.name}|ub')

        # Forward constraint: duration[t+1] ≤ duration[t] + duration_per_step[t]
        constraints['forward'] = model.add_constraints(
            duration.isel({duration_dim: slice(1, None)})
            <= duration.isel({duration_dim: slice(None, -1)}) + duration_per_step.isel({duration_dim: slice(None, -1)}),
            name=f'{duration.name}|forward',
        )

        # Backward constraint: duration[t+1] ≥ duration[t] + duration_per_step[t] + (state[t+1] - 1) * M
        constraints['backward'] = model.add_constraints(
            duration.isel({duration_dim: slice(1, None)})
            >= duration.isel({duration_dim: slice(None, -1)})
            + duration_per_step.isel({duration_dim: slice(None, -1)})
            + (state_variable.isel({duration_dim: slice(1, None)}) - 1) * mega,
            name=f'{duration.name}|backward',
        )

        # Initial condition: duration[0] = (duration_per_step[0] + previous_duration) * state[0]
        constraints['initial'] = model.add_constraints(
            duration.isel({duration_dim: 0})
            == (duration_per_step.isel({duration_dim: 0}) + previous_duration) * state_variable.isel({duration_dim: 0}),
            name=f'{duration.name}|initial',
        )

        # Minimum duration constraint if provided
        if minimum_duration is not None:
            constraints['lb'] = model.add_constraints(
                duration
                >= (
                    state_variable.isel({duration_dim: slice(None, -1)})
                    - state_variable.isel({duration_dim: slice(1, None)})
                )
                * minimum_duration.isel({duration_dim: slice(None, -1)}),
                name=f'{duration.name}|lb',
            )

            # Handle initial condition for minimum duration
            prev = (
                float(previous_duration)
                if not isinstance(previous_duration, xr.DataArray)
                else float(previous_duration.max().item())
            )
            min0 = float(minimum_duration.isel({duration_dim: 0}).max().item())
            if prev > 0 and prev < min0:
                constraints['initial_lb'] = model.add_constraints(
                    state_variable.isel({duration_dim: 0}) == 1, name=f'{duration.name}|initial_lb'
                )

        variables = {'duration': duration}

        return variables, constraints

    @staticmethod
    def mutual_exclusivity_constraint(
        model: Submodel,
        binary_variables: list[linopy.Variable],
        tolerance: float = 1,
        short_name: str = 'mutual_exclusivity',
    ) -> linopy.Constraint:
        """
        Creates mutual exclusivity constraint for binary variables.

        Mathematical formulation:
            Σ(binary_vars[i]) ≤ tolerance  ∀t

        Ensures at most one binary variable can be 1 at any time.
        Tolerance > 1.0 accounts for binary variable numerical precision.

        Args:
            binary_variables: List of binary variables that should be mutually exclusive
            tolerance: Upper bound
            short_name: Short name of the constraint

        Returns:
            variables: {} (no new variables created)
            constraints: {'mutual_exclusivity': constraint}

        Raises:
            AssertionError: If fewer than 2 variables provided or variables aren't binary
        """
        if not isinstance(model, Submodel):
            raise ValueError('ModelingPrimitives.mutual_exclusivity_constraint() can only be used with a Submodel')

        assert len(binary_variables) >= 2, (
            f'Mutual exclusivity requires at least 2 variables, got {len(binary_variables)}'
        )

        for var in binary_variables:
            assert var.attrs.get('binary', False), (
                f'Variable {var.name} must be binary for mutual exclusivity constraint'
            )

        # Create mutual exclusivity constraint
        mutual_exclusivity = model.add_constraints(sum(binary_variables) <= tolerance, short_name=short_name)

        return mutual_exclusivity


class BoundingPatterns:
    """High-level patterns that compose primitives and return (variables, constraints) tuples"""

    @staticmethod
    def basic_bounds(
        model: Submodel,
        variable: linopy.Variable,
        bounds: tuple[TemporalData, TemporalData],
        name: str = None,
    ) -> list[linopy.constraints.Constraint]:
        """Create simple bounds.
        variable ∈ [lower_bound, upper_bound]

        Mathematical Formulation:
            lower_bound ≤ variable ≤ upper_bound

        Args:
            model: The optimization model instance
            variable: Variable to be bounded
            bounds: Tuple of (lower_bound, upper_bound) absolute bounds

        Returns:
            List containing lower_bound and upper_bound constraints
        """
        if not isinstance(model, Submodel):
            raise ValueError('BoundingPatterns.basic_bounds() can only be used with a Submodel')

        lower_bound, upper_bound = bounds
        name = name or f'{variable.name}'

        upper_constraint = model.add_constraints(variable <= upper_bound, name=f'{name}|ub')
        lower_constraint = model.add_constraints(variable >= lower_bound, name=f'{name}|lb')

        return [lower_constraint, upper_constraint]

    @staticmethod
    def bounds_with_state(
        model: Submodel,
        variable: linopy.Variable,
        bounds: tuple[TemporalData, TemporalData],
        variable_state: linopy.Variable,
        name: str = None,
    ) -> list[linopy.Constraint]:
        """Constraint a variable to bounds, that can be escaped from to 0 by a binary variable.
        variable ∈ {0, [max(ε, lower_bound), upper_bound]}

        Mathematical Formulation:
            - variable_state * max(ε, lower_bound) ≤ variable ≤ variable_state * upper_bound

        Use Cases:
            - Investment decisions
            - Unit commitment (on/off states)

        Args:
            model: The optimization model instance
            variable: Variable to be bounded
            bounds: Tuple of (lower_bound, upper_bound) absolute bounds
            variable_state: Binary variable controlling the bounds

        Returns:
            Tuple containing:
                - variables (Dict): Empty dict
                - constraints (Dict[str, linopy.Constraint]): 'ub', 'lb'
        """
        if not isinstance(model, Submodel):
            raise ValueError('BoundingPatterns.bounds_with_state() can only be used with a Submodel')

        lower_bound, upper_bound = bounds
        name = name or f'{variable.name}'

        if np.allclose(lower_bound, upper_bound, atol=1e-10, equal_nan=True):
            fix_constraint = model.add_constraints(variable == variable_state * upper_bound, name=f'{name}|fix')
            return [fix_constraint]

        epsilon = np.maximum(CONFIG.Modeling.epsilon, lower_bound)

        upper_constraint = model.add_constraints(variable <= variable_state * upper_bound, name=f'{name}|ub')
        lower_constraint = model.add_constraints(variable >= variable_state * epsilon, name=f'{name}|lb')

        return [lower_constraint, upper_constraint]

    @staticmethod
    def scaled_bounds(
        model: Submodel,
        variable: linopy.Variable,
        scaling_variable: linopy.Variable,
        relative_bounds: tuple[TemporalData, TemporalData],
        name: str = None,
    ) -> list[linopy.Constraint]:
        """Constraint a variable by scaling bounds, dependent on another variable.
        variable ∈ [lower_bound * scaling_variable, upper_bound * scaling_variable]

        Mathematical Formulation:
            scaling_variable * lower_factor ≤ variable ≤ scaling_variable * upper_factor

        Use Cases:
            - Flow rates bounded by equipment capacity
            - Production levels scaled by plant size

        Args:
            model: The optimization model instance
            variable: Variable to be bounded
            scaling_variable: Variable that scales the bound factors
            relative_bounds: Tuple of (lower_factor, upper_factor) relative to scaling variable

        Returns:
            Tuple containing:
                - variables (Dict): Empty dict
                - constraints (Dict[str, linopy.Constraint]): 'ub', 'lb'
        """
        if not isinstance(model, Submodel):
            raise ValueError('BoundingPatterns.scaled_bounds() can only be used with a Submodel')

        rel_lower, rel_upper = relative_bounds
        name = name or f'{variable.name}'

        if np.allclose(rel_lower, rel_upper, atol=1e-10, equal_nan=True):
            return [model.add_constraints(variable == scaling_variable * rel_lower, name=f'{name}|fixed')]

        upper_constraint = model.add_constraints(variable <= scaling_variable * rel_upper, name=f'{name}|ub')
        lower_constraint = model.add_constraints(variable >= scaling_variable * rel_lower, name=f'{name}|lb')

        return [lower_constraint, upper_constraint]

    @staticmethod
    def scaled_bounds_with_state(
        model: Submodel,
        variable: linopy.Variable,
        scaling_variable: linopy.Variable,
        relative_bounds: tuple[TemporalData, TemporalData],
        scaling_bounds: tuple[TemporalData, TemporalData],
        variable_state: linopy.Variable,
        name: str = None,
    ) -> list[linopy.Constraint]:
        """Constraint a variable by scaling bounds with binary state control.

        variable ∈ {0, [max(ε, lower_relative_bound) * scaling_variable, upper_relative_bound * scaling_variable]}

        Mathematical Formulation (Big-M):
            (variable_state - 1) * M_misc + scaling_variable * rel_lower ≤ variable ≤ scaling_variable * rel_upper
            variable_state * big_m_lower ≤ variable ≤ variable_state * big_m_upper

        Where:
            M_misc = scaling_max * rel_lower
            big_m_upper = scaling_max * rel_upper
            big_m_lower = max(ε, scaling_min * rel_lower)

        Args:
            model: The optimization model instance
            variable: Variable to be bounded
            scaling_variable: Variable that scales the bound factors
            relative_bounds: Tuple of (lower_factor, upper_factor) relative to scaling variable
            scaling_bounds: Tuple of (scaling_min, scaling_max) bounds of the scaling variable
            variable_state: Binary variable for on/off control
            name: Optional name prefix for constraints

        Returns:
            List[linopy.Constraint]: List of constraint objects
        """
        if not isinstance(model, Submodel):
            raise ValueError('BoundingPatterns.scaled_bounds_with_state() can only be used with a Submodel')

        rel_lower, rel_upper = relative_bounds
        scaling_min, scaling_max = scaling_bounds
        name = name or f'{variable.name}'

        big_m_misc = scaling_max * rel_lower

        scaling_lower = model.add_constraints(
            variable >= (variable_state - 1) * big_m_misc + scaling_variable * rel_lower, name=f'{name}|lb2'
        )
        scaling_upper = model.add_constraints(variable <= scaling_variable * rel_upper, name=f'{name}|ub2')

        big_m_upper = rel_upper * scaling_max
        big_m_lower = np.maximum(CONFIG.Modeling.epsilon, rel_lower * scaling_min)

        binary_upper = model.add_constraints(variable_state * big_m_upper >= variable, name=f'{name}|ub1')
        binary_lower = model.add_constraints(variable_state * big_m_lower <= variable, name=f'{name}|lb1')

        return [scaling_lower, scaling_upper, binary_lower, binary_upper]

    @staticmethod
    def state_transition_bounds(
        model: Submodel,
        state_variable: linopy.Variable,
        switch_on: linopy.Variable,
        switch_off: linopy.Variable,
        name: str,
        previous_state=0,
        coord: str = 'time',
    ) -> tuple[linopy.Constraint, linopy.Constraint, linopy.Constraint]:
        """
        Creates switch-on/off variables with state transition logic.

        Mathematical formulation:
            switch_on[t] - switch_off[t] = state[t] - state[t-1]  ∀t > 0
            switch_on[0] - switch_off[0] = state[0] - previous_state
            switch_on[t] + switch_off[t] ≤ 1  ∀t
            switch_on[t], switch_off[t] ∈ {0, 1}

        Returns:
            variables: {'switch_on': binary_var, 'switch_off': binary_var}
            constraints: {'transition': constraint, 'initial': constraint, 'mutex': constraint}
        """
        if not isinstance(model, Submodel):
            raise ValueError('ModelingPrimitives.state_transition_bounds() can only be used with a Submodel')

        # State transition constraints for t > 0
        transition = model.add_constraints(
            switch_on.isel({coord: slice(1, None)}) - switch_off.isel({coord: slice(1, None)})
            == state_variable.isel({coord: slice(1, None)}) - state_variable.isel({coord: slice(None, -1)}),
            name=f'{name}|transition',
        )

        # Initial state transition for t = 0
        initial = model.add_constraints(
            switch_on.isel({coord: 0}) - switch_off.isel({coord: 0})
            == state_variable.isel({coord: 0}) - previous_state,
            name=f'{name}|initial',
        )

        # At most one switch per timestep
        mutex = model.add_constraints(switch_on + switch_off <= 1, name=f'{name}|mutex')

        return transition, initial, mutex

    @staticmethod
    def continuous_transition_bounds(
        model: Submodel,
        continuous_variable: linopy.Variable,
        switch_on: linopy.Variable,
        switch_off: linopy.Variable,
        name: str,
        max_change: float | xr.DataArray,
        previous_value: float | xr.DataArray = 0.0,
        coord: str = 'time',
    ) -> tuple[linopy.Constraint, linopy.Constraint, linopy.Constraint, linopy.Constraint]:
        """
        Constrains a continuous variable to only change when switch variables are active.

        Mathematical formulation:
            -max_change * (switch_on[t] + switch_off[t]) <= continuous[t] - continuous[t-1] <= max_change * (switch_on[t] + switch_off[t])  ∀t > 0
            -max_change * (switch_on[0] + switch_off[0]) <= continuous[0] - previous_value <= max_change * (switch_on[0] + switch_off[0])
            switch_on[t], switch_off[t] ∈ {0, 1}

        This ensures the continuous variable can only change when switch_on or switch_off is 1.
        When both switches are 0, the variable must stay exactly constant.

        Args:
            model: The submodel to add constraints to
            continuous_variable: The continuous variable to constrain
            switch_on: Binary variable indicating when changes are allowed (typically transitions to active state)
            switch_off: Binary variable indicating when changes are allowed (typically transitions to inactive state)
            name: Base name for the constraints
            max_change: Maximum possible change in the continuous variable (Big-M value)
            previous_value: Initial value of the continuous variable before first period
            coord: Coordinate name for time dimension

        Returns:
            Tuple of constraints: (transition_upper, transition_lower, initial_upper, initial_lower)
        """
        if not isinstance(model, Submodel):
            raise ValueError('ModelingPrimitives.continuous_transition_bounds() can only be used with a Submodel')

        # Transition constraints for t > 0: continuous variable can only change when switches are active
        transition_upper = model.add_constraints(
            continuous_variable.isel({coord: slice(1, None)}) - continuous_variable.isel({coord: slice(None, -1)})
            <= max_change * (switch_on.isel({coord: slice(1, None)}) + switch_off.isel({coord: slice(1, None)})),
            name=f'{name}|transition_ub',
        )

        transition_lower = model.add_constraints(
            -(continuous_variable.isel({coord: slice(1, None)}) - continuous_variable.isel({coord: slice(None, -1)}))
            <= max_change * (switch_on.isel({coord: slice(1, None)}) + switch_off.isel({coord: slice(1, None)})),
            name=f'{name}|transition_lb',
        )

        # Initial constraints for t = 0
        initial_upper = model.add_constraints(
            continuous_variable.isel({coord: 0}) - previous_value
            <= max_change * (switch_on.isel({coord: 0}) + switch_off.isel({coord: 0})),
            name=f'{name}|initial_ub',
        )

        initial_lower = model.add_constraints(
            -continuous_variable.isel({coord: 0}) + previous_value
            <= max_change * (switch_on.isel({coord: 0}) + switch_off.isel({coord: 0})),
            name=f'{name}|initial_lb',
        )

        return transition_upper, transition_lower, initial_upper, initial_lower

    @staticmethod
    def link_changes_to_level_with_binaries(
        model: Submodel,
        level_variable: linopy.Variable,
        increase_variable: linopy.Variable,
        decrease_variable: linopy.Variable,
        increase_binary: linopy.Variable,
        decrease_binary: linopy.Variable,
        name: str,
        max_change: float | xr.DataArray,
        initial_level: float | xr.DataArray = 0.0,
        coord: str = 'period',
    ) -> tuple[linopy.Constraint, linopy.Constraint, linopy.Constraint, linopy.Constraint, linopy.Constraint]:
        """
        Link changes to level evolution with binary control and mutual exclusivity.

        Creates the complete constraint system for ALL time periods:
        1. level[0] = initial_level + increase[0] - decrease[0]
        2. level[t] = level[t-1] + increase[t] - decrease[t]  ∀t > 0
        3. increase[t] <= max_change * increase_binary[t]  ∀t
        4. decrease[t] <= max_change * decrease_binary[t]  ∀t
        5. increase_binary[t] + decrease_binary[t] <= 1  ∀t

        Args:
            model: The submodel to add constraints to
            increase_variable: Incremental additions for ALL periods (>= 0)
            decrease_variable: Incremental reductions for ALL periods (>= 0)
            increase_binary: Binary indicators for increases for ALL periods
            decrease_binary: Binary indicators for decreases for ALL periods
            level_variable: Level variable for ALL periods
            name: Base name for constraints
            max_change: Maximum change per period
            initial_level: Starting level before first period
            coord: Time coordinate name

        Returns:
            Tuple of (initial_constraint, transition_constraints, increase_bounds, decrease_bounds, mutual_exclusion)
        """
        if not isinstance(model, Submodel):
            raise ValueError('BoundingPatterns.link_changes_to_level_with_binaries() can only be used with a Submodel')

        # 1. Initial period: level[0] - initial_level =  increase[0] - decrease[0]
        initial_constraint = model.add_constraints(
            level_variable.isel({coord: 0}) - initial_level
            == increase_variable.isel({coord: 0}) - decrease_variable.isel({coord: 0}),
            name=f'{name}|initial_level',
        )

        # 2. Transition periods: level[t] = level[t-1] + increase[t] - decrease[t] for t > 0
        transition_constraints = model.add_constraints(
            level_variable.isel({coord: slice(1, None)})
            == level_variable.isel({coord: slice(None, -1)})
            + increase_variable.isel({coord: slice(1, None)})
            - decrease_variable.isel({coord: slice(1, None)}),
            name=f'{name}|transitions',
        )

        # 3. Increase bounds: increase[t] <= max_change * increase_binary[t] for all t
        increase_bounds = model.add_constraints(
            increase_variable <= increase_binary * max_change,
            name=f'{name}|increase_bounds',
        )

        # 4. Decrease bounds: decrease[t] <= max_change * decrease_binary[t] for all t
        decrease_bounds = model.add_constraints(
            decrease_variable <= decrease_binary * max_change,
            name=f'{name}|decrease_bounds',
        )

        # 5. Mutual exclusivity: increase_binary[t] + decrease_binary[t] <= 1 for all t
        mutual_exclusion = model.add_constraints(
            increase_binary + decrease_binary <= 1,
            name=f'{name}|mutual_exclusion',
        )

        return initial_constraint, transition_constraints, increase_bounds, decrease_bounds, mutual_exclusion
