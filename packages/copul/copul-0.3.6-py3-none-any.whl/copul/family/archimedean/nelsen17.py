import numpy as np
import sympy

from copul.family.archimedean.biv_archimedean_copula import BivArchimedeanCopula
from copul.family.frechet.biv_independence_copula import BivIndependenceCopula
from copul.wrapper.sympy_wrapper import SymPyFuncWrapper


class Nelsen17(BivArchimedeanCopula):
    ac = BivArchimedeanCopula
    theta_interval = sympy.Interval(-np.inf, np.inf, left_open=True, right_open=True)
    special_cases = {-1: BivIndependenceCopula}
    invalid_params = {0}

    @property
    def is_absolutely_continuous(self) -> bool:
        return True

    @property
    def _raw_generator(self):
        return -sympy.log(
            ((1 + self.t) ** (-self.theta) - 1) / (2 ** (-self.theta) - 1)
        )

    @property
    def _raw_inv_generator(self):
        theta = self.theta
        y = self.y
        return (2**theta * sympy.exp(y) / (2**theta * sympy.exp(y) - 2**theta + 1)) ** (
            1 / theta
        ) - 1

    @property
    def _cdf_expr(self):
        v = self.v
        u = self.u
        theta = self.theta
        return (
            1
            + ((1 + u) ** (-theta) - 1)
            * ((1 + v) ** (-theta) - 1)
            / (2 ** (-theta) - 1)
        ) ** (-1 / theta) - 1

    @property
    def pdf(self):
        theta = self.theta
        u = self.u
        v = self.v
        pdf = (
            2**theta
            * theta
            * (
                -(2**theta) * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                + (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
            )
            ** 2
            + 4**theta
            * (theta + 1)
            * (
                -(2**theta) * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                + ((u + 1) * (v + 1)) ** theta * (2**theta - 1)
            )
            * ((u + 1) ** theta - 1)
            * ((v + 1) ** theta - 1)
        ) / (
            (
                (
                    -(2**theta) * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    + (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                )
                / ((2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta)
            )
            ** (1 / theta)
            * (u + 1)
            * (v + 1)
            * (
                -(2**theta) * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                + (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
            )
            ** 3
        )
        return SymPyFuncWrapper(pdf)

    @property
    def first_deriv_of_inv_gen(self):
        theta = self.theta
        y = self.y
        return sympy.simplify(
            (2**theta * sympy.exp(y) / (2**theta * sympy.exp(y) - 2**theta + 1))
            ** (1 / theta)
            * (2**theta * (-(2**theta) + 1))
            / (2**theta * theta * (2**theta * sympy.exp(y) - 2**theta + 1))
        )

    @property
    def second_deriv_of_inv_gen(self):
        theta = self.theta
        y = self.y
        return sympy.simplify(
            (2**theta * sympy.exp(y) / (2**theta * sympy.exp(y) - 2**theta + 1))
            ** (1 / theta)
            * (
                2**theta * theta * (-(2**theta) + 1) * sympy.exp(y)
                - 2 ** (theta + 1) * theta * (-(2**theta) + 1) * sympy.exp(y)
                + (2**theta - 1) ** 2
            )
            / (theta**2 * (2**theta * sympy.exp(y) - 2**theta + 1) ** 2)
        )

    @property
    def first_deriv_of_ci_char(self):
        theta = self.theta
        y = self.y
        return sympy.simplify(
            (2**theta * (-(2**theta) + 1) - 4**theta * theta * sympy.exp(y))
            / (2**theta * theta * (2**theta * sympy.exp(y) - 2**theta + 1))
        )

    def first_deriv_of_tp2_char(self):
        theta = self.theta
        y = self.y
        a = 2**theta * sympy.exp(y) - 2**theta + 1
        b = 2**theta * theta * sympy.exp(y) + 2**theta - 1
        return (
            2**theta * theta**2 * a * sympy.exp(y)
            - 2 ** (theta + 1) * theta * b * sympy.exp(y)
            + (1 - 2**theta) * b
        ) / (theta * a * b)

    def second_deriv_of_tp2_char(self):
        theta = self.theta
        y = self.y
        a = 2**theta * sympy.exp(y) - 2**theta + 1
        b = 2**theta * theta * sympy.exp(y) + 2**theta - 1
        numerator = (
            (2**theta - 1) * theta**2 * a**2
            + 2**theta * b**2
            + 2 ** (theta + 1) * theta * b**2
            - theta**2 * a**2
            - 2 * theta * b**2
            - b**2
        )
        # sub_expr = a**2 * theta**2 + (1 + 2 * theta) * b**2
        # ey_part = (
        #     2 * 2 ** (2 * theta) * theta**3 * sympy.exp(2 * y)
        #     + 2 * 2 ** (2 * theta) * theta**2 * sympy.exp(2 * y)
        #     + 2 * 2 ** (2 * theta) * theta**2 * sympy.exp(y)
        #     + 2 * 2 ** (2 * theta) * theta * sympy.exp(y)
        #     - 2 * 2**theta * theta**2 * sympy.exp(y)
        #     - 2 * 2**theta * theta * sympy.exp(y)
        # )
        # ey_critical = (
        #         2**theta * theta**2 * sympy.exp(y)
        #         + 2**theta * theta * sympy.exp(y)
        #         + 2**theta * theta
        #         + 2**theta
        #         - theta
        #         - 1
        # )
        # numerator = (2**theta - 1)(sub_expr)
        return 2**theta * numerator * sympy.exp(y) / (theta * a**2 * b**2)

    def deriv_of_log_density(self):
        theta = self.theta
        u = self.u
        v = self.v
        return (
            -3
            * theta
            * (
                ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
            )
            * (
                2**theta
                * theta
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                )
                ** 2
                - 4**theta
                * (theta + 1)
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                )
                * ((u + 1) ** theta - 1)
                * ((v + 1) ** theta - 1)
            )
            - (
                2**theta
                * theta
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                )
                ** 2
                - 4**theta
                * (theta + 1)
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                )
                * ((u + 1) ** theta - 1)
                * ((v + 1) ** theta - 1)
            )
            * (
                -(2**theta) * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                + ((u + 1) * (v + 1)) ** theta * (2**theta - 1)
                + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
            )
            - (
                2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
            )
            * (
                2**theta
                * theta
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                )
                ** 2
                - 2 ** (theta + 1)
                * theta**2
                * (
                    ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                )
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                )
                + 4**theta
                * theta
                * (theta + 1)
                * (
                    ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                )
                * ((u + 1) ** theta - 1)
                * ((v + 1) ** theta - 1)
                - 4**theta
                * (theta + 1)
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                )
                * ((u + 1) ** theta - 1)
                * ((v + 1) ** theta - 1)
                + theta
                * (theta + 1)
                * (4 * u + 4) ** theta
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                )
                * ((v + 1) ** theta - 1)
            )
        ) / (
            (u + 1)
            * (
                2**theta
                * theta
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                )
                ** 2
                - 4**theta
                * (theta + 1)
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    - ((u + 1) * (v + 1)) ** theta * (2**theta - 1)
                )
                * ((u + 1) ** theta - 1)
                * ((v + 1) ** theta - 1)
            )
            * (
                2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
            )
        )

    def density_of_log_density(self):
        theta = self.theta
        v = self.v
        u = self.u
        return (
            (
                -3
                * theta
                * (
                    ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                )
                * (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    * (
                        2
                        * 2**theta
                        * theta
                        * (v + 1) ** theta
                        * ((u + 1) ** theta - 1)
                        / (v + 1)
                        - 2
                        * theta
                        * (2**theta - 1)
                        * (u + 1) ** theta
                        * (v + 1) ** theta
                        / (v + 1)
                    )
                    - 4**theta
                    * theta
                    * (theta + 1)
                    * (v + 1) ** theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((u + 1) ** theta - 1)
                    / (v + 1)
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta
                        * theta
                        * (v + 1) ** theta
                        * ((u + 1) ** theta - 1)
                        / (v + 1)
                        + theta
                        * ((u + 1) * (v + 1)) ** theta
                        * (1 - 2**theta)
                        / (v + 1)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                )
                - 3
                * theta
                * (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    ** 2
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                )
                * (
                    theta * ((u + 1) * (v + 1)) ** theta * (1 - 2**theta) / (v + 1)
                    + theta * (2 * u + 2) ** theta * (v + 1) ** theta / (v + 1)
                )
                - (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    ** 2
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                )
                * (
                    -(2**theta)
                    * theta
                    * (v + 1) ** theta
                    * ((u + 1) ** theta - 1)
                    / (v + 1)
                    + theta * ((u + 1) * (v + 1)) ** theta * (1 - 2**theta) / (v + 1)
                    + theta * ((u + 1) * (v + 1)) ** theta * (2**theta - 1) / (v + 1)
                    + theta * (2 * u + 2) ** theta * (v + 1) ** theta / (v + 1)
                )
                - (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                )
                * (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    * (
                        2
                        * 2**theta
                        * theta
                        * (v + 1) ** theta
                        * ((u + 1) ** theta - 1)
                        / (v + 1)
                        - 2
                        * theta
                        * (2**theta - 1)
                        * (u + 1) ** theta
                        * (v + 1) ** theta
                        / (v + 1)
                    )
                    - 2 ** (theta + 1)
                    * theta**2
                    * (
                        ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                        + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                    )
                    * (
                        2**theta
                        * theta
                        * (v + 1) ** theta
                        * ((u + 1) ** theta - 1)
                        / (v + 1)
                        + theta
                        * ((u + 1) * (v + 1)) ** theta
                        * (1 - 2**theta)
                        / (v + 1)
                    )
                    - 2 ** (theta + 1)
                    * theta**2
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * (
                        theta * ((u + 1) * (v + 1)) ** theta * (1 - 2**theta) / (v + 1)
                        + theta * (2 * u + 2) ** theta * (v + 1) ** theta / (v + 1)
                    )
                    + 4**theta
                    * theta**2
                    * (theta + 1)
                    * (v + 1) ** theta
                    * (
                        ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                        + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                    )
                    * ((u + 1) ** theta - 1)
                    / (v + 1)
                    + 4**theta
                    * theta
                    * (theta + 1)
                    * (
                        theta * ((u + 1) * (v + 1)) ** theta * (1 - 2**theta) / (v + 1)
                        + theta * (2 * u + 2) ** theta * (v + 1) ** theta / (v + 1)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                    - 4**theta
                    * theta
                    * (theta + 1)
                    * (v + 1) ** theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((u + 1) ** theta - 1)
                    / (v + 1)
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta
                        * theta
                        * (v + 1) ** theta
                        * ((u + 1) ** theta - 1)
                        / (v + 1)
                        + theta
                        * ((u + 1) * (v + 1)) ** theta
                        * (1 - 2**theta)
                        / (v + 1)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                    + theta**2
                    * (theta + 1)
                    * (4 * u + 4) ** theta
                    * (v + 1) ** theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    / (v + 1)
                    + theta
                    * (theta + 1)
                    * (4 * u + 4) ** theta
                    * (
                        2**theta
                        * theta
                        * (v + 1) ** theta
                        * ((u + 1) ** theta - 1)
                        / (v + 1)
                        + theta
                        * ((u + 1) * (v + 1)) ** theta
                        * (1 - 2**theta)
                        / (v + 1)
                    )
                    * ((v + 1) ** theta - 1)
                )
                - (
                    2**theta
                    * theta
                    * (v + 1) ** theta
                    * ((u + 1) ** theta - 1)
                    / (v + 1)
                    + theta * ((u + 1) * (v + 1)) ** theta * (1 - 2**theta) / (v + 1)
                )
                * (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    ** 2
                    - 2 ** (theta + 1)
                    * theta**2
                    * (
                        ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                        + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                    )
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    + 4**theta
                    * theta
                    * (theta + 1)
                    * (
                        ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                        + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                    + theta
                    * (theta + 1)
                    * (4 * u + 4) ** theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((v + 1) ** theta - 1)
                )
                - (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    * (
                        2
                        * 2**theta
                        * theta
                        * (v + 1) ** theta
                        * ((u + 1) ** theta - 1)
                        / (v + 1)
                        - 2
                        * theta
                        * (2**theta - 1)
                        * (u + 1) ** theta
                        * (v + 1) ** theta
                        / (v + 1)
                    )
                    - 4**theta
                    * theta
                    * (theta + 1)
                    * (v + 1) ** theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((u + 1) ** theta - 1)
                    / (v + 1)
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta
                        * theta
                        * (v + 1) ** theta
                        * ((u + 1) ** theta - 1)
                        / (v + 1)
                        + theta
                        * ((u + 1) * (v + 1)) ** theta
                        * (1 - 2**theta)
                        / (v + 1)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                )
                * (
                    -(2**theta) * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    + ((u + 1) * (v + 1)) ** theta * (2**theta - 1)
                    + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                )
            )
            / (
                (u + 1)
                * (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    ** 2
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - ((u + 1) * (v + 1)) ** theta * (2**theta - 1)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                )
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                )
            )
            + (
                -(2**theta)
                * theta
                * (v + 1) ** theta
                * ((u + 1) ** theta - 1)
                / (v + 1)
                + theta * (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta / (v + 1)
            )
            * (
                -3
                * theta
                * (
                    ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                )
                * (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    ** 2
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                )
                - (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    ** 2
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                )
                * (
                    -(2**theta) * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    + ((u + 1) * (v + 1)) ** theta * (2**theta - 1)
                    + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                )
                - (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                )
                * (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    ** 2
                    - 2 ** (theta + 1)
                    * theta**2
                    * (
                        ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                        + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                    )
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    + 4**theta
                    * theta
                    * (theta + 1)
                    * (
                        ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                        + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                    + theta
                    * (theta + 1)
                    * (4 * u + 4) ** theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((v + 1) ** theta - 1)
                )
            )
            / (
                (u + 1)
                * (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    ** 2
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - ((u + 1) * (v + 1)) ** theta * (2**theta - 1)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                )
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                )
                ** 2
            )
            + (
                -3
                * theta
                * (
                    ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                )
                * (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    ** 2
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                )
                - (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    ** 2
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                )
                * (
                    -(2**theta) * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    + ((u + 1) * (v + 1)) ** theta * (2**theta - 1)
                    + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                )
                - (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                )
                * (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    ** 2
                    - 2 ** (theta + 1)
                    * theta**2
                    * (
                        ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                        + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                    )
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    + 4**theta
                    * theta
                    * (theta + 1)
                    * (
                        ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                        + (2 * u + 2) ** theta * ((v + 1) ** theta - 1)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                    + theta
                    * (theta + 1)
                    * (4 * u + 4) ** theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        + ((u + 1) * (v + 1)) ** theta * (1 - 2**theta)
                    )
                    * ((v + 1) ** theta - 1)
                )
            )
            * (
                -(2**theta)
                * theta
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                )
                * (
                    2
                    * 2**theta
                    * theta
                    * (v + 1) ** theta
                    * ((u + 1) ** theta - 1)
                    / (v + 1)
                    - 2
                    * theta
                    * (2**theta - 1)
                    * (u + 1) ** theta
                    * (v + 1) ** theta
                    / (v + 1)
                )
                + 4**theta
                * theta
                * (theta + 1)
                * (v + 1) ** theta
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    - ((u + 1) * (v + 1)) ** theta * (2**theta - 1)
                )
                * ((u + 1) ** theta - 1)
                / (v + 1)
                + 4**theta
                * (theta + 1)
                * (
                    2**theta
                    * theta
                    * (v + 1) ** theta
                    * ((u + 1) ** theta - 1)
                    / (v + 1)
                    - theta * ((u + 1) * (v + 1)) ** theta * (2**theta - 1) / (v + 1)
                )
                * ((u + 1) ** theta - 1)
                * ((v + 1) ** theta - 1)
            )
            / (
                (u + 1)
                * (
                    2**theta
                    * theta
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                    )
                    ** 2
                    - 4**theta
                    * (theta + 1)
                    * (
                        2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                        - ((u + 1) * (v + 1)) ** theta * (2**theta - 1)
                    )
                    * ((u + 1) ** theta - 1)
                    * ((v + 1) ** theta - 1)
                )
                ** 2
                * (
                    2**theta * ((u + 1) ** theta - 1) * ((v + 1) ** theta - 1)
                    - (2**theta - 1) * (u + 1) ** theta * (v + 1) ** theta
                )
            )
        )

    def lambda_L(self):
        return 0

    def lambda_U(self):
        return 0
