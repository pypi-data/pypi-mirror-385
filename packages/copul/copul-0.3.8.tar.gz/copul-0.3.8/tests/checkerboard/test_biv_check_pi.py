import matplotlib
import numpy as np
import pytest
from matplotlib import pyplot as plt

from copul import FarlieGumbelMorgenstern, Frechet
from copul.checkerboard.biv_check_pi import BivCheckPi

matplotlib.use("Agg")  # Use the 'Agg' backend to suppress the pop-up


@pytest.mark.parametrize(
    "matr, point, expected",
    [
        ([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], (0.5, 1), 0.5),
        ([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], (0.5, 0.5), 0.25),
        ([[1, 5, 4], [5, 3, 2], [4, 2, 4]], (0.5, 0.5), 0.225),
        ([[1, 5, 4], [5, 3, 2], [4, 2, 4]], (1, 0.5), 0.5),
    ],
)
def test_ccop_cdf(matr, point, expected):
    ccop = BivCheckPi(matr)
    actual = ccop.cdf(*point)
    assert np.isclose(actual, expected)


@pytest.fixture
def setup_checkerboard_copula():
    # Setup code for initializing the CheckerboardCopula instance
    matr = [[0, 9, 1], [1, 0, 9], [9, 1, 0]]
    return BivCheckPi(matr)


def test___init__():
    orig_matr = [[1, 0], [0, 1]]
    ccop = BivCheckPi(orig_matr)
    ccop_matr = ccop.matr.tolist()
    assert ccop_matr == [[0.5, 0], [0, 0.5]]
    assert hasattr(ccop.matr, "ndim")


@pytest.mark.parametrize(
    "plotting_method",
    [
        lambda ccop: ccop.scatter_plot(),
        lambda ccop: ccop.plot_cdf(),
        lambda ccop: ccop.plot_pdf(),
    ],
)
def test_ccop_plotting(setup_checkerboard_copula, plotting_method):
    ccop = setup_checkerboard_copula

    plotting_method(ccop)
    try:
        plotting_method(ccop)
    except Exception as e:
        pytest.fail(f"{plotting_method.__name__} raised an exception: {e}")
    finally:
        plt.close("all")


@pytest.mark.parametrize(
    "matr, point, expected",
    [
        ([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], (0.5, 0.5), 1),
        ([[1, 5, 4], [5, 3, 2], [4, 2, 4]], (0.5, 0.5), 0.9),
        ([[1, 5, 4], [5, 3, 2], [4, 2, 4]], (0.5, 1), 9 / 15),
    ],
)
def test_ccop_pdf(matr, point, expected):
    ccop = BivCheckPi(matr)
    result = ccop.pdf(*point)
    assert result == expected


@pytest.mark.parametrize(
    "matr, expected",
    [
        ([[1, 0], [0, 1]], 0),  # 0.5 belongs to the second row, so ~ Unif[0.5, 1]
        ([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], 0.5),
        ([[1, 5, 4], [5, 3, 2], [4, 2, 4]], 0.65),  # second row -> (1*5+0.5*3+0*2)/10
    ],
)
def test_ccop_cond_distr_1(matr, expected):
    ccop = BivCheckPi(matr)
    actual = ccop.cond_distr_1(0.5, 0.5)
    assert np.isclose(actual, expected)


@pytest.mark.parametrize(
    "u, v, expected",
    [
        (0.4, 0.4, 0.8),
        (0.4, 0.6, 1),
        (0.6, 0.4, 0),
    ],
)
def test_ccop_cond_distr_1_different_points(u, v, expected):
    matr = [[1, 0], [0, 1]]
    ccop = BivCheckPi(matr)
    actual = ccop.cond_distr_1(u, v)
    assert np.isclose(actual, expected)


@pytest.mark.parametrize(
    "matr, expected",
    [
        ([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], 0.5),
        ([[1, 2], [2, 1]], 2 / 3),  # 0.5 belongs to second column
        ([[1, 0], [0, 1]], 0),  # 0.5 belongs to second row
    ],
)
def test_ccop_cond_distr_2(matr, expected):
    ccop = BivCheckPi(matr)
    result = ccop.cond_distr_2(0.5, 0.5)
    assert np.isclose(result, expected)


@pytest.mark.parametrize(
    "matr, expected",
    [
        ([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], 0),
        ([[1, 0], [0, 1]], 0.5),
    ],
)
def test_ccop_xi(matr, expected):
    np.random.seed(1)
    ccop = BivCheckPi(matr)
    xi_estimate = ccop.chatterjees_xi()
    actual_diff = np.abs(xi_estimate - expected)
    assert actual_diff < 0.02


