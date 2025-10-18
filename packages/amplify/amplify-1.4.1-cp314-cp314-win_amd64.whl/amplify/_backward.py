from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import NoReturn, overload

from typing_extensions import deprecated

from . import (
    AcceptableDegrees,
    Constraint,
    ConstraintList,
    Matrix,
    Model,
    PenaltyFormulation,
    Poly,
    PolyArray,
    QuadratizationMethod,
    Result,
    Values,
    VariableGenerator,
    solve,
    sum,
)

__all__ = [
    "BinaryIntMatrix",
    "BinaryIntPoly",
    "BinaryIntPolyArray",
    "BinaryIntQuadraticModel",
    "BinaryIntSymbolGenerator",
    "BinaryMatrix",
    "BinaryPoly",
    "BinaryPolyArray",
    "BinaryQuadraticModel",
    "BinarySymbolGenerator",
    "InequalityFormulation",
    "IsingIntMatrix",
    "IsingIntPoly",
    "IsingIntPolyArray",
    "IsingIntQuadraticModel",
    "IsingIntSymbolGenerator",
    "IsingMatrix",
    "IsingPoly",
    "IsingPolyArray",
    "IsingQuadraticModel",
    "IsingSymbolGenerator",
    "QuadraticModel",
    "Solver",
    "SolverResult",
    "SolverSolution",
    "SymbolGenerator",
    "convert_to_matrix",
    "decode_solution",
    "gen_symbols",
    "intersection",
    "pair_sum",
    "product",
    "replace_all",
    "sum_poly",
    "symmetric_difference",
    "union",
]


def _obsolete_warnings_msg(name: str, alt: str = "") -> str:
    return (
        name
        + " is obsolete and no longer supported since amplify v1.0.0.\n"
        + (f"Use {alt} instead. " if alt else "")
        + "Please see the migration guide for details: https://amplify.fixstars.com/docs/amplify/v1/migration.html"
    )


def _deprecation_warnings_msg(name: str, alt: str = "") -> str:
    return (
        name
        + " is deprecated since amplify v1.0.0 and will no longer support in the near future.\n"
        + (f"Use {alt} instead. " if alt else "")
        + "Please see the migration guide for details: https://amplify.fixstars.com/docs/amplify/v1/migration.html"
    )


