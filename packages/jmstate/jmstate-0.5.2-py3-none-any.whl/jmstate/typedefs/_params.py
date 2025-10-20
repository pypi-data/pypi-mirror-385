from dataclasses import field
from functools import cached_property
from itertools import chain
from typing import Any, Self, cast

import torch
from numpy import array2string
from pydantic import ConfigDict, dataclasses, validate_call
from rich.tree import Tree

from ..utils._checks import check_inf, check_matrix_dim, check_nan
from ..utils._dtype import get_dtype
from ..utils._linalg import cov_from_repr
from ..utils._misc import map_fn_params
from ..visualization._print import rich_str
from ._defs import MatRepr, Tensor1D


@dataclasses.dataclass(config=ConfigDict(arbitrary_types_allowed=True), frozen=True)
class ModelParams:
    r"""Dataclass containing model parameters.

    Note three types of covariance matrices parametrization are provided: scalar
    matrix; diagonal matrix; full matrix. Defaults to the full matrix parametrization.
    This is achieved through a log Cholesky parametrization of the inverse covariance
    matrix. Formally, consider :math:`P = \Sigma^{-1}` the precision matrix and let
    :math:`L` be the Cholesky factor with positive diagonal elements, the log Cholseky
    is given by:

    .. math::
        \tilde{L}_{ij} = L_{ij}, \, i > j,

    and:

    .. math::
        \tilde{L}_{ii} = \log L_{ii}.

    This is very numerically stable and fast, as it doesn't require inverting the
    matrix when computing quadratic forms. The log determinant is then equal to:

    .. math::

        \log \det P = 2 \operatorname{Tr}(\tilde{L}).

    You can use these methods by creating the appropriate `MatRepr` with methods of
    `ball`, `diag` or `full`.

    Additionnally, if your data has mixed missing values, do not use `full` matrix
    parametrization for the residuals, as is this case the components must be
    independent.

    Bypass checks by activating the `skip_validation` flag.

    Attributes:
        gamma (Tensor1D | None): The population level parameters.
        Q_repr (MatRepr): The random effects precision matrix representation.
        R_repr (MatRepr): The residuals precision matrix representation.
        alphas (dict[tuple[Any, Any], Tensor1D]) The link linear parameters.
        betas (dict[tuple[Any, Any], Tensor1D] | None): The covariates parameters.
        extra (list[torch.Tensor] | None): A list of parameters that is passed in
            addition to other mandatory parameters.
        skip_validation (bool): A boolean value to skip validation.
    """

    gamma: Tensor1D | None
    Q_repr: MatRepr
    R_repr: MatRepr
    alphas: dict[tuple[Any, Any], Tensor1D]
    betas: dict[tuple[Any, Any], Tensor1D] | None
    extra: list[torch.Tensor] | None = field(default=None, repr=False)
    skip_validation: bool = field(default=False, repr=False)

    def __str__(self) -> str:
        """Return a string representation of the model parameters.

        Returns:
            str: The string representation.
        """

        def _to_str(t: torch.Tensor) -> str:
            return array2string(t.numpy(), precision=3, suppress_small=True)

        tree = Tree("ModelParams")
        if self.gamma is not None:
            tree.add(f"gamma: {_to_str(self.gamma)}")
        tree.add(f"Q: {_to_str(self.Q_repr.flat)}")
        tree.add(f"R: {_to_str(self.R_repr.flat)}")
        alphas = tree.add("alphas:")
        for k, v in self.alphas.items():
            alphas.add(f"{k[0]} --> {k[1]}: {_to_str(v)}")
        if self.betas is not None:
            betas = tree.add("betas:")
            for k, v in self.betas.items():
                betas.add(f"{k[0]} --> {k[1]}: {_to_str(v)}")

        return rich_str(tree)

    def __post_init__(self):
        """Validate and put to dtype all tensors.

        Raises:
            ValueError: If any of the tensors contains inf values.
            ValueError: If any of the tensors contains NaN values.
        """
        if self.skip_validation:
            return

        def _sort_dict(
            dct: dict[tuple[Any, Any], torch.Tensor],
        ) -> dict[tuple[Any, Any], torch.Tensor]:
            return dict(sorted(dct.items(), key=lambda kv: str(kv[0])))

        # For reproducibility purposes and order
        object.__setattr__(self, "alphas", _sort_dict(self.alphas))
        if self.betas is not None:
            object.__setattr__(self, "betas", _sort_dict(self.betas))

        dtype = get_dtype()

        for t in self.as_list:
            t.data = t.to(dtype)
        if self.extra is not None:
            for t in self.extra:
                t.data = t.to(dtype)

        check_matrix_dim(self.Q_repr, "Q")
        check_matrix_dim(self.R_repr, "R")
        for key, val in self.as_dict.items():
            if isinstance(val, dict):
                tensor_tuple = tuple((t, key) for t in val.values())
                check_inf(tensor_tuple)
                check_nan(tensor_tuple)
            else:
                check_inf(((val, key),))
                check_nan(((val, key),))

    @cached_property
    def as_dict(self) -> dict[str, torch.Tensor | dict[tuple[Any, Any], torch.Tensor]]:
        """Gets a grouped dict of all the parameters.

        Returns:
            dict[str, torch.Tensor | dict[tuple[Any, Any], torch.Tensor]]: The dict of
                the parameters.
        """
        groups = {
            "gamma": self.gamma,
            "Q": self.Q_repr.flat,
            "R": self.R_repr.flat,
            "alphas": self.alphas,
            "betas": None if self.betas is None else self.betas,
        }
        return {key: val for key, val in groups.items() if val is not None}

    @cached_property
    def as_list(self) -> list[torch.Tensor]:
        """Gets a list of all the unique parameters.

        Returns:
            list[torch.Tensor]: The list of the (unique) parameters.
        """
        seen: set[torch.Tensor] = set()
        _is_new = lambda x: not (x in seen or seen.add(x))  # noqa: E731  # type: ignore

        def _items(
            v: torch.Tensor | dict[tuple[Any, Any], torch.Tensor],
        ) -> list[torch.Tensor]:
            if isinstance(v, torch.Tensor):
                return [v] if _is_new(v) else []
            return [t for t in v.values() if _is_new(t)]

        return list(chain.from_iterable(_items(v) for v in self.as_dict.values()))

    @cached_property
    def as_named_list(self) -> list[tuple[str, torch.Tensor]]:
        """Gets a list of all the unique parameters names and values.

        Returns:
            list[tuple[str, torch.Tensor]]: The list of the (unique) parameters names
                and values.
        """
        seen: set[torch.Tensor] = set()
        _is_new = lambda x: not (x in seen or seen.add(x))  # noqa: E731  # type: ignore

        def _items(
            k: str, v: torch.Tensor | dict[tuple[Any, Any], torch.Tensor]
        ) -> list[tuple[str, torch.Tensor]]:
            if isinstance(v, torch.Tensor):
                return [(k, v)] if _is_new(v) else []
            return [(f"{k}[{sk}]", sv) for sk, sv in v.items() if _is_new(sv)]

        return list(chain.from_iterable(_items(k, v) for k, v in self.as_dict.items()))

    @property
    def as_flat_tensor(self) -> Tensor1D:
        """Get the flattened unique parameters.

        Returns:
            torch.Tensor: The flattened (unique) parameters.
        """
        return torch.cat([p.reshape(-1) for p in self.as_list])

    @cached_property
    def numel(self) -> int:
        """Return the number of unique parameters.

        Returns:
            int: The number of the (unique) parameters.
        """
        return sum(p.numel() for p in self.as_list)

    def requires_grad_(self, req: bool):
        """Enable or disable gradient computation on non extra parameters.

        Args:
            req (bool): Wether to require or not.
        """
        for t in self.as_list:
            t.requires_grad_(req)

    def extra_requires_grad_(self, req: bool):
        """Enable or disable gradient computation on extra parameters.

        Args:
            req (bool): Wether to require or not.
        """
        if self.extra is None:
            return
        for t in self.extra:
            t.requires_grad_(req)

    def get_cov(self, matrix: str) -> torch.Tensor:
        """Get covariance from parameter.

        Args:
            matrix (str): Either "Q" or "R".

        Raises:
            ValueError: If the matrix is not in ("Q", "R")

        Returns:
            torch.Tensor: The covariance matrix.
        """
        if matrix not in ("Q", "R"):
            raise ValueError(f"matrix must be either Q or R, got {matrix}")

        # Get repr then covariance
        return cov_from_repr(getattr(self, matrix + "_repr"))

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def from_flat_tensor(self, flat: Tensor1D) -> Self:
        """Gets a ModelParams object based on the flat representation.

        This uses the current object as the reference.

        Args:
            flat (torch.Tensor): The flat representation.

        Returns:
            Self The constructed ModelParams.
        """
        seen: dict[torch.Tensor, torch.Tensor] = {}
        i = 0

        def _next(ref: torch.Tensor):
            nonlocal seen, i
            if ref in seen:
                return seen[ref]

            n = ref.numel()
            result = flat[i : i + n]
            i += n
            seen[ref] = result.reshape(ref.shape)

            return seen[ref]

        return cast(Self, map_fn_params(self, _next))

    def detach(self) -> Self:
        """Returns a detached reshape of the parameters.

        Returns:
            Self The detached reshape.
        """
        return cast(Self, map_fn_params(self, torch.detach))

    def clone(self) -> Self:
        """Returns a clone of the parameters.

        Returns:
            Self The clone.
        """
        seen: dict[torch.Tensor, torch.Tensor] = {}

        def _next(t: torch.Tensor):
            nonlocal seen
            if t not in seen:
                seen[t] = t.clone()

            return seen[t]

        return cast(Self, map_fn_params(self, _next))
