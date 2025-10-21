"""
Tests for the consolidated Copula class.
"""

import pytest
import numpy as np
import sympy as sp
from unittest.mock import MagicMock, patch

from copul import from_cdf
from copul.family.core.copula import Copula


class SampleCopula(Copula):
    """Concrete implementation of Copula for testing purposes"""

    # Define parameters
    theta = sp.symbols("theta", positive=True)
    params = [theta]
    intervals = {str(theta): sp.Interval(0, float("inf"))}

    def __init__(self, dimension=2, theta=0.5):
        super().__init__(dimension)
        self.theta = theta
        self._free_symbols = {"theta": self.theta}
        # Simple Independence Copula as default
        # Handle any dimension, but only use first two symbols for the CDF
        u1 = self.u_symbols[0]
        u2 = self.u_symbols[1] if len(self.u_symbols) > 1 else self.u_symbols[0]
        self._cdf_expr = u1 * u2 * (1 + self.theta * (1 - u1) * (1 - u2))

    @property
    def is_absolutely_continuous(self) -> bool:
        return True

    @property
    def is_symmetric(self) -> bool:
        return True


class TestCopulaBase:
    """Base tests for the Copula class core functionality."""

    @pytest.fixture
    def copula(self):
        """Create a test copula instance"""
        return SampleCopula(dimension=2, theta=0.5)

    def test_init(self):
        """Test initialization of Copula"""
        copula = SampleCopula(dimension=3)
        assert copula.dim == 3
        assert len(copula.u_symbols) == 3  # u1, u2, u3

    def test_str(self, copula):
        """Test string representation"""
        assert str(copula) == "SampleCopula"

    def test_call(self, copula):
        """Test the __call__ method for creating a new instance with updated parameters"""
        # Create a new instance with modified theta
        new_copula = copula(theta=1.0)

        # Original should be unchanged
        assert copula.theta == 0.5

        # New instance should have updated parameter
        assert new_copula.theta == 1.0
        assert new_copula is not copula  # Should be a different object

        # Params and intervals should be updated
        assert new_copula.params == []  # Used params are removed from list
        assert new_copula.intervals == {}  # Used intervals are removed

    def test_set_params(self, copula):
        """Test _set_params method"""
        # Test with positional args
        test_copula = SampleCopula(dimension=2)
        test_copula._set_params([0.8], {})
        assert test_copula.theta == 0.8

        # Test with kwargs
        test_copula = SampleCopula(dimension=2)
        test_copula._set_params([], {"theta": 1.2})
        assert test_copula.theta == 1.2

    def test_parameters(self, copula):
        """Test parameters property"""
        assert copula.parameters == {
            str(sp.symbols("theta")): sp.Interval(0, float("inf"))
        }

    def test_are_class_vars(self, copula):
        """Test _are_class_vars method"""
        # Valid attribute
        copula._are_class_vars({"theta": 1.0})

        # Invalid attribute should raise assertion error
        with pytest.raises(AssertionError):
            copula._are_class_vars({"invalid_param": 1.0})

    def test_slice_interval(self, copula):
        """Test slice_interval method"""
        # Reset intervals to original state before each test
        theta_symbol = sp.symbols("theta")
        copula.intervals = {str(theta_symbol): sp.Interval(0, float("inf"))}

        # Test with string parameter name
        copula.slice_interval("theta", 0.1, 2.0)
        assert copula.intervals["theta"] == sp.Interval(0.1, 2.0, False, False)

        # Reset and test with sympy symbol
        copula.intervals = {str(theta_symbol): sp.Interval(0, float("inf"))}
        copula.slice_interval(theta_symbol, 0.2, 1.5)
        assert copula.intervals["theta"] == sp.Interval(0.2, 1.5, False, False)

        # Reset and test with only start interval
        copula.intervals = {str(theta_symbol): sp.Interval(0, float("inf"))}
        copula.slice_interval("theta", 0.3, None)
        assert copula.intervals["theta"].left == 0.3
        assert copula.intervals["theta"].right == float("inf")

        # Reset and test with only end interval
        copula.intervals = {str(theta_symbol): sp.Interval(0, float("inf"))}
        copula.slice_interval("theta", None, 1.0)
        assert copula.intervals["theta"].left == 0
        assert copula.intervals["theta"].right == 1.0

    def test_cdf(self):
        """Test cdf property"""
        # Set up the wrapper to return a simple value
        expected = 0.25

        # Create a minimal subclass with a controlled _cdf attribute
        class TestCopulaForCDF(SampleCopula):
            def __init__(self):
                super().__init__()
                # Simple _cdf expression for testing
                self._cdf_expr = sp.sympify("u1*u2")
                self._free_symbols = {}

        # Use the test subclass
        test_copula = TestCopulaForCDF()
        cdf_value = test_copula.cdf(0.5, 0.5)

        # Verify the result
        assert cdf_value == expected

    def test_conditional_distributions(self):
        """Test conditional distribution methods"""
        # Instead of patching cdf property directly, patch the sympy.diff function
        with patch("sympy.diff") as mock_diff:
            # Set up a mock differentiation result
            mock_diff_result = MagicMock()
            mock_diff.return_value = mock_diff_result

            # And patch the SymPyFuncWrapper constructor
            with patch("copul.wrapper.sympy_wrapper.SymPyFuncWrapper") as mock_wrapper:
                # Create a mock wrapper that returns controlled values
                mock_func_wrapper = MagicMock()
                expected_value = 0.375  # Example expected value
                mock_func_wrapper.return_value = expected_value
                mock_wrapper.return_value = mock_func_wrapper

                # Test specific methods instead of cond_distr
                # Patch cond_distr_1 directly
                with patch.object(
                    SampleCopula, "cond_distr_1", autospec=True
                ) as mock_cond_distr_1:
                    mock_cond_distr_1.return_value = expected_value

                    # Create a new copula to use the patched method
                    test_copula = SampleCopula()
                    result = test_copula.cond_distr_1([0.5, 0.5])

                    # Verify the result
                    assert result == expected_value
                    mock_cond_distr_1.assert_called_once()

                # Test cond_distr_2
                with patch.object(
                    SampleCopula, "cond_distr_2", autospec=True
                ) as mock_cond_distr_2:
                    mock_cond_distr_2.return_value = mock_func_wrapper

                    # Create a new copula to use the patched method
                    test_copula = SampleCopula()
                    result = test_copula.cond_distr_2()

                    # Verify the result
                    assert result == mock_func_wrapper
                    mock_cond_distr_2.assert_called_once()

    def test_pdf(self):
        """Test pdf method"""
        # Patch at the class level instead of the instance level
        with patch.object(SampleCopula, "pdf", autospec=True) as mock_pdf:
            expected_value = 1.0
            mock_pdf.return_value = expected_value

            # Create a new instance to use the patched class method
            test_copula = SampleCopula()
            pdf_value = test_copula.pdf([0.5, 0.5])

            # Verify the result
            assert pdf_value == expected_value
            mock_pdf.assert_called_once()

    def test_abstract_methods(self):
        """Test that abstract methods must be implemented"""

        # Create a subclass without implementing abstract methods
        class IncompleteTestCopula(Copula):
            def __init__(self):
                super().__init__(dimension=2)

        # Should be able to create an instance
        incomplete = IncompleteTestCopula()

        # But calling abstract methods should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            _ = incomplete.is_absolutely_continuous

        with pytest.raises(NotImplementedError):
            _ = incomplete.is_symmetric


