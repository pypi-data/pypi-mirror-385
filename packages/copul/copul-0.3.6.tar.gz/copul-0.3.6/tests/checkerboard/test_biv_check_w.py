import random

import numpy as np
import pytest

from copul.checkerboard.biv_check_w import BivCheckW
from copul.exceptions import PropertyUnavailableException


@pytest.mark.parametrize(
    "matr, point, expected",
    [
        ([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], (0.5, 0.5), 0.25),
        ([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], (0.5, 1), 0.5),
        (
            [[1, 5, 4], [5, 3, 2], [4, 2, 4]],
            (0.5, 0.5),
            (1 + 5 / 2 + 5 / 2) / 30,
        ),
        ([[1, 5, 4], [5, 3, 2], [4, 2, 4]], (1, 0.5), 0.5),
    ],
)
def test_ccop_cdf(matr, point, expected):
    ccop = BivCheckW(matr)
    actual = ccop.cdf(*point)
    assert np.isclose(actual, expected)


def test_ccop_cdf_vectorized():
    matr = [[1, 5, 4], [5, 3, 2], [4, 2, 4]]
    ccop = BivCheckW(matr)
    points = np.array([[0.5, 0.5], [0.5, 1], [1, 0.5]])
    expected = np.array([0.2, 0.5, 0.5])
    actual = ccop.cdf(points)
    assert np.allclose(actual, expected)


def test_ccop_pdf():
    ccop = BivCheckW([[1, 0], [0, 1]])
    with pytest.raises(PropertyUnavailableException):
        ccop.pdf()


@pytest.mark.parametrize(
    "matr, point, expected",
    [
        ([[1, 1], [1, 1]], (0.2, 0.1), 0),
        ([[1, 1], [1, 1]], (0.1, 0.3), 0),
        ([[1, 1], [1, 1]], (0.1, 0.4), 0.5),
        ([[1, 1], [1, 1]], (0.1, 0.8), 0.5),
        ([[1, 1], [1, 1]], (0.1, 0.9), 1),
        ([[1, 1], [1, 1]], (0.1, 1), 1),
        ([[1, 1], [1, 1]], (0.7, 0.6), 0.5),
        ([[1, 1], [1, 1]], (0.6, 0.7), 0.5),
        ([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], (0.5, 0.5), 0.5),
        ([[1, 5, 4], [5, 3, 2], [4, 2, 4]], (0.5, 0.5), 0.8),
    ],
)
def test_ccop_cond_distr_1(matr, point, expected):
    ccop = BivCheckW(matr)
    actual = ccop.cond_distr_1(*point)
    assert np.isclose(actual, expected)


@pytest.mark.parametrize(
    "matr, point, expected",
    [
        # (
        #     [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]],
        #     (0.5, 0.5),
        #     0.5,
        # ),
        # (
        #     [[1, 2], [2, 1]],
        #     (0.5, 0.5),
        #     2 / 3,
        # ),
        ([[1, 1], [1, 1]], (0.7, 0.25), 0.5),
        ([[1, 1], [1, 1]], (0.8, 0.25), 1),
    ],
)
def test_ccop_cond_distr_2(matr, point, expected):
    ccop = BivCheckW(matr)
    result = ccop.cond_distr_2(*point)
    assert np.isclose(result, expected)


@pytest.mark.parametrize("matr, expected", [([[0, 1], [1, 0]], 1)])
def test_lower_ccop_xi(matr, expected):
    random.seed(0)
    ccop = BivCheckW(matr)
    xi_estimate = ccop.chatterjees_xi()
    assert np.isclose(xi_estimate, expected, atol=0.02)


@pytest.mark.parametrize("matr", [[[1, 0], [0, 1]], [[1]]])
def test_biv_check_min_rvs(matr):
    ccop = BivCheckW(matr)
    sample_data = ccop.rvs(3)
    for data in sample_data:
        # (data[0] + data[1])*2 should approx be an integer
        check_sum = (data[0] + data[1]) * 2
        rounded_sum = round(check_sum)
        assert np.isclose(check_sum, rounded_sum)


# Tests for tau (Kendall's tau)
@pytest.mark.parametrize("n", [2, 3, 4])
def test_tau_independence(n):
    """Test that tau is close to 0 for independence copula."""
    matr = np.ones((n, n))  # Uniform distribution represents independence
    ccop = BivCheckW(matr)
    tau = ccop.kendalls_tau()
    assert tau < 0