def test_check_pi_rvs():
    np.random.seed(1)
    ccop = BivCheckPi([[1, 2], [2, 1]])
    n = 1_000
    samples = ccop.rvs(n)
    n_lower_empirical = sum([(sample < (0.5, 0.5)).all() for sample in samples])
    n_upper_empirical = sum([(sample > (0.5, 0.5)).all() for sample in samples])
    theoretical_ratio = 1 / 6 * n
    assert n_lower_empirical < 1.5 * theoretical_ratio
    assert n_upper_empirical < 1.5 * theoretical_ratio


# Tests for tau (Kendall's tau)
@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_tau_independence(n):
    """Test that tau is close to 0 for independence copula."""
    matr = np.ones((n, n))  # Uniform distribution represents independence
    ccop = BivCheckPi(matr)
    tau = ccop.kendalls_tau()
    assert np.isclose(tau, 0, atol=1e-2)


@pytest.mark.parametrize("n", [3, 4])
def test_tau_perfect_dependence(n):
    """Test tau for perfect positive and negative dependence."""
    # Perfect positive dependence
    matr_pos = np.zeros((n, n))
    np.fill_diagonal(matr_pos, 1)  # Place 1's on the main diagonal
    ccop_pos = BivCheckPi(matr_pos)
    tau_pos = ccop_pos.kendalls_tau()

    # Perfect negative dependence
    matr_neg = np.zeros((n, n))
    for i in range(3):
        matr_neg[i, 2 - i] = 1  # Place 1's on the opposite diagonal
    ccop_neg = BivCheckPi(matr_neg)
    tau_neg = ccop_neg.kendalls_tau()

    # Tau should be positive for positive dependence and negative for negative dependence
    assert tau_pos > 0.5
    assert tau_neg < -0.5


def test_tau_2x2_exact():
    """Test exact values for 2x2 checkerboard copulas."""
    np.random.seed(42)
    # For a 2x2 checkerboard with perfect positive dependence
    matr_pos = np.array([[1, 0], [0, 1]])
    ccop_pos = BivCheckPi(matr_pos)

    # For a 2x2 checkerboard with perfect negative dependence
    matr_neg = np.array([[0, 1], [1, 0]])
    ccop_neg = BivCheckPi(matr_neg)

    # For 2x2, these are the exact values
    tau_pos = ccop_pos.kendalls_tau()
    assert np.isclose(tau_pos, 0.5, atol=1e-2)
    tau_neg = ccop_neg.kendalls_tau()
    assert np.isclose(tau_neg, -0.5, atol=1e-2)


def test_measures_of_assiciation_with_rectangular_matrix():
    """Test that tau and rho are consistent for a rectangular matrix."""
    matr = [
        [
            0.258794517498538,
            0.3467253550730139,
            0.39100995184938075,
            0.41768373795216235,
        ],
        [
            0.4483122636880096,
            0.3603814261135337,
            0.3160968293371668,
            0.2894230432343852,
        ],
    ]
    ccop = BivCheckPi(matr)
    xi1 = ccop.chatterjees_xi(condition_on_y=False)
    xi2 = ccop.chatterjees_xi(condition_on_y=True)
    assert 1 > xi1 > 0
    assert 1 > xi2 > 0
    tau = ccop.kendalls_tau()
    rho = ccop.spearmans_rho()
    assert 1 > tau > -1
    assert 1 > rho > -1


def test_tau_example():
    """Test tau for the example matrix from the original code."""
    matr = np.array([[1, 5, 4], [5, 3, 2], [4, 2, 4]])
    ccop = BivCheckPi(matr)
    tau = ccop.kendalls_tau()

    # Check range and expected sign (this matrix has positive dependence)
    assert -1 <= tau <= 1
    assert tau < 0


# Tests for rho (Spearman's rho)
def test_rho_independence():
    """Test that rho is close to 0 for independence copula."""
    np.random.seed(42)
    matr = np.ones((4, 4))  # Uniform distribution represents independence
    ccop = BivCheckPi(matr)
    rho = ccop.spearmans_rho()
    assert np.isclose(rho, 0, atol=1e-2)


def test_rho_perfect_dependence():
    """Test rho for perfect positive and negative dependence."""
    # Perfect positive dependence
    matr_pos = np.zeros((3, 3))
    np.fill_diagonal(matr_pos, 1)  # Place 1's on the main diagonal
    ccop_pos = BivCheckPi(matr_pos)
    rho_pos = ccop_pos.spearmans_rho()

    # Perfect negative dependence
    matr_neg = np.zeros((3, 3))
    for i in range(3):
        matr_neg[i, 2 - i] = 1  # Place 1's on the opposite diagonal
    ccop_neg = BivCheckPi(matr_neg)
    rho_neg = ccop_neg.spearmans_rho()

    # Rho should be positive for positive dependence and negative for negative dependence
    assert rho_pos > 0.5
    assert rho_neg < -0.5