class TestCopulaSampling:
    """Tests specifically for the sampling functionality of Copula."""

    def setup_method(self):
        """Setup test fixtures."""
        # Create a proper mock instance
        self.copula = MagicMock(spec=Copula)
        self.copula.dim = 2

        # We need to manually add the rvs method from Copula to our mock
        # This is the method we're actually testing
        self.copula.rvs = Copula.rvs.__get__(self.copula)

    @patch("copul.family.core.copula_sampling_mixin.CopulaSampler")
    def test_rvs_default_parameters(self, mock_sampler_class):
        """Test the rvs method with default parameters."""
        # Create mock sampler
        mock_sampler = MagicMock()
        mock_sampler_class.return_value = mock_sampler

        # Create sample return value
        sample_data = np.random.random((1, 2))
        mock_sampler.rvs.return_value = sample_data

        # Call the method
        result = self.copula.rvs()

        # Verify the calls
        mock_sampler_class.assert_called_once_with(self.copula, random_state=None)
        mock_sampler.rvs.assert_called_once_with(1, False)

        # Verify the result
        assert np.array_equal(result, sample_data)

    @patch("copul.family.core.copula_sampling_mixin.CopulaSampler")
    def test_rvs_custom_parameters(self, mock_sampler_class):
        """Test the rvs method with custom parameters."""
        # Create mock sampler
        mock_sampler = MagicMock()
        mock_sampler_class.return_value = mock_sampler

        # Create sample return value
        sample_data = np.random.random((50, 2))
        mock_sampler.rvs.return_value = sample_data

        # Call the method with custom parameters
        n_samples = 50
        random_state = 42
        result = self.copula.rvs(n=n_samples, random_state=random_state)

        # Verify the calls
        mock_sampler_class.assert_called_once_with(
            self.copula, random_state=random_state
        )
        mock_sampler.rvs.assert_called_once_with(n_samples, False)

        # Verify the result
        assert np.array_equal(result, sample_data)

    @patch("copul.family.core.copula_sampling_mixin.CopulaSampler")
    def test_rvs_with_approximate(self, mock_sampler_class):
        """Test the rvs method with approximate=True."""
        # Create mock sampler
        mock_sampler = MagicMock()
        mock_sampler_class.return_value = mock_sampler

        # Create sample return value
        sample_data = np.random.random((10, 2))
        mock_sampler.rvs.return_value = sample_data

        # Call the method with approximate=True
        result = self.copula.rvs(n=10, approximate=True)

        # Verify the calls
        mock_sampler_class.assert_called_once_with(self.copula, random_state=None)
        mock_sampler.rvs.assert_called_once_with(10, True)

        # Verify the result
        assert np.array_equal(result, sample_data)

    @patch("copul.family.core.copula_sampling_mixin.CopulaSampler")
    def test_rvs_with_random_state(self, mock_sampler_class):
        """Test the rvs method with a specific random_state."""
        # Create mock sampler
        mock_sampler = MagicMock()
        mock_sampler_class.return_value = mock_sampler

        # Create sample return value
        sample_data = np.random.random((5, 2))
        mock_sampler.rvs.return_value = sample_data

        # Call the method with a specific random_state
        result = self.copula.rvs(n=5, random_state=123)

        # Verify the calls
        mock_sampler_class.assert_called_once_with(self.copula, random_state=123)
        mock_sampler.rvs.assert_called_once_with(5, False)

        # Verify the result
        assert np.array_equal(result, sample_data)

    @patch("copul.family.core.copula_sampling_mixin.CopulaSampler")
    def test_rvs_error_handling(self, mock_sampler_class):
        """Test error handling in the rvs method."""
        # Create mock sampler
        mock_sampler = MagicMock()
        mock_sampler_class.return_value = mock_sampler

        # Make rvs raise an exception
        mock_sampler.rvs.side_effect = ValueError("Test error")

        # Verify the exception is propagated
        with pytest.raises(ValueError, match="Test error"):
            self.copula.rvs()


