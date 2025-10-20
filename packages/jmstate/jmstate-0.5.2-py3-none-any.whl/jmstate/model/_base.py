from bisect import bisect_left
from collections.abc import Callable, Sequence
from functools import partial
from typing import Any, cast

import torch
from pydantic import ConfigDict, validate_call
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.tree import Tree
from torch.distributions import Normal
from tqdm import trange

from ..jobs._computation import ComputeCriteria, ComputeFIM
from ..jobs._fitting import Fit
from ..typedefs._data import CompleteModelData, ModelData, ModelDesign, SampleData
from ..typedefs._defaults import DEFAULT_HYPERPARAMETERS, DEFAULT_HYPERPARAMETERS_FIELDS
from ..typedefs._defs import (
    SIGNIFICANCE_CODES,
    SIGNIFICANCE_LEVELS,
    AuxData,
    Info,
    IntNonNegative,
    IntStrictlyPositive,
    Job,
    Metrics,
    NumNonNegative,
    NumProbability,
    Trajectory,
)
from ..typedefs._params import ModelParams
from ..utils._checks import check_consistent_size, check_inf, check_nan
from ..utils._dtype import get_dtype
from ..utils._misc import run_jobs
from ..visualization._print import rich_str
from ._hazard import HazardMixin
from ._longitudinal import LongitudinalMixin
from ._prior import PriorMixin
from ._sampler import MetropolisHastingsSampler