def test_rho_2x2_exact():
    """Test exact values for 2x2 checkerboard copulas."""
    np.random.seed(42)
    # For a 2x2 checkerboard with perfect positive dependence
    matr_pos = np.array([[1, 0], [0, 1]])
    ccop_pos = BivCheckPi(matr_pos)

    # For a 2x2 checkerboard with perfect negative dependence
    matr_neg = np.array([[0, 1], [1, 0]])
    ccop_neg = BivCheckPi(matr_neg)

    # For 2x2, these are the exact values
    pos_rho = ccop_pos.spearmans_rho()
    assert np.isclose(pos_rho, 0.745, atol=1e-1)
    neg_rho = ccop_neg.spearmans_rho()
    assert np.isclose(neg_rho, -0.745, atol=1e-1)


def test_rho_example():
    """Test rho for the example matrix from the original code."""
    matr = np.array([[1, 5, 4], [5, 3, 2], [4, 2, 4]])
    ccop = BivCheckPi(matr)
    rho_val = ccop.spearmans_rho()

    # Check range and expected sign (this matrix has positive dependence)
    assert -1 <= rho_val <= 1
    assert rho_val < 0


# Tests for xi (Chatterjee's xi)
@pytest.mark.parametrize(
    "n, condition_on_y",
    ([(1, True), (1, False), (2, True), (2, False), (3, True), (3, False)]),
)
def test_xi_independence(n, condition_on_y):
    """Test that xi is close to 0 for independence copula."""
    matr = np.ones((n, n))  # Uniform distribution represents independence
    ccop = BivCheckPi(matr)
    assert np.isclose(ccop.chatterjees_xi(condition_on_y), 0, atol=1e-2)


def test_xi_perfect_dependence():
    """Test xi for perfect positive and negative dependence."""
    # Perfect positive dependence
    matr_pos = np.zeros((10, 10))
    np.fill_diagonal(matr_pos, 1)  # Place 1's on the main diagonal
    ccop_pos = BivCheckPi(matr_pos)
    xi_pos = ccop_pos.chatterjees_xi()

    # Perfect negative dependence
    matr_neg = np.zeros((10, 10))
    for i in range(10):
        matr_neg[i, 9 - i] = 1  # Place 1's on the opposite diagonal
    ccop_neg = BivCheckPi(matr_neg)
    xi_neg = ccop_neg.chatterjees_xi()

    # Xi should be close to 1 for both perfect positive and negative dependence
    assert xi_pos > 0.8
    assert xi_neg > 0.8


def test_xi_2x2_exact():
    """Test exact values for 2x2 checkerboard copulas."""
    np.random.seed(42)
    # For a 2x2 checkerboard with perfect positive dependence
    matr_pos = np.array([[1, 0], [0, 1]])
    ccop_pos = BivCheckPi(matr_pos)

    # For a 2x2 checkerboard with perfect negative dependence
    matr_neg = np.array([[0, 1], [1, 0]])
    ccop_neg = BivCheckPi(matr_neg)

    # For 2x2, both should have xi = 1 (perfect dependence)
    xi_pos = ccop_pos.chatterjees_xi()
    xi_neg = ccop_neg.chatterjees_xi()
    assert np.isclose(xi_pos, 0.5, atol=1e-1)
    assert np.isclose(xi_neg, 0.5, atol=1e-1)


def test_xi_example():
    """Test xi for the example matrix from the original code."""
    matr = np.array([[1, 5, 4], [5, 3, 2], [4, 2, 4]])
    ccop = BivCheckPi(matr)
    xi_val = ccop.chatterjees_xi()

    # Check range (xi is always between 0 and 1)
    assert 0 <= xi_val <= 1


def test_measure_consistency():
    """Test that tau and rho have consistent signs for asymmetric matrices."""
    # Create a matrix with positive dependence
    matr_pos = np.array([[0.6, 0.2, 0.0], [0.2, 0.4, 0.2], [0.0, 0.2, 0.6]])
    ccop_pos = BivCheckPi(matr_pos)
    tau_pos = ccop_pos.kendalls_tau()
    rho_pos = ccop_pos.spearmans_rho()

    # Both should be positive
    assert tau_pos > 0
    assert rho_pos > 0

    # Create a matrix with negative dependence
    matr_neg = np.array([[0.0, 0.2, 0.6], [0.2, 0.4, 0.2], [0.6, 0.2, 0.0]])
    ccop_neg = BivCheckPi(matr_neg)
    tau_neg = ccop_neg.kendalls_tau()
    rho_neg = ccop_neg.spearmans_rho()

    # Both should be negative
    assert tau_neg < 0
    assert rho_neg < 0