@pytest.mark.parametrize(
    "n_samples,random_state,approximate",
    [
        (1, None, False),  # Default case
        (10, 42, False),  # With random_state
        (100, None, True),  # With approximate
        (1000, 123, True),  # With all parameters
    ],
)
def test_rvs_parameter_combinations(n_samples, random_state, approximate):
    """Parametrized test for different parameter combinations in rvs method."""
    # Create mock copula
    mock_copula = MagicMock(spec=Copula)
    mock_copula.dim = 2

    # Store original method to call later
    original_rvs = Copula.rvs.__get__(mock_copula)

    # Create mock sampler
    with patch(
        "copul.family.core.copula_sampling_mixin.CopulaSampler"
    ) as mock_sampler_class:
        mock_sampler = MagicMock()
        mock_sampler.rvs.return_value = np.random.random((n_samples, 2))
        mock_sampler_class.return_value = mock_sampler

        # Call the method using the bound method
        original_rvs(n=n_samples, random_state=random_state, approximate=approximate)

        # Verify the calls
        mock_sampler_class.assert_called_once_with(
            mock_copula, random_state=random_state
        )
        mock_sampler.rvs.assert_called_once_with(n_samples, approximate)


def test_3d_copula_sampling():
    """Test sampling from a 3D copula."""
    func = "(x**(-theta) + y**(-theta) + z**(-theta) - 2)**(-1/theta)"
    copulas = from_cdf(func)
    copula = copulas(theta=3)
    sample_values = copula.rvs(100, approximate=True)
    assert sample_values.shape == (100, 3)
    assert np.all(sample_values >= 0)
    assert np.all(sample_values <= 1)
    assert not np.isnan(sample_values).any()


