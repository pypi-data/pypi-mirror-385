from higher.patch import _MonkeyPatchBase
from higher.optim import DifferentiableOptimizer
from typing import Dict, Any, Callable

from boat_torch.operation_registry import register_class
from boat_torch.dynamic_ol.dynamical_system import DynamicalSystem


@register_class
class DI(DynamicalSystem):
    """
    Implements the lower-level optimization procedure for Dynamic Initialization [1].

    Parameters
    ----------
    ll_objective : Callable
        The lower-level objective function of the BLO problem.
    ul_objective : Callable
        The upper-level objective function of the BLO problem.
    ll_model : torch.nn.Module
        The lower-level model of the BLO problem.
    ul_model : torch.nn.Module
        The upper-level model of the BLO problem.
    lower_loop : int
        The number of iterations for the lower-level optimization process.
    solver_config : Dict[str, Any]
        A dictionary containing configurations for the optimization solver, including hyperparameters and specific settings for NGD and GDA.

    References
    ----------
    [1] Liu R., Liu Y., Zeng S., et al. "Towards gradient-based bilevel optimization with non-convex followers and beyond," in NeurIPS, 2021.
    """

    def optimize(
        self,
        ll_feed_dict: Dict[str, Any],
        ul_feed_dict: Dict[str, Any],
        auxiliary_model: _MonkeyPatchBase,
        auxiliary_opt: DifferentiableOptimizer,
        current_iter: int,
        next_operation: str = None,
        **kwargs
    ):
        """
        Executes the lower-level optimization procedure using the provided data and models.

        Parameters
        ----------
        ll_feed_dict : Dict[str, Any]
            Dictionary containing the lower-level data used for optimization. Typically includes:
            - "data" : The input data for lower-level optimization.
            - "target" : The target output (optional, depending on the task).

        ul_feed_dict : Dict[str, Any]
            Dictionary containing the upper-level data used for optimization. Typically includes:
            - "data" : The input data for upper-level optimization.
            - "target" : The target output (optional, depending on the task).

        auxiliary_model : _MonkeyPatchBase
            A patched lower model wrapped by the `higher` library. Serves as the lower-level model for optimization in a differentiable way.

        auxiliary_opt : DifferentiableOptimizer
            A patched optimizer for the lower-level model, wrapped by the `higher` library. Allows for differentiable optimization steps.

        current_iter : int
            The current iteration number of the optimization process.

        next_operation : str
            Specifies the next operation to execute during the optimization process. Must not be None.

        **kwargs : dict
            Additional arguments passed to the optimization procedure.

        Returns
        -------
        Dict
            A dictionary containing the input parameters and any additional keyword arguments.

        Raises
        ------
        AssertionError
            If `next_operation` is not defined.

        Notes
        -----
        Ensure that `next_operation` is defined before calling this function to specify the next operation in the optimization pipeline.
        """
        assert next_operation is not None, "Next operation should be defined."
        return {
            "ll_feed_dict": ll_feed_dict,
            "ul_feed_dict": ul_feed_dict,
            "auxiliary_model": auxiliary_model,
            "auxiliary_opt": auxiliary_opt,
            "current_iter": current_iter,
            **kwargs,
        }
