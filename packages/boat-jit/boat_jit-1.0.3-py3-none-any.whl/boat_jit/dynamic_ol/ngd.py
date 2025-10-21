from jittor import Module
from ..higher_jit.patch import _MonkeyPatchBase
from ..higher_jit.optim import DifferentiableOptimizer
from typing import Dict, Any, Callable
from ..utils.op_utils import stop_grads

from boat_jit.operation_registry import register_class
from boat_jit.dynamic_ol.dynamical_system import DynamicalSystem


@register_class
class NGD(DynamicalSystem):
    """
    Implements the optimization procedure of the Naive Gradient Descent (NGD) [1].

    Parameters
    ----------
    ll_objective : Callable
        The lower-level objective function of the BLO problem.
    ul_objective : Callable
        The upper-level objective function of the BLO problem.
    ll_model : jittor.Module
        The lower-level model of the BLO problem.
    ul_model : jittor.Module
        The upper-level model of the BLO problem.
    lower_loop : int
        The number of iterations for lower-level optimization.
    solver_config : Dict[str, Any]
        A dictionary containing configurations for the solver. Expected keys include:

        - "lower_level_opt" (jittor.optim.Optimizer): The optimizer for the lower-level model.
        - "hyper_op" (List[str]): A list of hyper-gradient operations to apply, such as "PTT" or "FOA".
        - "RGT" (Dict): Configuration for Truncated Gradient Iteration (RGT):
            - "truncate_iter" (int): The number of iterations to truncate the gradient computation.

    References
    ----------
    [1] L. Franceschi, P. Frasconi, S. Salzo, R. Grazzi, and M. Pontil, "Bilevel
        programming for hyperparameter optimization and meta-learning", in ICML, 2018.
    """

    def __init__(
        self,
        ll_objective: Callable,
        ul_objective: Callable,
        ll_model: Module,
        ul_model: Module,
        lower_loop: int,
        solver_config: Dict[str, Any],
    ):
        super(NGD, self).__init__(
            ll_objective, ul_objective, lower_loop, ul_model, ll_model, solver_config
        )
        self.truncate_max_loss_iter = "PTT" in solver_config["hyper_op"]
        self.truncate_iters = solver_config["RGT"]["truncate_iter"]
        self.ll_opt = solver_config["lower_level_opt"]
        self.foa = "FOA" in solver_config["hyper_op"]

    def optimize(
        self,
        ll_feed_dict: Dict,
        ul_feed_dict: Dict,
        auxiliary_model: _MonkeyPatchBase,
        auxiliary_opt: DifferentiableOptimizer,
        current_iter: int,
        next_operation: str = None,
        **kwargs
    ):
        """
        Execute the lower-level optimization procedure using data, models, and patched optimizers.

        Parameters
        ----------
        ll_feed_dict : Dict
            Dictionary containing the lower-level data used for optimization. Typically includes training data, targets, and other information required to compute the lower-level (LL) objective.

        ul_feed_dict : Dict
            Dictionary containing the upper-level data used for optimization. Typically includes validation data, targets, and other information required to compute the upper-level (UL) objective.

        auxiliary_model : _MonkeyPatchBase
            A patched lower-level model wrapped by the `higher` library. Used for differentiable optimization in the lower-level procedure.

        auxiliary_opt : DifferentiableOptimizer
            A patched optimizer for the lower-level model, wrapped by the `higher` library. Enables differentiable optimization.

        current_iter : int
            The current iteration number of the optimization process.

        Returns
        -------
        None
        """

        assert next_operation is None, "NGD does not support next_operation"
        if "gda_loss" in kwargs:
            gda_loss = kwargs["gda_loss"]
            alpha = kwargs["alpha"]
            alpha_decay = kwargs["alpha_decay"]
        else:
            gda_loss = None

        # truncate with RGT operation
        if self.truncate_iters > 0:
            ll_backup = [x.clone().stop_grad() for x in self.ll_model.parameters()]
            for _ in range(self.truncate_iters):
                if gda_loss is not None:
                    ll_feed_dict["alpha"] = alpha
                    loss_f = gda_loss(
                        ll_feed_dict, ul_feed_dict, self.ul_model, auxiliary_model
                    )
                    alpha = alpha * alpha_decay
                else:
                    loss_f = self.ll_objective(
                        ll_feed_dict, self.ul_model, auxiliary_model
                    )
                self.ll_opt.step(loss_f)
            for x, y in zip(self.ll_model.parameters(), auxiliary_model.parameters()):
                y.update(x.clone())
            for x, y in zip(ll_backup, self.ll_model.parameters()):
                y.update(x.clone())

        # truncate with PTT method
        if self.truncate_max_loss_iter:
            ul_loss_list = []
            for _ in range(self.lower_loop):
                if gda_loss is not None:
                    ll_feed_dict["alpha"] = alpha
                    loss_f = gda_loss(
                        ll_feed_dict, ul_feed_dict, self.ul_model, auxiliary_model
                    )
                    alpha = alpha * alpha_decay
                else:
                    loss_f = self.ll_objective(
                        ll_feed_dict, self.ul_model, auxiliary_model
                    )
                auxiliary_opt.step(loss_f)
                upper_loss = self.ul_objective(
                    ul_feed_dict, self.ul_model, auxiliary_model
                )
                ul_loss_list.append(upper_loss.item())
            ll_step_with_max_ul_loss = ul_loss_list.index(max(ul_loss_list))
            return ll_step_with_max_ul_loss + 1

        for _ in range(self.lower_loop - self.truncate_iters):
            if gda_loss is not None:
                ll_feed_dict["alpha"] = alpha
                loss_f = gda_loss(
                    ll_feed_dict, ul_feed_dict, self.ul_model, auxiliary_model
                )
                alpha = alpha * alpha_decay
            else:
                loss_f = self.ll_objective(ll_feed_dict, self.ul_model, auxiliary_model)
            auxiliary_opt.step(loss_f)
            auxiliary_opt.step(loss_f, grad_callback=stop_grads if self.foa else None)
        return -1