class MultiStateJointModel(PriorMixin, LongitudinalMixin, HazardMixin):
    r"""A class of the nonlinear multistate joint model.

    It features methods to simulate data, fit based on stochastic gradient with any
    `torch.optim.Optimizer` of choice.

    It leverages the Fisher identity and stochastic gradient algorithm coupled
    with a MCMC (Metropolis Hastings) sampler:

    .. math::
        \nabla_\theta \log \mathcal{L}(\theta ; x) = \mathbb{E}_{b \sim p(\cdot \mid x,
        \theta)} \bigl(\nabla_\theta \log \mathcal{L}(\theta ; x, b)\bigr).

    The use of penalization is possible through the attribute `pen`.

    Please note this class encompasses both the linear joint model and the standard
    joint model, but also allows for the modeling of multiple states assuming a semi
    Markov property.

    Attributes:
        model_design (ModelDesign): The model design.
        params_ (ModelParams): The (variable) model parameters.
        pen (Callable[[ModelParams], torch.Tensor] | None): The log likelihood penalty.
        n_quad (int): The number of nodes for the Gauss Legendre quadrature of hazard.
        n_bisect (int): The number of bisection steps for the bisection algorithm.
        cache_limit (int | None): The limit of the cache used in hazard computation,
            greatly reducing memory and CPU usage. None means infinite, 0 means no
            caching.
        data (ModelData | None): The learnable dataset used when the model was fitted.
        metrics_ (Metrics): Metrics object containing information about the model
            and the jobs it executed.
        fit_ (bool): A boolean value set to True when the model has been fitted.
    """

    model_design: ModelDesign
    params_: ModelParams
    pen: Callable[[ModelParams], torch.Tensor] | None
    n_quad: int
    n_bisect: int
    cache_limit: int | None
    data: ModelData | None
    metrics_: Metrics
    fit_: bool

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(
        self,
        model_design: ModelDesign,
        init_params: ModelParams,
        *,
        pen: Callable[[ModelParams], torch.Tensor] | None = None,
        n_quad: IntStrictlyPositive = 32,
        n_bisect: IntStrictlyPositive = 32,
        cache_limit: IntNonNegative | None = 256,
    ):
        """Initializes the joint model based on the user defined design.

        Args:
            model_design (ModelDesign): Model design containing modeling information.
            init_params (ModelParams): Initial values for the parameters.
            pen (Callable[[ModelParams], torch.Tensor] | None, optional):
                The penalization function. Defaults to None.
            n_quad (IntStrictlyPositive, optional): The used number of points for
                Gauss-Legendre quadrature. Defaults to 32.
            n_bisect (IntStrictlyPositive, optional): The number of bisection steps
                used in transition sampling. Defaults to 32.
            cache_limit (IntNonNegative | None, optional): The max length of cache.
                Defaults to 256.
        """
        # Store model components
        self.model_design = model_design
        self.params_ = init_params.clone()

        # Store penalization
        self.pen = pen

        # Info of the Mixin Classes
        super().__init__(
            n_quad=n_quad,
            n_bisect=n_bisect,
            cache_limit=cache_limit,
        )

        # Initialize attributes that will be set later
        self.data = None
        self.metrics_ = Metrics()
        self.fit_ = False

    def __str__(self) -> str:
        """Returns a string representation of the model.

        Returns:
            str: The string representation.
        """
        tree = Tree("MultiStateJointModel")
        tree.add(f"model_design: {self.model_design}")
        tree.add(f"params_: {self.params_}")
        tree.add(f"pen: {self.pen}")
        tree.add(f"n_quad: {self.n_quad}")
        tree.add(f"n_bisect: {self.n_bisect}")
        tree.add(f"cache_limit: {self.cache_limit}")
        tree.add(f"data: {self.data}")
        tree.add(f"metrics_: object with attributes {list(vars(self.metrics_).keys())}")
        tree.add(f"fit_: {self.fit_}")

        return rich_str(tree)

    def summary(self, fmt: str = ".3f"):
        """Prints a summary of the model.

        Args:
            fmt (str, optional): The format of the p-values. Defaults to ".3f".

        This function prints the p-values of the parameters as well as values and
        standard error. Also prints the log likelihood, AIC, BIC with lovely colors!
        """
        named_params_list = self.params_.as_named_list
        values = self.params_.as_flat_tensor
        stderrors = self.stderror.as_flat_tensor
        zvalues = torch.abs(values / stderrors)
        pvalues = cast(torch.Tensor, 2 * (1 - Normal(0, 1).cdf(zvalues)))

        table = Table()
        table.add_column("Parameter name", justify="left")
        table.add_column("Value", justify="center")
        table.add_column("Standard Error", justify="center")
        table.add_column("z-value", justify="center")
        table.add_column("p-value", justify="center")
        table.add_column("Significance level", justify="center")

        i = 0
        for name, value in named_params_list:
            for j in range(1, value.numel() + 1):
                code = SIGNIFICANCE_CODES[
                    bisect_left(SIGNIFICANCE_LEVELS, pvalues[i].item())
                ]

                table.add_row(
                    f"{name}[{j}]" if value.numel() > 1 else name,
                    f"{values[i]:{fmt}}",
                    f"{stderrors[i]:{fmt}}",
                    f"{zvalues[i]:{fmt}}",
                    f"{pvalues[i]:{fmt}}",
                    code,
                )
                i += 1

        criteria = Text(
            f"Log-likelihood: {self.loglik:{fmt}}\n"
            f"Penalized negative log-likelihood: {self.nloglik_pen:{fmt}}\n"
            f"AIC: {self.aic:{fmt}}\n"
            f"BIC: {self.bic:{fmt}}",
            style="bold cyan",
        )

        content = Group(table, Rule(style="dim"), criteria, Rule(style="dim"))

        panel = Panel(
            content, title="Model Summary", border_style="green", expand=False
        )

        Console().print(panel)

    def _logpdfs_aux_fn(
        self, params: ModelParams, b: torch.Tensor, data: CompleteModelData
    ) -> tuple[torch.Tensor, AuxData]:
        """Gets the log pdfs with individual effects and log likelihoods.

        Args:
            params (ModelParams): The model parameters.
            b (torch.Tensor): The random effects.
            data (CompleteModelData): Dataset on which likelihood is computed.

        Returns:
           tuple[torch.Tensor, AuxData]: The log pdfs and aux.
        """
        psi = self.model_design.individual_effects_fn(params.gamma, data.x, b)
        logliks = super()._long_logliks(params, psi, data) + super()._hazard_logliks(
            params, psi, data
        )
        logpdfs = logliks + super()._prior_logliks(params, b)

        return (logpdfs, AuxData(psi, logliks))

    def _setup_mcmc(
        self,
        data: CompleteModelData,
        n_chains: int,
        init_step_size: int | float,
        adapt_rate: int | float,
        target_accept_rate: int | float,
    ) -> MetropolisHastingsSampler:
        """Setup the MCMC kernel and hyper-parameters.

        Args:
            data (CompleteModelData): The complete dataset.
            n_chains (int): The number of parallel MCMC chains.
            init_step_size (int | float): Kernel standard error in Metropolis.
            adapt_rate (int | float): Adaptation rate for the step_size.
            target_accept_rate (int | float): Mean acceptance target.

        Returns:
            MetropolisHastingsSampler: The intialized Markov kernel.
        """
        # Initialize random effects
        init_b = torch.zeros(
            n_chains, data.size, self.params_.Q_repr.dim, dtype=get_dtype()
        )

        return MetropolisHastingsSampler(
            partial(self._logpdfs_aux_fn, self.params_, data=data),
            init_b,
            n_chains,
            init_step_size,
            adapt_rate,
            target_accept_rate,
        )

    def _get_hyperparameters(
        self, job_factories: Sequence[Callable[[Info], Job]]
    ) -> dict[str, Any] | None:
        """Gets default hyper-parameters.

        Args:
            job_factories (Sequence[Callable[[Info], Job]]): The job factories.

        Returns:
            dict[str, Any] | None: The default hyper-parameters associated.
        """
        for job_factory in reversed(job_factories):
            key = getattr(job_factory, "cls", None)
            if not (isinstance(key, type) and issubclass(key, Job)):
                continue

            hyperparameters = DEFAULT_HYPERPARAMETERS.get(key)
            if hyperparameters is not None:
                return hyperparameters

        return None

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def sample_trajectories(
        self,
        sample_data: SampleData,
        c_max: torch.Tensor,
        *,
        max_length: IntStrictlyPositive = 10,
    ) -> list[Trajectory]:
        """Sample trajectories from the joint model.

        The sampling is done usign a bisection algorithm by inversing the log cdf of the
        transitions inside a Gillespie-like algorithm.

        Checks are run only if the `skip_validation` attribute of `sample_date` is not
        set to `True`.

        Args:
            sample_data (SampleData): Prediction data.
            c_max (TensorCol): The maximum trajectory censoring times.
            max_length (IntStrictlyPositive, optional): Maximum iterations or sampling.
                Defaults to 10.

        Raises:
            ValueError: If c_max contains inf values.
            ValueError: If c_max contains NaN values.
            ValueError: If c_max has incorrect shape.

        Returns:
            list[Trajectory]: The sampled trajectories.
        """
        c_max = c_max.to(get_dtype())

        if not sample_data.skip_validation:
            check_inf(((c_max, "c_max"),))
            check_nan(((c_max, "c_max"),))
            check_consistent_size(
                ((c_max, 0, "c_max"), (sample_data.size, None, "sample_data.size"))
            )

        return super()._sample_trajectories(sample_data, c_max, max_length=max_length)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def compute_surv_logps(
        self, sample_data: SampleData, u: torch.Tensor
    ) -> torch.Tensor:
        r"""Computes log probabilites of remaining event free up to time u.

        A censoring time may also be given. With known individual effects, this computes
        at the times :math:`u` the values of the log survival probabilities given input
        data conditionally to survival up to time :math:`c`:

        .. math::
            \log \mathbb{P}(T^* \geq u \mid T^* > c) = -\int_c^u \lambda(t) \, dt.

        When multiple transitions are allowed, :math:`\lambda(t)` is a sum over all
        possible transitions, that is to say if an individual is in the state :math:`k`
        from time :math:`t_0`, this gives:

        .. math::
            -\int_c^u \sum_{k'} \lambda^{k' \mid k}(t \mid t_0) \, dt.

        Please note this makes use of the Chasles property in order to avoid the
        computation of two integrals and make computations more precise.

        The variable `u` is expected to be a matrix with the same number of rows as
        individuals, and the same number of columns as prediction times.

        Checks are run only if the `skip_validation` attribute of `sample_date` is not
        set to `True`.

        Args:
            sample_data (SampleData): The data on which to compute the probabilities.
            u (Tensor2D): The time at which to evaluate the probabilities.

        Raises:
            ValueError: If u contains inf values.
            ValueError: If u contains NaN values.
            ValueError: If u has incorrect shape.

        Returns:
            torch.Tensor: The computed survival log probabilities.
        """
        u = u.to(get_dtype())

        if not sample_data.skip_validation:
            check_inf(((u, "u"),))
            check_nan(((u, "u"),))
            check_consistent_size(
                ((u, 0, "u"), (sample_data.size, None, "sample_data.size"))
            )

        return super()._compute_surv_logps(sample_data, u)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def do(
        self,
        data: ModelData,
        job_factories: Sequence[Callable[[Info], Job]],
        *,
        max_iterations: int | None = None,
        n_chains: IntStrictlyPositive | None = None,
        warmup: IntNonNegative | None = None,
        n_steps: IntStrictlyPositive | None = None,
        init_step_size: NumNonNegative = 0.1,
        adapt_rate: NumNonNegative = 0.1,
        accept_target: NumProbability = 0.234,
        verbose: bool = True,
    ) -> Metrics:
        """Runs the sampler loop and some jobs.

        Many jobs are predefined for user convenience, but you can use the base class
        `Job` to define your own. The `Job` class returns a factory that is not
        initialized until this function calls the job factories. For default jobs, a set
        of default hyper-parameters allows matching via the `.cls` attribute, but these
        defaults can always be overriden. In the case where multiple jobs with
        conflicting defaults are passed, only the last default will be kept and used.

        To do parallel MCMC sampling, which is enabled by default, use `n_chains`.

        Also, note that the function passed to the MCMC sampler will be built using the
        `torch.no_grad()` decorator. If needs be, use `torch.enable_grad()` if one of
        the model design functions always require gradient computation regardless of
        setting.

        To enable caching, please refer to the argument `cache_limit` to see the
        behaviour.

        This returns a `Metrics` object.

        Args:
            data (ModelData): The dataset to learn from.
            job_factories (Sequence[Callable[[Info], Job]]): A sequence of job factories
                to execute in the order in which they are given.
            max_iterations (int | None, optional): Maximum number of iterations.
                Defaults to None.
            n_chains (IntStrictlyPositive | None, optional): Batch size used. Defaults
                to None.
            warmup (IntNonNegative | None, optional): The number of iteration steps used
            in the warmup. Defaults to None.
            n_steps (IntStrictlyPositive | None, optional): The steps to do at each
                iteration; this is sub-sampling. Defaults to None.
            init_step_size (NumNonNegative, optional): Initial kernel step size in
                Metropolis Hastings. Defaults to 0.1.
            adapt_rate (NumNonNegative, optional): Adaptation rate for the step_size.
                The adaptation is done with the Robbins Monro algorithm in log scale.
                Defaults to 0.1.
            accept_target (NumProbability, optional): Acceptance target. Defaults to
                0.234.
            verbose (bool, optional): Whether or not to show progress. Defaults to True.

        Raises:
            TypeError: If some attribute is left unset.

        Returns:
            Metrics: The metrics.
        """
        # Load and complete data
        complete_data = CompleteModelData(
            data.x, data.t, data.y, data.trajectories, data.c, skip_validation=True
        )
        complete_data.prepare(self.model_design, self.params_)

        # Set up jobs and hyper-parameters.
        hyperparameters = self._get_hyperparameters(job_factories)
        if hyperparameters is not None:
            max_iterations = (
                hyperparameters["max_iterations"]
                if max_iterations is None
                else max_iterations
            )
            n_chains = hyperparameters["n_chains"] if n_chains is None else n_chains
            warmup = hyperparameters["warmup"] if warmup is None else warmup
            n_steps = hyperparameters["n_steps"] if n_steps is None else n_steps

        # Check everything is there
        for field in DEFAULT_HYPERPARAMETERS_FIELDS:
            if locals()[field] is None:
                raise TypeError(f"Missing required argument: '{field}'")

        # Set up MCMC
        sampler = self._setup_mcmc(
            complete_data,
            cast(int, n_chains),
            init_step_size,
            adapt_rate,
            accept_target,
        )
        for _ in range(cast(int, warmup)):
            sampler.step()

        # Initialize info
        info = Info(
            data=data,
            logpdfs_aux_fn=partial(self._logpdfs_aux_fn, data=complete_data),
            iteration=-1,
            model=self,
            sampler=sampler,
        )

        jobs = [job_factory(info) for job_factory in job_factories]

        # Main loop
        for _ in trange(
            cast(int, max_iterations), desc="Running joint model", disable=not verbose
        ):
            info.iteration += 1
            if run_jobs(jobs, info):
                break

            for _ in range(cast(int, n_steps)):
                sampler.step()

        # End things
        metrics = Metrics()

        info.iteration += 1
        for job in jobs:
            job.end(info=info, metrics=metrics)

        self._cache.clear_cache()
        return metrics

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def fit(
        self,
        data: ModelData,
        job_factories: Sequence[Callable[[Info], Job]] = (),
        *,
        max_iterations: int | None = None,
        n_chains: IntStrictlyPositive | None = None,
        warmup: IntNonNegative | None = None,
        n_steps: IntStrictlyPositive | None = None,
        init_step_size: NumNonNegative = 0.1,
        adapt_rate: NumNonNegative = 0.1,
        accept_target: NumProbability = 0.234,
        verbose: bool = True,
        opt_factory: type[torch.optim.Optimizer] | None = None,
        fit_extra: bool = True,
        **kwargs: Any,
    ) -> Metrics:
        """Fits the model and runs some jobs.

        Interally calls
        `do(data, [Fit(opt_factory, fit_extra, lr, **kwargs), *job_factories], ...)`.
        See `do` for more details.

        This sets the `fit_` attribute to True and the `data` attribute to the data
        provided. Metrics are stored in the `metrics_` attribute.

        Args:
            data (ModelData): The dataset to learn from.
            job_factories (Sequence[Callable[[Info], Fit]], optional): A sequence of job
                factories to execute in the order in which they are given. Defaults to
                ()
            max_iterations (int | None, optional): Maximum number of iterations.
                Defaults to None.
            n_chains (IntStrictlyPositive | None, optional): Batch size used. Defaults
                to None.
            warmup (IntNonNegative | None, optional): The number of iteration steps used
            in the warmup. Defaults to None.
            n_steps (IntStrictlyPositive | None, optional): The steps to do at each
                iteration; this is sub-sampling. Defaults to None.
            init_step_size (NumNonNegative, optional): Initial kernel step size in
                Metropolis Hastings. Defaults to 0.1.
            adapt_rate (NumNonNegative, optional): Adaptation rate for the step_size.
                The adaptation is done with the Robbins Monro algorithm in log scale.
                Defaults to 0.1.
            accept_target (NumProbability, optional): Acceptance target. Defaults to
                0.234.
            verbose (bool, optional): Whether or not to show progress. Defaults to True.
            opt_factory (type[torch.optim.Optimizer] | None, optional): The optimizer
                factory. Defaults to None.
            fit_extra (bool, optional): An option to fit extra parameters or not.
                Defaults to True.
            kwargs (Any): Additional kwargs passed to the optimizer factory, such as lr.

        Returns:
            Metrics: The metrics computed.
        """
        metrics = self.do(
            data,
            [Fit(opt_factory, fit_extra, **kwargs), *job_factories],
            max_iterations=max_iterations,
            n_chains=n_chains,
            warmup=warmup,
            n_steps=n_steps,
            init_step_size=init_step_size,
            adapt_rate=adapt_rate,
            accept_target=accept_target,
            verbose=verbose,
        )
        vars(self.metrics_).update(vars(metrics))

        return metrics

    def compute_summary(
        self,
        job_factories: Sequence[Callable[[Info], Job]] = (),
        *,
        max_iterations: int | None = None,
        n_chains: IntStrictlyPositive | None = None,
        warmup: IntNonNegative | None = None,
        n_steps: IntStrictlyPositive | None = None,
        init_step_size: NumNonNegative = 0.1,
        adapt_rate: NumNonNegative = 0.1,
        accept_target: NumProbability = 0.234,
        verbose: bool = True,
    ) -> Metrics:
        """Fits the model and runs some jobs.

        Interally calls
        `do(self.data, [ComputeFIM(), ComputeCriteria(), *job_factories], ...)`. See
        `do` for more details.

        Args:
            job_factories (Sequence[Callable[[Info], Job]], optional): A sequence of job
                factories to execute in the order in which they are given.
            max_iterations (int | None, optional): Maximum number of iterations.
                Defaults to None.
            n_chains (IntStrictlyPositive | None, optional): Batch size used. Defaults
                to None.
            warmup (IntNonNegative | None, optional): The number of iteration steps used
            in the warmup. Defaults to None.
            n_steps (IntStrictlyPositive | None, optional): The steps to do at each
                iteration; this is sub-sampling. Defaults to None.
            init_step_size (NumNonNegative, optional): Initial kernel step size in
                Metropolis Hastings. Defaults to 0.1.
            adapt_rate (NumNonNegative, optional): Adaptation rate for the step_size.
                The adaptation is done with the Robbins Monro algorithm in log scale.
                Defaults to 0.1.
            accept_target (NumProbability, optional): Acceptance target. Defaults to
                0.234.
            verbose (bool, optional): Whether or not to show progress. Defaults to True.

        Raises:
            ValueError: If self.data is None.

        Returns:
            Metrics: The metrics computed.
        """
        if self.data is None:
            raise ValueError("Data must be set before and seen during fitting")

        metrics = self.do(
            self.data,
            [ComputeFIM(), ComputeCriteria(), *job_factories],
            max_iterations=max_iterations,
            n_chains=n_chains,
            warmup=warmup,
            n_steps=n_steps,
            init_step_size=init_step_size,
            adapt_rate=adapt_rate,
            accept_target=accept_target,
            verbose=verbose,
        )
        vars(self.metrics_).update(vars(metrics))

        return metrics

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def sample_params(self, sample_size: IntNonNegative) -> list[ModelParams]:
        """Sample parameters based on asymptotic behavior of the MLE.

        Args:
            sample_size (IntNonNegative): The desired sample size.

        Returns:
            list[ModelParams]: A list of model parameters.
        """
        dist = torch.distributions.MultivariateNormal(
            self.params_.as_flat_tensor, self.fim.inverse()
        )
        flat_samples = dist.sample((sample_size,))

        return [self.params_.from_flat_tensor(sample) for sample in flat_samples]

    @property
    def fim(self) -> torch.Tensor:
        """Returns the Fisher Information Matrix.

        Raises:
            ValueError: If Fisher Information Matrix has not yet been computed.

        Returns:
            torch.Tensor: The Fisher Information Matrix.
        """
        if not hasattr(self.metrics_, "fim"):
            raise ValueError("Fisher Information Matrix must be previously computed.")

        return self.metrics_.fim

    @property
    def loglik(self) -> float:
        """Returns the log likelihood of the model.

        Returns:
            float: The log likelihood.
        """
        if not hasattr(self.metrics_, "loglik"):
            raise ValueError("Log likelihood must be previously computed.")

        return self.metrics_.loglik

    @property
    def nloglik_pen(self) -> float:
        """Returns the penalized negative log likelihood of the model.

        Returns:
            float: The penalized negative log likelihood.
        """
        if not hasattr(self.metrics_, "nloglik_pen"):
            raise ValueError(
                "Penalized negative log likelihood must be previously computed."
            )

        return self.metrics_.nloglik_pen

    @property
    def aic(self) -> float:
        """Returns the Akaike Information Criterion of the model.

        Returns:
            float: The Akaike Information Criterion.
        """
        if not hasattr(self.metrics_, "aic"):
            raise ValueError("AIC must be previously computed.")

        return self.metrics_.aic

    @property
    def bic(self) -> float:
        """Returns the Bayesian Information Criterion of the model.

        Returns:
            float: The Bayesian Information Criterion.
        """
        if not hasattr(self.metrics_, "bic"):
            raise ValueError("BIC must be previously computed.")

        return self.metrics_.bic

    @property
    def stderror(self) -> ModelParams:
        r"""Returns the standard error of the parameters.

        They can be used to draw confidence intervals. The standard errors are computed
        using the diagonal of the inverse of the inverse Fisher Information Matrix at
        the MLE:

        .. math::
            \text{sd} = \sqrt{\operatorname{diag}\bigl(\mathcal{I}(\hat{\theta})^{-1}
            \bigr)}

        Returns:
            ModelParams: The standard error in the same format as the parameters.
        """
        return self.params_.from_flat_tensor(self.fim.inverse().diag().sqrt())