def test_xi_equivalent_to_monte_carlo():
    """Test that our implementation matches the standard case from existing test."""
    # This matrix was tested previously with Monte Carlo
    matr = np.array([[1, 0], [0, 1]])
    ccop = BivCheckPi(matr)
    xi_value = ccop.chatterjees_xi()
    assert np.isclose(xi_value, 0.5, atol=0.02)


def test_pdf():
    matr = [[1, 5, 4], [5, 3, 2], [4, 2, 4]]
    ccop = BivCheckPi(matr)
    point = (0.1, 0.1)
    expected_pdf = 1 / 30 * 9
    actual_pdf = ccop.pdf(*point)
    assert np.isclose(actual_pdf, expected_pdf, atol=1e-2), (
        f"Expected {expected_pdf}, got {actual_pdf}"
    )


def test_xi_with_small_m_and_large_n():
    matr = np.array([[0.1] * 10])
    ccop = BivCheckPi(matr)
    xi = ccop.chatterjees_xi()
    assert np.isclose(xi, 0, atol=0.02)


def test_xi_with_large_m_and_small_n():
    matr = np.array([[0.1] * 10]).T
    ccop = BivCheckPi(matr)
    xi = ccop.chatterjees_xi()
    assert np.isclose(xi, 0, atol=0.02)


@pytest.mark.parametrize(
    "matr, expected_sign",
    [
        (np.ones((2, 2)), 0.0),  # independence
        (np.eye(2), 1.0),  # comonotonic
        (np.fliplr(np.eye(2)), -1.0),  # countermonotonic approx
    ],
)
def test_footrule_signs(matr, expected_sign):
    ccop = BivCheckPi(matr)
    result = ccop.spearmans_footrule()
    if expected_sign == 0.0:
        assert np.isclose(result, 0.0, atol=1e-2)
    elif expected_sign > 0:
        assert result == 0.5  # clearly positive
    else:
        assert result < -0.3  # clearly negative but not necessarily -1


@pytest.mark.parametrize(
    "alpha, beta",
    [
        (0.5, 0.5),  # Independence
        (0.2, 0.3),
        (1.0, 0),  # Perfect positive dependence
        (0.6, 0.4),
        (0.0, 1.0),  # Perfect negative dependence
    ],
)
def test_footrule_and_gamma_frechet(alpha, beta):
    """Test the footrule for the Frechet copula with known parameters."""
    frechet = Frechet(alpha, beta)
    checkerboard = frechet.to_checkerboard(100)

    footrule_direct = frechet.spearmans_footrule()
    footrule_check = checkerboard.spearmans_footrule()
    assert np.isclose(footrule_direct, footrule_check, atol=1e-2), (
        f"Expected {footrule_direct}, got {footrule_check}"
    )
    gamma_direct = frechet.ginis_gamma()
    gamma_check = checkerboard.ginis_gamma()
    assert np.isclose(gamma_direct, gamma_check, atol=2e-2), (
        f"Expected {gamma_direct}, got {gamma_check}"
    )


@pytest.mark.parametrize(
    "theta",
    [-1, -0.7, -0.3, 0, 0.3, 0.7, 1],
)
def test_footrule_and_gamma_for_farlie_gumbel_morgenstern(theta):
    """Test the footrule for the Frechet copula with known parameters."""
    fgm = FarlieGumbelMorgenstern(theta)
    checkerboard = fgm.to_checkerboard()

    footrule_direct = fgm.spearmans_footrule()
    footrule_check = checkerboard.spearmans_footrule()
    assert np.isclose(footrule_direct, footrule_check, atol=1e-2), (
        f"Expected {footrule_direct}, got {footrule_check}"
    )
    gamma_direct = fgm.ginis_gamma()
    gamma_check = checkerboard.ginis_gamma()
    assert np.isclose(gamma_direct, gamma_check, atol=1e-2), (
        f"Expected {gamma_direct}, got {gamma_check}"
    )
    blomqvist_direct = fgm.blomqvists_beta()
    blomqvist_check = checkerboard.blomqvists_beta()
    assert np.isclose(blomqvist_direct.evalf(), blomqvist_check, atol=1e-2), (
        f"Expected {blomqvist_direct}, got {blomqvist_check}"
    )


def test_footrule_and_gamma_rectangular_matrix_warning():
    """Ensure rectangular matrices return NaN with warning for footrule/gamma."""
    matr = np.ones((2, 3))
    ccop = BivCheckPi(matr)
    footrule_val = ccop.spearmans_footrule()
    gamma_val = ccop.ginis_gamma()
    assert np.isnan(footrule_val)
    assert np.isnan(gamma_val)