class _NotImplemented:
    def __init__(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError(f"{type(self).__name__} is obsoleted and not implemented.")


@deprecated(_deprecation_warnings_msg("BinaryPoly", "Poly"))  # type: ignore
class BinaryPoly(Poly):
    """alias of :class:`~amplify.Poly`"""


@deprecated(_obsolete_warnings_msg("BinaryIntPoly", "Poly"))  # type: ignore
class BinaryIntPoly(_NotImplemented):
    pass


@deprecated(_deprecation_warnings_msg("IsingPoly", "Poly"))  # type: ignore
class IsingPoly(Poly):
    """alias of :class:`~amplify.Poly`"""


@deprecated(_obsolete_warnings_msg("IsingIntPoly", "Poly"))  # type: ignore
class IsingIntPoly(_NotImplemented):
    pass


@deprecated(_obsolete_warnings_msg("replace_all"))  # type: ignore
def replace_all(*args, **kwargs):
    raise NotImplementedError("replace_all is obsolete and not implemented.")


@deprecated(_deprecation_warnings_msg("sum_poly", "sum()"))  # type: ignore
def sum_poly(*args, **kwargs):
    return sum(*args, **kwargs)


@deprecated(_obsolete_warnings_msg("pair_sum"))  # type: ignore
def pair_sum(*args, **kwargs):
    raise NotImplementedError("pair_sum is obsolete and not implemented.")


@deprecated(_obsolete_warnings_msg("product"))  # type: ignore
def product(*args, **kwargs):
    raise NotImplementedError("product is obsolete and not implemented.")


@deprecated(_obsolete_warnings_msg("intersection"))  # type: ignore
def intersection(*args, **kwargs):
    raise NotImplementedError("intersection is obsolete and not implemented.")


@deprecated(_obsolete_warnings_msg("union"))  # type: ignore
def union(*args, **kwargs):
    raise NotImplementedError("union is obsolete and not implemented.")


@deprecated(_obsolete_warnings_msg("symmetric_difference"))  # type: ignore
def symmetric_difference(*args, **kwargs):
    raise NotImplementedError("symmetric_difference is obsolete and not implemented.")


@deprecated(_deprecation_warnings_msg("BinaryPolyArray", "PolyArray"))  # type: ignore
class BinaryPolyArray(PolyArray):
    pass


@deprecated(_obsolete_warnings_msg("BinaryIntPolyArray", "PolyArray"))  # type: ignore
class BinaryIntPolyArray(_NotImplemented):
    pass


@deprecated(_deprecation_warnings_msg("IsingPolyArray", "PolyArray"))  # type: ignore
class IsingPolyArray(PolyArray):
    pass


@deprecated(_obsolete_warnings_msg("IsingIntPolyArray", "PolyArray"))  # type: ignore
class IsingIntPolyArray(_NotImplemented):
    pass


@deprecated(_deprecation_warnings_msg("BinarySymbolGenerator", "VariableGenerator"))  # type: ignore
class BinarySymbolGenerator:
    def __init__(self):
        self._gen = VariableGenerator()

    def array(self, *args, **kwargs):
        return self._gen.array("Binary", *args, **kwargs)

    def scalar(self, *args, **kwargs):
        return self._gen.scalar("Binary", *args, **kwargs)

    def matrix(self, *args, **kwargs):
        return self._gen.matrix("Binary", *args, **kwargs)

    @property
    def variables(self):
        return self._gen.variables


@deprecated(_obsolete_warnings_msg("BinaryIntSymbolGenerator", "VariableGenerator"))  # type: ignore
class BinaryIntSymbolGenerator(_NotImplemented):
    pass


@deprecated(_deprecation_warnings_msg("IsingSymbolGenerator", "VariableGenerator"))  # type: ignore
class IsingSymbolGenerator:
    def __init__(self):
        self._gen = VariableGenerator()

    def array(self, *args, **kwargs):
        return self._gen.array("Ising", *args, **kwargs)

    def scalar(self, *args, **kwargs):
        return self._gen.scalar("Ising", *args, **kwargs)

    def matrix(self, *args, **kwargs):
        return self._gen.matrix("Ising", *args, **kwargs)

    @property
    def variables(self):
        return self._gen.variables


@deprecated(_obsolete_warnings_msg("IsingIntSymbolGenerator", "VariableGenerator"))  # type: ignore
class IsingIntSymbolGenerator(_NotImplemented):
    pass


@deprecated(_deprecation_warnings_msg("SymbolGenerator", "VariableGenerator"))  # type: ignore
def SymbolGenerator(arg=None) -> VariableGenerator | BinarySymbolGenerator | IsingSymbolGenerator:  # noqa: N802
    if arg is None:
        return VariableGenerator()
    if arg is BinaryPoly:
        return BinarySymbolGenerator()
    if arg is IsingPoly:
        return IsingSymbolGenerator()
    raise TypeError(f"SymbolGenerator does not support {arg}.")


@deprecated(_obsolete_warnings_msg("gen_symbols"))  # type: ignore
def gen_symbols(*args, **kwargs):
    raise NotImplementedError("gen_symbols is obsolete and not implemented.")


@deprecated(_obsolete_warnings_msg("decode_solution"))  # type: ignore
def decode_solution(
    array: PolyArray,
    solution: Values,
):
    return array.evaluate(solution)


@deprecated(_deprecation_warnings_msg("BinaryMatrix", "Matrix"))  # type: ignore
class BinaryMatrix(Matrix):
    pass


@deprecated(_obsolete_warnings_msg("BinaryIntMatrix", "Matrix"))  # type: ignore
class BinaryIntMatrix(_NotImplemented):
    pass


@deprecated(_deprecation_warnings_msg("IsingMatrix", "Matrix"))  # type: ignore
class IsingMatrix(Matrix):
    pass


@deprecated(_obsolete_warnings_msg("IsingIntMatrix", "Matrix"))  # type: ignore
class IsingIntMatrix(_NotImplemented):
    pass


@deprecated(_obsolete_warnings_msg("convert_to_matrix"))  # type: ignore
def convert_to_matrix(*args, **kwargs):
    raise NotImplementedError("convert_to_matrix is obsolete and not implemented.")


class QuadraticModel(ABC):
    @overload
    def __init__(
        self,
        arg0: Poly,
        arg1: Constraint | ConstraintList | None = None,
        *,
        method: QuadratizationMethod = QuadratizationMethod.IshikawaKZFD,
    ): ...

    @overload
    def __init__(
        self,
        arg0: Matrix,
        arg1: Constraint | ConstraintList | None = None,
        *,
        method: QuadratizationMethod = QuadratizationMethod.IshikawaKZFD,
    ): ...

    @overload
    def __init__(self, arg0: Model, arg1=None, *, method: QuadratizationMethod = QuadratizationMethod.IshikawaKZFD): ...

    @overload
    def __init__(
        self,
        arg0: Constraint | ConstraintList,
        arg1=None,
        *,
        method: QuadratizationMethod = QuadratizationMethod.IshikawaKZFD,
    ): ...

    def __init__(
        self,
        arg0,
        arg1=None,
        *,
        method: QuadratizationMethod = QuadratizationMethod.IshikawaKZFD,
    ):
        if isinstance(arg0, Model):
            self._model = arg0
        elif arg1 is None:
            self._model = Model(arg0)
        else:
            self._model = Model(arg0, arg1)

        self._method = method
        self._substitution_multiplier = 1.0
        self.__intermediate_model: Model | None = None
        self._intermediate_poly: Poly | None = None
        self._intermediate_mapping: Result.ModelConversion.IntermediateMapping | None = None

    def __add__(self, arg: Constraint | ConstraintList):
        return self.__class__(self._model + arg)  # type: ignore

    def __iadd__(self, arg: Constraint | ConstraintList):
        self._model += arg
        return self

    def __radd__(self, arg: Constraint | ConstraintList):
        return self.__class__(arg + self._model)  # type: ignore

    @property
    def substitution_multiplier(self) -> float:
        return self._substitution_multiplier

    @substitution_multiplier.setter
    def substitution_multiplier(self, value: float):
        if not isinstance(value, float) or value <= 0:
            raise ValueError("substitution_multiplier must be positive float.")
        self._substitution_multiplier = value

    @property
    def input_constraints(self) -> ConstraintList:
        return self._model.constraints

    @property
    def input_matrix(self) -> Matrix | None:
        if isinstance(self._model.objective, Matrix):
            return self._model.objective
        return None

    @property
    def input_poly(self) -> Poly | None:
        if isinstance(self._model.objective, Poly):
            return self._model.objective
        return None

    @classmethod
    @abstractmethod
    def _intermediate_degrees(cls) -> AcceptableDegrees:
        pass

    def _intermediate_model(self):
        if self.__intermediate_model is None or self._intermediate_mapping is None or self._intermediate_poly is None:
            self.__intermediate_model, self._intermediate_mapping = self._model.to_intermediate_model(
                self._intermediate_degrees(), substitution_multiplier=self._substitution_multiplier
            )
            self._intermediate_poly = self.__intermediate_model.to_unconstrained_poly()
        return self.__intermediate_model, self._intermediate_mapping, self._intermediate_poly

    @property
    def logical_mapping(self) -> Result.ModelConversion.IntermediateMapping:
        return self._intermediate_model()[1]

    @property
    def logical_matrix(self) -> Matrix | None:
        objective = self._intermediate_model()[0].objective
        if isinstance(objective, Matrix):
            return objective
        return None

    @property
    @deprecated(_obsolete_warnings_msg("Model.logical_model_matrix"))  # type: ignore
    def logical_model_matrix(self):
        raise NotImplementedError("Model.logical_model_matrix is obsolete and not implemented.")

    @property
    def logical_model_poly(self) -> Poly:
        return self._intermediate_model()[2]

    @property
    def logical_poly(self) -> Poly | None:
        objective = self._intermediate_model()[0].objective
        if isinstance(objective, Poly):
            return objective
        return None

    @property
    def num_input_vars(self) -> int:
        return len(self._model.variables)

    @property
    def num_logical_vars(self) -> int:
        return len(self._intermediate_model()[0].get_variables(True))

    def check_constraints(self, values: Values) -> list[tuple[Constraint, bool]]:
        return [(c, c.is_satisfied(values)) for c in self.input_constraints]


@deprecated(_deprecation_warnings_msg("BinaryQuadraticModel", "Model"))  # type: ignore
class BinaryQuadraticModel(QuadraticModel):
    @classmethod
    def _intermediate_degrees(cls) -> AcceptableDegrees:
        return AcceptableDegrees(objective={"Binary": "Quadratic"})


@deprecated(_obsolete_warnings_msg("BinaryIntQuadraticModel", "Model"))  # type: ignore
class BinaryIntQuadraticModel(_NotImplemented):
    pass


@deprecated(_deprecation_warnings_msg("IsingQuadraticModel", "Model"))  # type: ignore
class IsingQuadraticModel(QuadraticModel):
    @classmethod
    def _intermediate_degrees(cls) -> AcceptableDegrees:
        return AcceptableDegrees(objective={"Ising": "Quadratic"})


@deprecated(_obsolete_warnings_msg("IsingIntQuadraticModel", "Model"))  # type: ignore
class IsingIntQuadraticModel(_NotImplemented):
    pass


@deprecated(_deprecation_warnings_msg("SolverSolution"))  # type: ignore
class SolverSolution:
    def __init__(self, energy, is_feasible, values):
        self._energy = energy
        self._is_feasible = is_feasible
        self._values = values

    @property
    def energy(self):
        return self._energy

    @property
    @deprecated(_deprecation_warnings_msg("SolverSolution.frequency"))  # type: ignore
    def frequency(self):
        return 1

    @property
    def is_feasible(self):
        return self._is_feasible

    @property
    def values(self):
        return self._values


@deprecated(_deprecation_warnings_msg("SolverResult"))  # type: ignore
class SolverResult(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def solutions(self) -> list[SolverSolution]:
        return list(self)


@deprecated(_deprecation_warnings_msg("Solver", "solve()"))  # type: ignore
class Solver:
    def __init__(self, client):
        self._client = client
        self._chain_strength = 1.0
        self._client_result = None
        self._embedding_time_limit = 10
        self._execution_time = None
        self._filter_solution = True
        self._logical_result = None
        self._sort_solution = True

    def solve(self, arg) -> SolverResult:
        result = solve(
            arg._model if isinstance(arg, QuadraticModel) else arg,  # noqa: SLF001
            self._client,
            embedding_timeout=self._embedding_time_limit,
            chain_strength=self._chain_strength,
            filter_solution=self._filter_solution,
            sort_solution=self._sort_solution,
        )
        self._client_result = result.client_result
        self._execution_time = result.execution_time
        self._logical_result = result.intermediate.values_list

        return SolverResult([
            SolverSolution(solution.objective, solution.feasible, solution.values) for solution in result
        ])

    @property
    def chain_strength(self):
        return self._chain_strength

    @chain_strength.setter
    def chain_strength(self, value: float):
        self._chain_strength = value

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    @property
    def client_result(self):
        return self._client_result

    @property
    @deprecated(_obsolete_warnings_msg("Solver.deduplicate"))  # type: ignore
    def deduplicate(self):
        raise NotImplementedError("Solver.deduplicate is obsolete and not implemented.")

    @deduplicate.setter
    @deprecated(_obsolete_warnings_msg("Solver.deduplicate"))  # type: ignore
    def deduplicate(self, value):
        raise NotImplementedError("Solver.deduplicate is obsolete and not implemented.")

    @property
    def embedding_time_limit(self):
        return self._embedding_time_limit

    @embedding_time_limit.setter
    def embedding_time_limit(self, value):
        self._embedding_time_limit = value

    @property
    def execution_time(self):
        return self._execution_time

    @property
    def filter_solution(self):
        return self._filter_solution

    @filter_solution.setter
    def filter_solution(self, value):
        self._filter_solution = value

    @property
    def logical_result(self):
        return self._logical_result

    @property
    def sort_solution(self):
        return self._sort_solution

    @sort_solution.setter
    def sort_solution(self, value):
        self._sort_solution = value


@deprecated(_deprecation_warnings_msg("InequalityFormulation", "IntegerEncodingMethod and PenaltyFormulation"))  # type: ignore
class InequalityFormulation(Enum):
    Default = PenaltyFormulation.Default
    Unary = PenaltyFormulation.Default  # noqa: PIE796
    Binary = PenaltyFormulation.Default  # noqa: PIE796
    Linear = PenaltyFormulation.Default  # noqa: PIE796
    Relaxation = PenaltyFormulation.Relaxation
    RelaxationLinear = PenaltyFormulation.LinearRelaxation
    RelaxationQuadra = PenaltyFormulation.QuadraticRelaxation
