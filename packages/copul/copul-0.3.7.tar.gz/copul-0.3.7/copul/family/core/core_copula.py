import copy
import numpy as np
import sympy

from copul.numerics import to_numpy_callable
from copul.wrapper.cdf_wrapper import CDFWrapper
from copul.wrapper.cdi_wrapper import CDiWrapper
from copul.wrapper.sympy_wrapper import SymPyFuncWrapper


class CoreCopula:
    r"""
    Unified core for copula classes.

    This class consolidates functionality that was previously split between
    ``CoreCopula`` and ``Copula``. It manages symbolic CDF/PDF expressions,
    parameters and their admissible intervals, and provides flexible evaluation
    utilities (single point, vectorized, and partially substituted forms).
    """

    params = []
    intervals = {}
    log_cut_off = 4
    _cdf_expr_internal = (
        None  # Renamed from _cdf to avoid confusion with the new method
    )
    _free_symbols = {}

    def _unwrap_expr(self, maybe_wrapper):
        """Return the underlying sympy.Expr for wrappers; otherwise return as-is."""
        return getattr(maybe_wrapper, "func", maybe_wrapper)

    @property
    def _cdf_expr(self):
        # If we have an internal expression set, use it as a template
        if self._cdf_expr_internal is not None:
            # Make a deep copy to avoid modifying the original
            expr = self._cdf_expr_internal

            # Apply any symbol updates if _free_symbols is available
            if hasattr(self, "_free_symbols") and self._free_symbols:
                current_values = {}
                for symbol_name, symbol_obj in self._free_symbols.items():
                    # Get the current value from the object
                    if hasattr(self, symbol_name):
                        current_values[symbol_obj] = getattr(self, symbol_name)

                # Only create a new expression if we have substitutions
                if current_values:
                    expr = expr.subs(current_values)

            return expr
        return None

    @_cdf_expr.setter
    def _cdf_expr(self, value):
        self._cdf_expr_internal = value

    def __str__(self):
        return self.__class__.__name__

    def __init__(self, dimension, *args, **kwargs):
        r"""
        Initialize a copula.

        Parameters
        ----------
        dimension : int
            Dimension :math:`d` of the copula.
        *args : tuple
            Positional arguments mapped onto remaining symbolic parameters in order.
        **kwargs : dict
            Explicit parameter assignments (e.g. ``rho=0.5``) or other attributes.

        Notes
        -----
        Any provided parameters are removed from ``self.params`` and their intervals
        from ``self.intervals``; the remaining ones stay symbolic.
        """

        self.u_symbols = sympy.symbols(f"u1:{dimension + 1}", positive=True)
        self.dim = dimension
        self._are_class_vars(kwargs)
        for i in range(len(args)):
            kwargs[str(self.params[i])] = args[i]
        for k, v in kwargs.items():
            if isinstance(v, str):
                v = getattr(self.__class__, v)
            setattr(self, k, v)
        self.params = [param for param in self.params if str(param) not in kwargs]
        self.intervals = {
            k: v for k, v in self.intervals.items() if str(k) not in kwargs
        }

    def __call__(self, *args, **kwargs):
        """
        Create a new copula instance with updated parameters, or reduce dimension
        if margins are fixed at 1 via u<i>=1. If the resulting dimension is 2,
        return a BivCopula instance with symbols remapped to (u, v).

        Supports parameter updates in the same call; parameter updates are applied
        to the returned object (whether reduced or not).
        """
        # --- split parameter updates vs. u<i>=1 margin-fixes -------------------
        fix_idxs = set()
        param_kwargs = {}

        # first map positional args to remaining params (like your original code)
        for i in range(min(len(args), len(self.params))):
            param_kwargs[str(self.params[i])] = args[i]

        # now handle kwargs
        for k, v in list(kwargs.items()):
            if k.startswith("u") and v == 1:
                try:
                    idx = int(k[1:])  # 'u3' -> 3
                except ValueError:
                    raise ValueError(f"Unrecognized variable keyword {k!r}")
                fix_idxs.add(idx)
            else:
                param_kwargs[k] = v

        # ----------- NO reduction: behave like before (parameter update) -------
        if not fix_idxs:
            new_copula = copy.copy(self)
            self._are_class_vars(param_kwargs)
            for k, v in param_kwargs.items():
                if isinstance(v, str):
                    v = getattr(self.__class__, v)
                setattr(new_copula, k, v)
            new_copula.params = [p for p in self.params if str(p) not in param_kwargs]
            new_copula.intervals = {
                k: v for k, v in self.intervals.items() if str(k) not in param_kwargs
            }
            return new_copula

        # ----------------------- reduction path (u<i>=1) -----------------------
        if any(not (1 <= j <= self.dim) for j in fix_idxs):
            raise ValueError(f"indices must be in 1..{self.dim}")
        if self._cdf_expr is None:
            raise ValueError("CDF expression is not set for this copula.")

        # 1) substitute u_j = 1
        subs = {self.u_symbols[j - 1]: 1 for j in fix_idxs}
        new_expr = sympy.simplify(self._cdf_expr.subs(subs))

        # 2) keep remaining symbols and re-map to u1..u_{d'}
        keep_pairs = [
            (j, s) for j, s in enumerate(self.u_symbols, start=1) if j not in fix_idxs
        ]
        new_dim = len(keep_pairs)
        if new_dim == 0:
            raise ValueError(
                "All margins were fixed to 1; resulting copula has dimension 0."
            )
        new_u_symbols = sympy.symbols(f"u1:{new_dim + 1}", positive=True)
        remap = {old: new_u_symbols[i] for i, (_, old) in enumerate(keep_pairs)}
        new_expr = sympy.simplify(new_expr.subs(remap))

        # 3) if new_dim == 2, return a BivCopula with (u1,u2)->(u,v)
        if new_dim == 2:
            from copul.family.core.biv_copula import BivCopula  # adjust path if needed

            biv = BivCopula()

            # carry over parameters/intervals/free symbols + any concrete param values
            biv.params = list(self.params)
            biv.intervals = dict(self.intervals)
            biv._free_symbols = dict(getattr(self, "_free_symbols", {}))
            for p in biv.params:
                name = str(p)
                if hasattr(self, name):
                    setattr(biv, name, getattr(self, name))

            # remap u1,u2 -> biv.u, biv.v
            u1, u2 = sympy.symbols("u1 u2", positive=True)
            new_expr_uv = sympy.simplify(new_expr.subs({u1: biv.u, u2: biv.v}))

            biv._cdf_expr = new_expr_uv
            biv.u_symbols = [biv.u, biv.v]

            # apply any parameter updates passed in this call
            for k, v in param_kwargs.items():
                if isinstance(v, str):
                    v = getattr(biv.__class__, v)
                setattr(biv, k, v)
            biv.params = [p for p in biv.params if str(p) not in param_kwargs]
            biv.intervals = {
                k: v for k, v in biv.intervals.items() if str(k) not in param_kwargs
            }

            return biv

        # 4) otherwise return a reduced CoreCopula-like object
        new_copula = copy.copy(self)
        new_copula.dim = new_dim
        new_copula.u_symbols = new_u_symbols
        new_copula._cdf_expr = new_expr
        # keep params/intervals/_free_symbols; then apply param updates on the reduced object
        for k, v in param_kwargs.items():
            if isinstance(v, str):
                v = getattr(new_copula.__class__, v)
            setattr(new_copula, k, v)
        new_copula.params = [p for p in self.params if str(p) not in param_kwargs]
        new_copula.intervals = {
            k: v for k, v in self.intervals.items() if str(k) not in param_kwargs
        }
        return new_copula

    def _set_params(self, args, kwargs):
        r"""
        Populate parameters from ``args``/``kwargs`` on the current instance.

        Parameters
        ----------
        args : tuple
            Positional arguments mapped onto the remaining parameters in order.
        kwargs : dict
            Explicit parameter assignments (overrides values from ``args``).
        """

        if args and len(args) <= len(self.params):
            for i in range(len(args)):
                kwargs[str(self.params[i])] = args[i]
        if kwargs:
            for k, v in kwargs.items():
                setattr(self, k, v)

    @property
    def parameters(self):
        r"""
        Parameter intervals of the copula.

        Returns
        -------
        dict
            Mapping ``name -> sympy.Interval`` for the **remaining** (not yet fixed)
            parameters.
        """

        return self.intervals

    @property
    def is_absolutely_continuous(self) -> bool:
        r"""
        Whether the copula is absolutely continuous.

        Returns
        -------
        bool
            ``True`` if the copula has a density a.e. on :math:`[0,1]^d`,
            otherwise ``False``.

        Notes
        -----
        Subclasses must override this property.
        """

        # Implementations should override this method
        raise NotImplementedError("This method must be implemented in a subclass")

    @property
    def is_symmetric(self) -> bool:
        r"""
        Whether the copula is exchangeable (symmetric under coordinate permutations).

        Returns
        -------
        bool
            ``True`` if :math:`C(u_{\pi(1)},\ldots,u_{\pi(d)}) = C(u_1,\ldots,u_d)`
            for all permutations :math:`\pi`, otherwise ``False``.

        Notes
        -----
        Subclasses must override this property.
        """

        # Implementations should override this method
        raise NotImplementedError("This method must be implemented in a subclass")

    def _are_class_vars(self, kwargs):
        r"""
        Validate that all keys in ``kwargs`` are attributes of the instance.

        Parameters
        ----------
        kwargs : dict
            Candidate attribute assignments.

        Raises
        ------
        AssertionError
            If a key is not found among the instance attributes.
        """

        class_vars = set(dir(self))
        assert set(kwargs).issubset(class_vars), (
            f"keys: {set(kwargs)}, free symbols: {class_vars}"
        )

    def slice_interval(self, param, interval_start=None, interval_end=None):
        r"""
        Restrict the admissible interval of a parameter.

        Parameters
        ----------
        param : str or sympy.Symbol
            Parameter to restrict.
        interval_start : float, optional
            New lower bound (inclusive).
        interval_end : float, optional
            New upper bound (inclusive).

        Notes
        -----
        If a bound is not provided, the corresponding bound from the current
        interval is kept. Open bounds are closed when explicitly set.
        """

        if not isinstance(param, str):
            param = str(param)
        left_open = self.intervals[param].left_open
        right_open = self.intervals[param].right_open
        if interval_start is None:
            interval_start = self.intervals[param].inf
        else:
            left_open = False
        if interval_end is None:
            interval_end = self.intervals[param].sup
        else:
            right_open = False
        self.intervals[param] = sympy.Interval(
            interval_start, interval_end, left_open, right_open
        )

    def _get_cdf_expr(self):
        r"""
        Return the symbolic CDF wrapper with current parameter substitutions.

        Returns
        -------
        CDFWrapper
            Wrapper around the (possibly partially substituted) CDF expression.
        """

        return CDFWrapper(self._cdf_expr)

    def cdf(self, *args, **kwargs):
        r"""
        Evaluate (or partially evaluate) the CDF.

        Supports:
          - C(u1,...,ud) via separate scalars or a 1D array
          - partial substitution via kwargs (u1=..., u2=..., u=..., v=...)
          - returns a callable wrapper if variables remain, otherwise a scalar
        """
        cdf_expr = self._get_cdf_expr()
        # Apply substitutions (kwargs)
        cdf_expr = cdf_expr(**kwargs)

        # If NO positional args: if expression is constant (no u-symbols), return scalar
        if not args:
            expr = self._unwrap_expr(cdf_expr)
            # which u-symbols remain?
            rem_syms = [s for s in self.u_symbols if expr.has(s)]
            if not rem_syms:
                # fully constant after kwargs → evaluate now
                return float(expr) if expr.is_number else float(expr.evalf())
            # still has variables → return partially evaluated wrapper
            return cdf_expr

        # If positional args ARE provided:
        # Fast-path: full-point evaluation via separate scalars/array
        # - If args represent a single 1D array of length dim
        if len(args) == 1:
            arg = args[0]
            if hasattr(arg, "ndim") and hasattr(arg, "shape"):
                arr = np.asarray(arg, dtype=float)
                if arr.ndim == 1 and len(arr) == self.dim:
                    # full point → map all u_symbols
                    sub_all = {
                        str(sym): float(val) for sym, val in zip(self.u_symbols, arr)
                    }
                    return cdf_expr(**sub_all)
            elif hasattr(arg, "__len__"):
                if len(arg) == self.dim:
                    point = np.array(arg, dtype=float)
                    sub_all = {
                        str(sym): float(val) for sym, val in zip(self.u_symbols, point)
                    }
                    return cdf_expr(**sub_all)
                # else: will fall through to partial-remain logic below

        # Case: separate scalars for a full point
        if len(args) == self.dim and not kwargs:
            point = np.array(args, dtype=float)
            sub_all = {str(sym): float(val) for sym, val in zip(self.u_symbols, point)}
            return cdf_expr(**sub_all)

        # Otherwise: partial substitution + remaining vars provided in *args*
        expr = self._unwrap_expr(cdf_expr)
        remaining_vars = [str(sym) for sym in self.u_symbols if expr.has(sym)]
        remaining_dim = len(remaining_vars)

        # Convert *args* to a 1D point for remaining variables
        if len(args) == 1:
            arg = args[0]
            if hasattr(arg, "ndim") and hasattr(arg, "shape"):
                arr = np.asarray(arg, dtype=float)
                if arr.ndim != 1:
                    raise ValueError(
                        "Cannot mix variable substitution with multi-point evaluation"
                    )
                if len(arr) != remaining_dim:
                    raise ValueError(
                        f"Expected {remaining_dim} remaining coordinates, got {len(arr)}"
                    )
                point = arr
            elif hasattr(arg, "__len__"):
                if len(arg) != remaining_dim:
                    raise ValueError(
                        f"Expected {remaining_dim} remaining coordinates, got {len(arg)}"
                    )
                point = np.array(arg, dtype=float)
            else:
                if remaining_dim != 1:
                    raise ValueError(
                        f"Expected {remaining_dim} remaining coordinates, got 1"
                    )
                point = np.array([arg], dtype=float)
        else:
            if len(args) != remaining_dim:
                raise ValueError(
                    f"Expected {remaining_dim} remaining coordinates, got {len(args)}"
                )
            point = np.array(args, dtype=float)

        sub_dict = {var: float(val) for var, val in zip(remaining_vars, point)}
        return cdf_expr(**sub_dict)

    def _cdf_single_point(self, u):
        r"""
        Helper: CDF at a **single** point.

        Parameters
        ----------
        u : numpy.ndarray
            1D array of length ``dim``.

        Returns
        -------
        float
            :math:`C(u)`.
        """

        # Get the CDF wrapper and evaluate
        cdf_wrapper = self._get_cdf_expr()
        return cdf_wrapper(*u)

    def cond_distr(self, i, *args, **kwargs):
        r"""
        Evaluate (or partially evaluate) the conditional distribution
        F_{U_{-i}|U_i}(u_{-i} | u_i) = ∂C/∂u_i.
        """
        if i < 1 or i > self.dim:
            raise ValueError(f"Dimension {i} out of range 1..{self.dim}")

        # Build derivative and wrap
        cdf = self.cdf()
        cond_expr = cdf.diff(self.u_symbols[i - 1])
        cond_expr = CDiWrapper(cond_expr, i)(**kwargs)

        # If no args: if constant w.r.t remaining u’s, return scalar
        if not args:
            expr = self._unwrap_expr(cond_expr)
            rem_syms = [s for s in self.u_symbols if expr.has(s)]
            if not rem_syms:
                return float(expr) if expr.is_number else float(expr.evalf())
            return cond_expr

        # Full-point fallback: if user passed a full coordinate and no kwargs
        if len(args) == self.dim and not kwargs:
            point = np.array(args, dtype=float)
            sub_all = {str(sym): float(val) for sym, val in zip(self.u_symbols, point)}
            wrapper = CDiWrapper(self._unwrap_expr(cond_expr), i)  # rewrap cleanly
            return wrapper(**sub_all)

        # Otherwise, remaining-vars path
        expr = self._unwrap_expr(cond_expr)
        remaining_vars = [str(sym) for sym in self.u_symbols if expr.has(sym)]
        remaining_dim = len(remaining_vars)

        if len(args) == 1:
            arg = args[0]
            if hasattr(arg, "ndim") and hasattr(arg, "shape"):
                arr = np.asarray(arg, dtype=float)
                if arr.ndim != 1:
                    raise ValueError(
                        "Cannot mix variable substitution with multi-point evaluation"
                    )
                if len(arr) != remaining_dim:
                    raise ValueError(
                        f"Expected {remaining_dim} remaining coordinates, got {len(arr)}"
                    )
                point = arr
            elif hasattr(arg, "__len__"):
                if len(arg) != remaining_dim:
                    raise ValueError(
                        f"Expected {remaining_dim} remaining coordinates, got {len(arg)}"
                    )
                point = np.array(arg, dtype=float)
            else:
                if remaining_dim != 1:
                    raise ValueError(
                        f"Expected {remaining_dim} remaining coordinates, got 1"
                    )
                point = np.array([arg], dtype=float)
        else:
            if len(args) != remaining_dim:
                raise ValueError(
                    f"Expected {remaining_dim} remaining coordinates, got {len(args)}"
                )
            point = np.array(args, dtype=float)

        sub_dict = {var: float(val) for var, val in zip(remaining_vars, point)}
        wrapper = CDiWrapper(expr, i)
        return wrapper(**sub_dict)

    def _cond_distr_single(self, i, u):
        r"""
        Helper: conditional distribution at a **single** point.

        Parameters
        ----------
        i : int
            Conditioning index (1-based).
        u : numpy.ndarray
            1D array of length ``dim``.

        Returns
        -------
        float
            Value of :math:`F_{U_{-i}\mid U_i}(u_{-i}\mid u_i)`.
        """

        # Get the conditional distribution function
        cdf = self.cdf()
        derivative = sympy.diff(cdf, self.u_symbols[i - 1])
        cond_distr_func = SymPyFuncWrapper(derivative)

        # Evaluate at the point
        return cond_distr_func(*u)

    def _cond_distr_vectorized(self, i, points):
        r"""
        Helper: conditional distribution for **multiple** points.

        Parameters
        ----------
        i : int
            Conditioning index (1-based).
        points : numpy.ndarray
            Array of shape ``(n_points, dim)``.

        Returns
        -------
        numpy.ndarray
            Values of :math:`F_{U_{-i}\mid U_i}` for each row.
        """

        n_points = points.shape[0]
        results = np.zeros(n_points)

        # Get the conditional distribution function
        cond_distr_func = SymPyFuncWrapper(
            sympy.diff(self._get_cdf_expr(), self.u_symbols[i - 1])
        )

        # Evaluate for each point
        for j, point in enumerate(points):
            results[j] = cond_distr_func(*point)

        return results

    def cond_distr_1(self, *args, **kwargs):
        r"""
        :math:`F_{U_{-1}\mid U_1}(u_{-1}\mid u_1)`.

        Parameters
        ----------
        *args, **kwargs
            See :meth:`cond_distr`.
        """

        return self.cond_distr(1, *args, **kwargs)

    def cond_distr_2(self, *args, **kwargs):
        r"""
        :math:`F_{U_{-2}\mid U_2}(u_{-2}\mid u_2)`.

        Parameters
        ----------
        *args, **kwargs
            See :meth:`cond_distr`.
        """

        return self.cond_distr(2, *args, **kwargs)

    def pdf(self, *args, **kwargs):
        r"""
        Evaluate (or partially evaluate) the PDF:
          ∂^d C / ∂u1 ... ∂ud
        """
        # Build PDF sympy expr by differentiating C w.r.t. all u_j
        pdf_expr = self._get_cdf_expr()
        for u_symbol in self.u_symbols:
            pdf_expr = pdf_expr.diff(u_symbol)

        pdf_expr = pdf_expr(**kwargs)  # apply partial substitutions

        # If no args: if constant, return scalar (important for independence)
        if not args:
            expr = self._unwrap_expr(pdf_expr)
            rem_syms = [s for s in self.u_symbols if expr.has(s)]
            if not rem_syms:
                return float(expr) if expr.is_number else float(expr.evalf())
            return SymPyFuncWrapper(expr)

        # Full-point fallback: separate scalars / array for a full coordinate
        if len(args) == 1:
            arg = args[0]
            if hasattr(arg, "ndim") and hasattr(arg, "shape"):
                arr = np.asarray(arg, dtype=float)
                if arr.ndim == 1 and len(arr) == self.dim and not kwargs:
                    sub_all = {
                        str(sym): float(val) for sym, val in zip(self.u_symbols, arr)
                    }
                    return pdf_expr(**sub_all)
            elif hasattr(arg, "__len__"):
                if len(arg) == self.dim and not kwargs:
                    point = np.array(arg, dtype=float)
                    sub_all = {
                        str(sym): float(val) for sym, val in zip(self.u_symbols, point)
                    }
                    return pdf_expr(**sub_all)

        if len(args) == self.dim and not kwargs:
            point = np.array(args, dtype=float)
            sub_all = {str(sym): float(val) for sym, val in zip(self.u_symbols, point)}
            return pdf_expr(**sub_all)

        # Partial path: determine remaining variables robustly
        expr = self._unwrap_expr(pdf_expr)
        remaining_vars = [str(sym) for sym in self.u_symbols if expr.has(sym)]
        remaining_dim = len(remaining_vars)

        if len(args) == 1:
            arg = args[0]
            if hasattr(arg, "ndim") and hasattr(arg, "shape"):
                arr = np.asarray(arg, dtype=float)
                if arr.ndim != 1:
                    raise ValueError(
                        "Cannot mix variable substitution with multi-point evaluation"
                    )
                if len(arr) != remaining_dim:
                    raise ValueError(
                        f"Expected {remaining_dim} remaining coordinates, got {len(arr)}"
                    )
                point = arr
            elif hasattr(arg, "__len__"):
                if len(arg) != remaining_dim:
                    raise ValueError(
                        f"Expected {remaining_dim} remaining coordinates, got {len(arg)}"
                    )
                point = np.array(arg, dtype=float)
            else:
                if remaining_dim != 1:
                    raise ValueError(
                        f"Expected {remaining_dim} remaining coordinates, got 1"
                    )
                point = np.array([arg], dtype=float)
        else:
            if len(args) != remaining_dim:
                raise ValueError(
                    f"Expected {remaining_dim} remaining coordinates, got {len(args)}"
                )
            point = np.array(args, dtype=float)

        sub_dict = {var: float(val) for var, val in zip(remaining_vars, point)}
        return SymPyFuncWrapper(expr)(**sub_dict)

    def _pdf_single_point(self, u):
        r"""
        Helper: PDF at a **single** point.

        Parameters
        ----------
        u : numpy.ndarray
            1D array of length ``dim``.

        Returns
        -------
        float
            :math:`c(u)` (the copula density at ``u``).
        """

        # Compute the PDF
        term = self._get_cdf_expr()
        for u_symbol in self.u_symbols:
            term = sympy.diff(term, u_symbol)
        pdf_func = SymPyFuncWrapper(term)

        # Evaluate at the point
        return pdf_func(*u)

    def _pdf_vectorized(self, points):
        r"""
        Vectorized PDF for **multiple** points.

        Parameters
        ----------
        points : numpy.ndarray
            Array of shape ``(n_points, dim)`` where each row is a point.

        Returns
        -------
        numpy.ndarray
            Array of shape ``(n_points,)`` with values of :math:`c(u)`.
        """

        n_points = points.shape[0]
        results = np.zeros(n_points)

        # Compute the PDF function
        term = self._get_cdf_expr()
        for u_symbol in self.u_symbols:
            term = sympy.diff(term, u_symbol)
        pdf_func = SymPyFuncWrapper(term)

        # Evaluate for each point
        for i, point in enumerate(points):
            results[i] = pdf_func(*point)

        return results

    # ------------------------------------------------------------------
    # Copula transforms
    # ------------------------------------------------------------------
    def survival_copula(self):
        r"""
        Return the survival (upper-tail) copula :math:`\widehat C` corresponding to *self*.

        In :math:`d` dimensions, the survival copula is given by the inclusion–exclusion formula

        .. math::

           \widehat C(u)
           \;=\;
           \sum_{J\subseteq\{1,\dots,d\}} (-1)^{|J|}
           \, C\!\big(u^{(J)}\big),

        where :math:`u^{(J)}` denotes the vector obtained from :math:`u` by replacing
        :math:`u_j` with :math:`1` for all :math:`j\in J`.

        Returns
        -------
        CoreCopula
            A new copula object whose CDF expression is the survival copula of the current one.
        """

        from itertools import combinations

        if self._cdf_expr is None:
            raise ValueError("CDF expression is not set for this copula.")

        expr = 0
        # Inclusion–exclusion over all coordinate subsets
        for k in range(self.dim + 1):
            for J in combinations(range(self.dim), k):
                subs = {self.u_symbols[j]: 1 for j in J}
                expr += (-1) ** k * self._cdf_expr.subs(subs)

        new_copula = copy.copy(self)
        new_copula._cdf_expr = sympy.simplify(expr)
        return new_copula

    def vertical_reflection(self, margin: int = 2):
        r"""
        Vertical reflection :math:`C^{\vee}` of *self* with respect to one margin.

        By default (``margin=2``) and in the bivariate case,
        \[
        C^{\vee}(u,v) \;=\; u \;-\; C\bigl(u,\,1-v\bigr).
        \]
        For general ``margin=j`` (``1 \le j \le \mathrm{dim}``),
        \[
        C^{\vee}(u) \;=\; u_j \;-\;
        C\bigl(u_1,\dots,u_{j-1},\,1-u_j,\,u_{j+1},\dots,u_d\bigr).
        \]

        Parameters
        ----------
        margin : int, optional
            1-based index of the reflected coordinate (default ``2``).

        Returns
        -------
        CoreCopula
            A new copula object whose CDF expression is the vertical reflection of the current one.
        """

        if not (1 <= margin <= self.dim):
            raise ValueError(f"margin must be in 1..{self.dim}")

        if self._cdf_expr is None:
            raise ValueError("CDF expression is not set for this copula.")

        uj = self.u_symbols[margin - 1]
        reflected_expr = sympy.simplify(uj - self._cdf_expr.subs({uj: 1 - uj}))

        new_copula = copy.copy(self)
        new_copula._cdf_expr = reflected_expr
        return new_copula

    def is_fully_specified(self) -> bool:
        """True iff all parameters have been assigned concrete values."""
        return len(self.params) == 0

    def _lambdify_cdf_numpy(self):
        if self._cdf_expr is None:
            raise ValueError("CDF expression is not set for this copula.")
        return to_numpy_callable(self._cdf_expr, self.u_symbols, ae=True)

    def validate_copula(
        self, m: int = 21, tol: float = 1e-8, return_details: bool = False
    ):
        """
        Numerically validate copula properties on an (m+1)^d grid.

        Parameters
        ----------
        m : int
            Number of intervals per axis (grid has m+1 knots).
        tol : float
            Numerical tolerance for checks.
        return_details : bool
            If True, returns a dict with diagnostics in addition to the boolean.

        Returns
        -------
        ok : bool  (and optionally details : dict)
        """
        if not self.is_fully_specified():
            raise ValueError(
                "Copula has free parameters; fix all parameters before validation."
            )

        d = self.dim
        f = self._lambdify_cdf_numpy()
        axes = [np.linspace(0.0, 1.0, m + 1) for _ in range(d)]
        grids = np.meshgrid(
            *axes, indexing="ij"
        )  # list of d arrays shape (m+1,...,m+1)

        # Evaluate C on the grid
        with np.errstate(divide="ignore", invalid="ignore"):
            C_grid = f(*grids)
        if not np.all(np.isfinite(C_grid)):
            details = {"finite": False}
            return (False, details) if return_details else False

        # Bounds: 0 <= C <= 1
        bounds_ok = (C_grid.min() >= -tol) and (C_grid.max() <= 1 + tol)

        # Groundedness: any coordinate = 0 => C = 0
        grounded_ok = True
        for k in range(d):
            slicer = [slice(None)] * d
            slicer[k] = 0  # axis k at 0
            grounded_ok &= np.all(np.abs(C_grid[tuple(slicer)]) <= tol)

        # Margins: C(1,...,u_k,...,1) == u_k
        margins_ok = True
        max_margin_err = 0.0
        for k in range(d):
            slicer = [slice(None)] * d
            for j in range(d):
                if j != k:
                    slicer[j] = -1  # set others to 1
            # extract 1D margin curve over axis k
            curve = C_grid[tuple(slicer)]
            err = np.max(np.abs(curve - axes[k]))
            max_margin_err = max(max_margin_err, err)
            margins_ok &= err <= 5 * tol  # a bit looser because it compounds

        # d-increasing: all cell masses (successive forward differences) >= 0; sum ≈ 1
        mass = C_grid.copy()
        for axis in range(d):
            mass = np.diff(mass, axis=axis)
        # inclusion–exclusion via successive diffs yields cell masses on shape (m,)*d
        min_mass = mass.min()
        sum_mass = mass.sum()
        increasing_ok = (min_mass >= -1e-10) and (abs(sum_mass - 1.0) <= 1e-6)

        ok = bounds_ok and grounded_ok and margins_ok and increasing_ok

        if not return_details:
            return ok

        details = {
            "bounds_ok": bounds_ok,
            "grounded_ok": grounded_ok,
            "margins_ok": margins_ok,
            "max_margin_abs_err": float(max_margin_err),
            "increasing_ok": increasing_ok,
            "min_cell_mass": float(min_mass),
            "sum_cell_mass": float(sum_mass),
            "grid_size_per_axis": m + 1,
            "dim": d,
            "tol": tol,
        }
        return ok, details