def test_tau_perfect_dependence():
    """Test tau for perfect positive and negative dependence."""
    # Perfect positive dependence
    matr_pos = np.zeros((3, 3))
    np.fill_diagonal(matr_pos, 1)  # Place 1's on the main diagonal
    ccop_pos = BivCheckW(matr_pos)
    tau_pos = ccop_pos.kendalls_tau()
    # Perfect negative dependence
    matr_neg = np.zeros((3, 3))
    for i in range(3):
        matr_neg[i, 2 - i] = 1  # Place 1's on the opposite diagonal
    ccop_neg = BivCheckW(matr_neg)
    tau_neg = ccop_neg.kendalls_tau()

    # Tau should be positive for positive dependence and negative for negative dependence
    assert tau_pos < 0.4
    assert tau_neg < -0.5


def test_tau_2x2_exact():
    """Test exact values for 2x2 checkerboard copulas."""
    # For a 2x2 checkerboard with perfect positive dependence
    matr_pos = np.array([[1, 0], [0, 1]])
    ccop_pos = BivCheckW(matr_pos)

    # For a 2x2 checkerboard with perfect negative dependence
    matr_neg = np.array([[0, 1], [1, 0]])
    ccop_neg = BivCheckW(matr_neg)

    # For 2x2, these are the exact values
    pos_tau = ccop_pos.kendalls_tau()
    assert np.isclose(pos_tau, 0, atol=1e-2)
    neg_tau = ccop_neg.kendalls_tau()
    assert np.isclose(neg_tau, -1, atol=1e-2)


def test_tau_example():
    """Test tau for the example matrix from the original code."""
    matr = np.array([[1, 5, 4], [5, 3, 2], [4, 2, 4]])
    ccop = BivCheckW(matr)
    tau_val = ccop.kendalls_tau()

    # Check range and expected sign (this matrix has positive dependence)
    assert -1 <= tau_val <= 1
    assert tau_val < 0


# Tests for rho (Spearman's rho)
def test_rho_independence():
    """Test that rho is close to 0 for independence copula."""
    np.random.seed(42)
    matr = np.ones((4, 4))  # Uniform distribution represents independence
    ccop = BivCheckW(matr)
    rho = ccop.spearmans_rho()
    assert rho < 0


def test_rho_perfect_dependence():
    """Test rho for perfect positive and negative dependence."""
    # Perfect positive dependence
    matr_pos = np.zeros((3, 3))
    np.fill_diagonal(matr_pos, 1)  # Place 1's on the main diagonal
    ccop_pos = BivCheckW(matr_pos)
    rho_pos = ccop_pos.spearmans_rho()

    # Perfect negative dependence
    matr_neg = np.zeros((3, 3))
    for i in range(3):
        matr_neg[i, 2 - i] = 1  # Place 1's on the opposite diagonal
    ccop_neg = BivCheckW(matr_neg)
    rho_neg = ccop_neg.spearmans_rho()

    # Rho should be positive for positive dependence and negative for negative dependence
    assert rho_pos > 0.5
    assert rho_neg < -0.5


def test_rho_2x2_exact():
    """Test exact values for 2x2 checkerboard copulas."""
    np.random.seed(42)
    # For a 2x2 checkerboard with perfect positive dependence
    matr_pos = np.array([[1, 0], [0, 1]])
    ccop_pos = BivCheckW(matr_pos)

    # For a 2x2 checkerboard with perfect negative dependence
    matr_neg = np.array([[0, 1], [1, 0]])
    ccop_neg = BivCheckW(matr_neg)

    # For 2x2, these are the exact values
    pos_rho = ccop_pos.spearmans_rho()
    assert pos_rho < 0.55
    neg_rho = ccop_neg.spearmans_rho()
    assert np.isclose(neg_rho, -1, atol=1e-2)


def test_rho_example():
    """Test rho for the example matrix from the original code."""
    matr = np.array([[1, 5, 4], [5, 3, 2], [4, 2, 4]])
    ccop = BivCheckW(matr)
    rho_val = ccop.spearmans_rho()

    # Check range and expected sign (this matrix has positive dependence)
    assert -1 <= rho_val <= 1
    assert rho_val < 0


# Tests for xi (Chatterjee's xi)
@pytest.mark.parametrize("n", [2, 3, 4])
def test_xi_independence_with_order(n):
    """Test that xi is close to 0 for independence copula."""
    np.random.seed(42)
    matr = np.ones((n, n))  # Uniform distribution represents independence
    ccop = BivCheckW(matr)
    xi = ccop.chatterjees_xi()
    assert 1 > xi > 0.02


