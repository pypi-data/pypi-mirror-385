import sympy

from copul.family.archimedean.biv_archimedean_copula import BivArchimedeanCopula
from copul.family.frechet.biv_independence_copula import BivIndependenceCopula


class Nelsen10(BivArchimedeanCopula):
    ac = BivArchimedeanCopula
    theta = sympy.symbols("theta", nonnegative=True)
    theta_interval = sympy.Interval(0, 1, left_open=False, right_open=False)
    special_cases = {0: BivIndependenceCopula}

    @property
    def is_absolutely_continuous(self) -> bool:
        return True

    @property
    def _raw_generator(self):
        return sympy.log(2 * self.t ** (-self.theta) - 1)

    @property
    def _raw_inv_generator(self):
        return (2 / (sympy.exp(self.y) + 1)) ** (1 / self.theta)

    @property
    def _cdf_expr(self):  # ToDo check why this differs from Nelsen cdf
        return (
            2
            * self.u**self.theta
            * self.v**self.theta
            / (
                self.u**self.theta * self.v**self.theta
                + (self.u**self.theta - 2) * (self.v**self.theta - 2)
            )
        ) ** (1 / self.theta)
