# file: copul/families/xi_psi_lower_boundary.py
import sympy as sp
import numpy as np

from copul.family.core.biv_copula import BivCopula
from copul.family.frechet.biv_independence_copula import BivIndependenceCopula
from copul.wrapper.sympy_wrapper import SymPyFuncWrapper


class XiPsiLowerJensenBound(BivCopula):
    r"""
    A family of copulas tracing the lower boundary of the attainable region
    for pairs of Chatterjee's :math:`\xi` and Spearman's footrule :math:`\psi`.
    This family is derived by minimizing the functional
    :math:`J(C) = \psi(C) + \mu\,\xi(C)` for a parameter :math:`\mu \ge 1/2`.

    **Parameter —** :math:`\mu`
        :math:`\mu \in [\tfrac12,\infty)`. The special case :math:`\mu=\tfrac12`
        corresponds to the endpoint :math:`(\xi,\psi)=(12\ln 2 - 8,\,-\tfrac12)`.
        As :math:`\mu \to \infty`, the copula approaches independence.

    **Formulas**

    The copula's structure is defined by its conditional probability
    :math:`h(t,v) = \partial_1 C(t,v)`, which is piecewise constant in :math:`t`.
    Let :math:`v_0 = \dfrac{1}{2\mu+1}` and :math:`v_1 = \dfrac{2\mu}{2\mu+1}`.
    Then
    :math:`h(t,v) = h_1(v)\,\mathbf{1}_{\{t\le v\}} + h_2(v)\,\mathbf{1}_{\{t>v\}}`,
    where

    .. math::

       \begin{aligned}
       \text{for } v \in [0,v_0]:\quad & h_1(v)=0,\quad h_2(v)=\frac{v}{1-v},\\
       \text{for } v \in (v_0,v_1]:\quad & h_1(v)=v-\frac{1-v}{2\mu},\quad h_2(v)=v+\frac{v}{2\mu},\\
       \text{for } v \in (v_1,1]:\quad & h_1(v)=2-\frac{1}{v},\quad h_2(v)=1.
       \end{aligned}

    The CDF is

    .. math::

       C(u,v) =
       \begin{cases}
       u\,h_1(v), & u \le v,\\
       v\,h_1(v) + (u-v)\,h_2(v), & u > v.
       \end{cases}

    **Dependence measures**

    .. math::

       \psi(\mu) = -2v_1^2 + 6v_1 - 5 + \frac{1}{v_1},
       \qquad
       v_1 = \frac{2\mu}{2\mu+1}.

    .. math::

       \xi(\mu) = 4v_1^3 - 18v_1^2 + 36v_1 - 22 - 12\ln(v_1)
                  + \frac{6v_1^2 - 4v_1^3 - 1}{4\mu^2}.
    """

    # symbolic parameter & admissible interval
    mu = sp.symbols("mu", real=True)
    params = [mu]
    intervals = {"mu": sp.Interval(sp.Rational(1, 2), sp.oo)}
    special_cases = {sp.oo: BivIndependenceCopula}

    # convenience symbols
    u, v = sp.symbols("u v", positive=True)

    def __new__(cls, *args, **kwargs):
        if args and len(args) == 1:
            kwargs["mu"] = args[0]
        if "mu" in kwargs and kwargs["mu"] in cls.special_cases:
            special_case_cls = cls.special_cases[kwargs["mu"]]
            del kwargs["mu"]
            return special_case_cls()
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        if args and len(args) == 1:
            kwargs["mu"] = args[0]
        super().__init__(**kwargs)

    def __call__(self, *args, **kwargs):
        if args and len(args) == 1:
            kwargs["mu"] = args[0]
        if "mu" in kwargs and kwargs["mu"] in self.special_cases:
            special_case_cls = self.special_cases[kwargs["mu"]]
            del kwargs["mu"]
            return special_case_cls()
        return super().__call__(**kwargs)

    # -------- Symbolic helper functions -------- #
    @staticmethod
    def _h1_expr(v, mu):
        """Symbolic expression for the h_1(v) component."""
        v0 = 1 / (2 * mu + 1)
        v1 = (2 * mu) / (2 * mu + 1)

        h1_reg1 = 0
        h1_reg2 = v - (1 - v) / (2 * mu)
        h1_reg3 = 2 - 1 / v

        return sp.Piecewise(
            (h1_reg1, v <= v0),
            (h1_reg2, v <= v1),
            (h1_reg3, True),
        )

    @staticmethod
    def _h2_expr(v, mu):
        """Symbolic expression for the h_2(v) component."""
        v0 = 1 / (2 * mu + 1)
        v1 = (2 * mu) / (2 * mu + 1)

        h2_reg1 = v / (1 - v)
        h2_reg2 = v + v / (2 * mu)
        h2_reg3 = 1

        return sp.Piecewise(
            (h2_reg1, v <= v0),
            (h2_reg2, v <= v1),
            (h2_reg3, True),
        )

    # -------- CDF / PDF definitions -------- #
    @property
    def _cdf_expr(self):
        mu, u, v = self.mu, self.u, self.v

        h1 = self._h1_expr(v, mu)
        h2 = self._h2_expr(v, mu)

        # C(u,v) = integral from 0 to u of h(t,v) dt
        cdf_le = u * h1
        cdf_gt = v * h1 + (u - v) * h2

        return sp.Piecewise(
            (cdf_le, u <= v),
            (cdf_gt, True),
        )

    def _pdf_expr(self):
        """Joint density c(u,v) = ∂²C/∂u∂v."""
        expr = self.cdf.func.diff(self.u).diff(self.v)
        return SymPyFuncWrapper(expr)

    # ===================================================================
    # START: Vectorized CDF implementation for performance improvement
    # ===================================================================

    @staticmethod
    def _h1_h2_numpy(v, mu):
        """
        Numpy-based vectorized implementation of the h1 and h2 functions.
        This is a helper for `cdf_vectorized`.
        """
        v = np.asarray(v, dtype=float)
        mu = float(mu)

        # Ensure values are within [0,1] to avoid domain errors
        v = np.clip(v, 0, 1)

        v0 = 1 / (2 * mu + 1)
        v1 = (2 * mu) / (2 * mu + 1)

        # Initialize arrays
        h1 = np.zeros_like(v)
        h2 = np.zeros_like(v)

        # Define masks for the three regions
        mask1 = v <= v0
        mask3 = v > v1
        mask2 = ~mask1 & ~mask3  # v is in (v0, v1]

        # Region 1: v <= v0
        h1[mask1] = 0
        # Avoid division by zero if v=1 (though not possible in this region)
        v_safe_1 = np.minimum(v[mask1], 1 - 1e-12)
        h2[mask1] = v_safe_1 / (1 - v_safe_1)

        # Region 2: v0 < v <= v1
        h1[mask2] = v[mask2] - (1 - v[mask2]) / (2 * mu)
        h2[mask2] = v[mask2] + v[mask2] / (2 * mu)

        # Region 3: v > v1
        # Avoid division by zero if v=0 (not possible in this region)
        v_safe_3 = np.maximum(v[mask3], 1e-12)
        h1[mask3] = 2 - 1 / v_safe_3
        h2[mask3] = 1.0

        return h1, h2

    def cdf_vectorized(self, u, v):
        """
        Vectorized implementation of the cumulative distribution function.
        """
        u = np.asarray(u, dtype=float)
        v = np.asarray(v, dtype=float)

        mu = self.mu
        h1, h2 = self._h1_h2_numpy(v, mu)

        # C(u,v) = u*h1 if u <= v, else v*h1 + (u-v)*h2
        cond = u <= v
        res_le = u * h1
        res_gt = v * h1 + (u - v) * h2

        return np.where(cond, res_le, res_gt)

    # ===================================================================
    # END: Vectorized CDF implementation
    # ===================================================================

    # -------- Metadata -------- #
    @property
    def is_absolutely_continuous(self) -> bool:
        return True

    @property
    def is_symmetric(self) -> bool:
        # The construction h(t,v) is not symmetric in t and v.
        return False

    def spearmans_footrule(self):
        r"""
        Closed-form Spearman's footrule :math:`\psi(\mu)`.

        .. math::
           \psi(\mu) = -2v_1^2 + 6v_1 - 5 + \frac{1}{v_1},
           \qquad v_1 = \frac{2\mu}{2\mu+1}.
        """
        mu = self.mu
        v1 = (2 * mu) / (2 * mu + 1)
        return -2 * v1**2 + 6 * v1 - 5 + 1 / v1

    def chatterjees_xi(self):
        r"""
        Closed-form Chatterjee's :math:`\xi(\mu)`.

        .. math::
           \xi(\mu) = 4v_1^3 - 18v_1^2 + 36v_1 - 22 - 12\ln(v_1)
                      + \frac{6v_1^2 - 4v_1^3 - 1}{4\mu^2},
           \qquad v_1 = \frac{2\mu}{2\mu+1}.
        """
        mu = self.mu
        v1 = (2 * mu) / (2 * mu + 1)

        term1 = 4 * v1**3 - 18 * v1**2 + 36 * v1 - 22 - 12 * sp.log(v1)
        term2 = (6 * v1**2 - 4 * v1**3 - 1) / (4 * mu**2)

        return term1 + term2


if __name__ == "__main__":
    # Example usage for the endpoint mu = 0.5
    copula = XiPsiLowerJensenBound(mu=0.7)
    # copula.plot_cdf()
    copula.plot_pdf(plot_type="contour")
    copula.plot_cond_distr_1()
    # copula.plot_cond_distr_2()
