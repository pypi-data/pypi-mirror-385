import numpy as np
import pandas as pd
import pytest
from .Normalization import (
    Linear_Max_Min,
    Linear_Max,
    Linear_sum,
    Vector_Normalization,
    Logarithmic_normalisation,
)
from .main import TOPSIS


@pytest.fixture
def sample_data():
    return np.array([1, 2, 3, 4, 5])


def test_linear_max_min_profit(sample_data):
    expected = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    result = Linear_Max_Min(sample_data, "profit")
    np.testing.assert_allclose(result, expected)


def test_linear_max_min_cost(sample_data):
    expected = np.array([1.0, 0.75, 0.5, 0.25, 0.0])
    result = Linear_Max_Min(sample_data, "cost")
    np.testing.assert_allclose(result, expected)


def test_linear_max_profit(sample_data):
    expected = np.array([0.2, 0.4, 0.6, 0.8, 1.0])
    result = Linear_Max(sample_data, "profit")
    np.testing.assert_allclose(result, expected)


def test_linear_max_cost(sample_data):
    expected = np.array([0.8, 0.6, 0.4, 0.2, 0.0])
    result = Linear_Max(sample_data, "cost")
    np.testing.assert_allclose(result, expected)


def test_linear_sum_profit(sample_data):
    expected = np.array([0.066667, 0.133333, 0.2, 0.266667, 0.333333])
    result = Linear_sum(sample_data, "profit")
    np.testing.assert_allclose(result, expected, rtol=1e-5)


def test_linear_sum_cost(sample_data):
    expected = np.array([0.437956, 0.218978, 0.145985, 0.109489, 0.087591])
    result = Linear_sum(sample_data, "cost")
    np.testing.assert_allclose(result, expected, rtol=1e-5)


def test_vector_normalization_profit(sample_data):
    expected = np.array([0.13484, 0.26968, 0.40452, 0.53936, 0.6742])
    result = Vector_Normalization(sample_data, "profit")
    np.testing.assert_allclose(result, expected, rtol=1e-5)


def test_vector_normalization_cost(sample_data):
    expected = np.array([0.86516, 0.73032, 0.59548, 0.46064, 0.3258])
    result = Vector_Normalization(sample_data, "cost")
    np.testing.assert_allclose(result, expected, rtol=1e-5)


def test_logarithmic_normalisation_profit(sample_data):
    expected = np.array([0.0, 0.144783, 0.229476, 0.289566, 0.336176])
    result = Logarithmic_normalisation(sample_data, "profit")
    np.testing.assert_allclose(result, expected, rtol=1e-5)


def test_logarithmic_normalisation_cost(sample_data):
    expected = np.array([0.25, 0.213804, 0.192631, 0.177609, 0.165956])
    result = Logarithmic_normalisation(sample_data, "cost")
    np.testing.assert_allclose(result, expected, rtol=1e-5)


def test_topsis_main_function():
    decision_matrix = pd.DataFrame([[2, 3], [4, 1]], columns=["C1", "C2"])
    weights = [0.5, 0.5]
    attribute_type = [1, 0]  # 1 for profit, 0 for cost
    expected_performance_score = np.array([0.6, 0.4])

    result = TOPSIS(decision_matrix, weights, attribute_type)
    np.testing.assert_allclose(result, expected_performance_score, rtol=1e-3)