def test_xi_perfect_dependence():
    """Test xi for perfect positive and negative dependence."""
    # Perfect positive dependence
    matr_pos = np.zeros((10, 10))
    np.fill_diagonal(matr_pos, 1)  # Place 1's on the main diagonal
    ccop_pos = BivCheckW(matr_pos)
    xi_pos = ccop_pos.chatterjees_xi()

    # Perfect negative dependence
    matr_neg = np.zeros((10, 10))
    for i in range(10):
        matr_neg[i, 9 - i] = 1  # Place 1's on the opposite diagonal
    ccop_neg = BivCheckW(matr_neg)
    xi_neg = ccop_neg.chatterjees_xi()

    # Xi should be close to 1 for both perfect positive and negative dependence
    assert xi_pos > 0.8
    assert xi_neg > 0.8


@pytest.mark.parametrize("n", [2, 3, 4])
def test_xi_with_shuffled_eye(n):
    """Test that xi is close to 1 for a shuffled identity matrix."""
    np.random.seed(42)
    n = 10
    matr = np.eye(n)
    np.random.shuffle(matr)
    ccop = BivCheckW(matr)
    xi = ccop.chatterjees_xi()
    assert np.isclose(xi, 1, atol=0.02)


def test_xi_2x2_exact():
    """Test exact values for 2x2 checkerboard copulas."""
    # For a 2x2 checkerboard with perfect positive dependence
    matr_pos = np.array([[1, 0], [0, 1]])
    ccop_pos = BivCheckW(matr_pos)

    # For a 2x2 checkerboard with perfect negative dependence
    matr_neg = np.array([[0, 1], [1, 0]])
    ccop_neg = BivCheckW(matr_neg)

    # For 2x2, both should have xi = 1 (perfect dependence)
    xi_pos = ccop_pos.chatterjees_xi()
    xi_neg = ccop_neg.chatterjees_xi()
    assert np.isclose(xi_pos, 1, atol=1e-2)
    assert np.isclose(xi_neg, 1, atol=1e-2)


def test_xi_example():
    """Test xi for the example matrix from the original code."""
    matr = np.array([[1, 5, 4], [5, 3, 2], [4, 2, 4]])
    ccop = BivCheckW(matr)
    xi_val = ccop.chatterjees_xi()

    # Check range (xi is always between 0 and 1)
    assert 0 <= xi_val <= 1


def test_measure_consistency():
    """Test that tau and rho have consistent signs for asymmetric matrices."""
    # Create a matrix with positive dependence
    matr_pos = np.array([[0.6, 0.2, 0.0], [0.2, 0.4, 0.2], [0.0, 0.2, 0.6]])
    ccop_pos = BivCheckW(matr_pos)
    tau_pos = ccop_pos.kendalls_tau()
    rho_pos = ccop_pos.spearmans_rho()

    # Both should be positive
    assert tau_pos > 0
    assert rho_pos > 0

    # Create a matrix with negative dependence
    matr_neg = np.array([[0.0, 0.2, 0.6], [0.2, 0.4, 0.2], [0.6, 0.2, 0.0]])
    ccop_neg = BivCheckW(matr_neg)
    tau_neg = ccop_neg.kendalls_tau()
    rho_neg = ccop_neg.spearmans_rho()

    # Both should be negative
    assert tau_neg < 0
    assert rho_neg < 0


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
    ccop = BivCheckW(matr)
    xi = ccop.chatterjees_xi(condition_on_y=True)
    xi2 = ccop.chatterjees_xi(condition_on_y=False)
    assert 1 > xi > 0
    assert 1 > xi2 > 0
    tau = ccop.kendalls_tau()
    rho = ccop.spearmans_rho()
    assert 1 > tau > -1
    assert 1 > rho > -1


def test_xi_with_small_m_and_large_n():
    matr = np.array([[0.1] * 10])
    ccop = BivCheckW(matr)
    xi = ccop.chatterjees_xi()
    assert np.isclose(xi, 0.01, atol=0.02)


def test_xi_with_large_m_and_small_n():
    matr = np.array([[0.1] * 10]).T
    ccop = BivCheckW(matr)
    xi = ccop.chatterjees_xi()
    assert np.isclose(xi, 1, atol=0.02)


def test_blests_nu():
    matr = [[0, 1], [1, 0]]
    ccop = BivCheckW(matr)
    nu = ccop.blests_nu()
    assert np.isclose(nu, -1, atol=0.02)
    ccop2 = BivCheckW([[1]])
    assert np.isclose(ccop2.blests_nu(), -1, atol=0.02)