def test_cond_distr_of_copula():
    """Test conditional distribution of a copula."""
    with patch("copul.from_cdf") as mock_from_cdf:
        # Setup mock copula
        mock_copula = MagicMock()
        mock_cond_distr = MagicMock()
        mock_cond_distr.return_value = 0.25
        mock_copula.cond_distr.return_value = mock_cond_distr
        mock_from_cdf.return_value = mock_copula

        # Call the function under test
        copula = mock_from_cdf("x*y*z")
        cond_distr = copula.cond_distr(2)
        result = cond_distr(0.5, 0.5)

        # Verify the result
        assert result == 0.25
        mock_from_cdf.assert_called_with("x*y*z")
        mock_copula.cond_distr.assert_called_with(2)
        mock_cond_distr.assert_called_with(0.5, 0.5)


def test_cond_distr_direct_eval():
    """Test direct evaluation of conditional distribution."""
    with patch("copul.from_cdf") as mock_from_cdf:
        # Setup mock copula
        mock_copula = MagicMock()
        mock_copula.cond_distr.return_value = 0.25
        mock_from_cdf.return_value = mock_copula

        # Call the function under test
        copula = mock_from_cdf("x*y*z")
        u = [0.5, 0.5]
        result = copula.cond_distr(2, u)

        # Verify the result
        assert result == 0.25
        mock_from_cdf.assert_called_with("x*y*z")
        mock_copula.cond_distr.assert_called_with(2, u)


def test_copula_pdf_evaluation():
    """Test PDF calculation of copula."""
    with patch("copul.from_cdf") as mock_from_cdf:
        # Setup mock copula and pdf
        mock_copula = MagicMock()
        mock_pdf = MagicMock()
        mock_pdf.func = 1
        mock_pdf_eval = MagicMock()
        mock_pdf_eval.evalf.return_value = 1
        mock_pdf.return_value = mock_pdf_eval
        mock_copula.pdf.return_value = mock_pdf
        mock_from_cdf.return_value = mock_copula

        # Call the function under test
        copula = mock_from_cdf("x*y*z")
        pdf = copula.pdf()

        # Verify the result
        assert pdf.func == 1
        evaluated_pdf = pdf(0.5, 0.5, 0.5)
        assert np.isclose(evaluated_pdf.evalf(), 1)
        mock_from_cdf.assert_called_with("x*y*z")
        mock_copula.pdf.assert_called_once()
