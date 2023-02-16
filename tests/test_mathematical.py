import pytest
from .helper import get_all_dtypes

import dpnp

import numpy
from numpy.testing import (
    assert_allclose,
    assert_array_almost_equal,
    assert_array_equal,
    assert_raises
)


@pytest.mark.usefixtures("allow_fall_back_on_numpy")
class TestConvolve:
    def test_object(self):
        d = [1.] * 100
        k = [1.] * 3
        assert_array_almost_equal(dpnp.convolve(d, k)[2:-2], dpnp.full(98, 3))

    def test_no_overwrite(self):
        d = dpnp.ones(100)
        k = dpnp.ones(3)
        dpnp.convolve(d, k)
        assert_array_equal(d, dpnp.ones(100))
        assert_array_equal(k, dpnp.ones(3))

    def test_mode(self):
        d = dpnp.ones(100)
        k = dpnp.ones(3)
        default_mode = dpnp.convolve(d, k, mode='full')
        full_mode = dpnp.convolve(d, k, mode='f')
        assert_array_equal(full_mode, default_mode)
        # integer mode
        with assert_raises(ValueError):
            dpnp.convolve(d, k, mode=-1)
        assert_array_equal(dpnp.convolve(d, k, mode=2), full_mode)
        # illegal arguments
        with assert_raises(TypeError):
            dpnp.convolve(d, k, mode=None)


@pytest.mark.usefixtures("allow_fall_back_on_numpy")
@pytest.mark.parametrize("array",
                         [[[0, 0], [0, 0]],
                          [[1, 2], [1, 2]],
                          [[1, 2], [3, 4]],
                          [[[1, 2], [3, 4]], [[1, 2], [2, 1]], [[1, 3], [3, 1]]],
                          [[[[1, 2], [3, 4]], [[1, 2], [2, 1]]], [[[1, 3], [3, 1]], [[0, 1], [1, 3]]]]
                          ],
                         ids=['[[0, 0], [0, 0]]',
                              '[[1, 2], [1, 2]]',
                              '[[1, 2], [3, 4]]',
                              '[[[1, 2], [3, 4]], [[1, 2], [2, 1]], [[1, 3], [3, 1]]]',
                              '[[[[1, 2], [3, 4]], [[1, 2], [2, 1]]], [[[1, 3], [3, 1]], [[0, 1], [1, 3]]]]'
                              ])
def test_diff(array):
    np_a = numpy.array(array)
    dpnp_a = dpnp.array(array)
    expected = numpy.diff(np_a)
    result = dpnp.diff(dpnp_a)
    assert_allclose(expected, result)


@pytest.mark.parametrize("dtype1", get_all_dtypes())
@pytest.mark.parametrize("dtype2", get_all_dtypes())
@pytest.mark.parametrize("func",
                         ['add', 'multiply', 'subtract', 'divide'])
@pytest.mark.parametrize("data",
                         [[[1, 2], [3, 4]]],
                         ids=['[[1, 2], [3, 4]]'])
def test_op_multiple_dtypes(dtype1, func, dtype2, data):
    np_a = numpy.array(data, dtype=dtype1)
    dpnp_a = dpnp.array(data, dtype=dtype1)

    np_b = numpy.array(data, dtype=dtype2)
    dpnp_b = dpnp.array(data, dtype=dtype2)

    if func == 'subtract' and (dtype1 == dtype2 == dpnp.bool):
        with pytest.raises(TypeError):
            result = getattr(dpnp, func)(dpnp_a, dpnp_b)
            expected = getattr(numpy, func)(np_a, np_b)
    else:
        result = getattr(dpnp, func)(dpnp_a, dpnp_b)
        expected = getattr(numpy, func)(np_a, np_b)
        assert_array_equal(result, expected)


@pytest.mark.parametrize("rhs", [[[1, 2, 3], [4, 5, 6]], [2.0, 1.5, 1.0], 3, 0.3])
@pytest.mark.parametrize("lhs", [[[6, 5, 4], [3, 2, 1]], [1.3, 2.6, 3.9]])
# TODO: achieve the same level of dtype support for all mathematical operations, like
# @pytest.mark.parametrize("dtype", get_all_dtypes())
# and to get rid of fallbacks on numpy allowed by below fixture
# @pytest.mark.usefixtures("allow_fall_back_on_numpy")
class TestMathematical:

    @staticmethod
    def array_or_scalar(xp, data, dtype=None):
        if numpy.isscalar(data):
            return data

        return xp.array(data, dtype=dtype)

    def _test_mathematical(self, name, dtype, lhs, rhs):
        a_dpnp = self.array_or_scalar(dpnp, lhs, dtype=dtype)
        b_dpnp = self.array_or_scalar(dpnp, rhs, dtype=dtype)

        a_np = self.array_or_scalar(numpy, lhs, dtype=dtype)
        b_np = self.array_or_scalar(numpy, rhs, dtype=dtype)

        if name == 'subtract' and not numpy.isscalar(rhs) and dtype == dpnp.bool:
            with pytest.raises(TypeError):
                result = getattr(dpnp, name)(a_dpnp, b_dpnp)
                expected = getattr(numpy, name)(a_np, b_np)
        else:
            result = getattr(dpnp, name)(a_dpnp, b_dpnp)
            expected = getattr(numpy, name)(a_np, b_np)
            assert_allclose(result, expected, atol=1e-4)

    @pytest.mark.parametrize("dtype", get_all_dtypes())
    def test_add(self, dtype, lhs, rhs):
        self._test_mathematical('add', dtype, lhs, rhs)

    @pytest.mark.usefixtures("allow_fall_back_on_numpy")
    @pytest.mark.parametrize("dtype", get_all_dtypes(no_bool=True, no_complex=True))
    def test_arctan2(self, dtype, lhs, rhs):
        self._test_mathematical('arctan2', dtype, lhs, rhs)

    @pytest.mark.usefixtures("allow_fall_back_on_numpy")
    @pytest.mark.parametrize("dtype", get_all_dtypes(no_bool=True, no_complex=True))
    def test_copysign(self, dtype, lhs, rhs):
        self._test_mathematical('copysign', dtype, lhs, rhs)

    @pytest.mark.parametrize("dtype", get_all_dtypes())
    def test_divide(self, dtype, lhs, rhs):
        self._test_mathematical('divide', dtype, lhs, rhs)

    @pytest.mark.usefixtures("allow_fall_back_on_numpy")
    @pytest.mark.parametrize("dtype", get_all_dtypes(no_bool=True, no_complex=True))
    def test_fmod(self, dtype, lhs, rhs):
        self._test_mathematical('fmod', dtype, lhs, rhs)

    @pytest.mark.usefixtures("allow_fall_back_on_numpy")
    @pytest.mark.parametrize("dtype", get_all_dtypes(no_bool=True, no_complex=True))
    def test_floor_divide(self, dtype, lhs, rhs):
        self._test_mathematical('floor_divide', dtype, lhs, rhs)

    @pytest.mark.usefixtures("allow_fall_back_on_numpy")
    @pytest.mark.parametrize("dtype", get_all_dtypes(no_bool=True, no_complex=True))
    def test_hypot(self, dtype, lhs, rhs):
        self._test_mathematical('hypot', dtype, lhs, rhs)

    @pytest.mark.usefixtures("allow_fall_back_on_numpy")
    @pytest.mark.parametrize("dtype", get_all_dtypes(no_bool=True, no_complex=True))
    def test_maximum(self, dtype, lhs, rhs):
        self._test_mathematical('maximum', dtype, lhs, rhs)

    @pytest.mark.usefixtures("allow_fall_back_on_numpy")
    @pytest.mark.parametrize("dtype", get_all_dtypes(no_bool=True, no_complex=True))
    def test_minimum(self, dtype, lhs, rhs):
        self._test_mathematical('minimum', dtype, lhs, rhs)

    @pytest.mark.parametrize("dtype", get_all_dtypes())
    def test_multiply(self, dtype, lhs, rhs):
        self._test_mathematical('multiply', dtype, lhs, rhs)

    @pytest.mark.usefixtures("allow_fall_back_on_numpy")
    @pytest.mark.parametrize("dtype", get_all_dtypes(no_bool=True, no_complex=True))
    def test_remainder(self, dtype, lhs, rhs):
        self._test_mathematical('remainder', dtype, lhs, rhs)

    @pytest.mark.usefixtures("allow_fall_back_on_numpy")
    @pytest.mark.parametrize("dtype", get_all_dtypes(no_bool=True, no_complex=True))
    def test_power(self, dtype, lhs, rhs):
        self._test_mathematical('power', dtype, lhs, rhs)

    @pytest.mark.parametrize("dtype", get_all_dtypes())
    def test_subtract(self, dtype, lhs, rhs):
        self._test_mathematical('subtract', dtype, lhs, rhs)


@pytest.mark.usefixtures("suppress_divide_invalid_numpy_warnings")
@pytest.mark.parametrize("val_type",
                         [bool, int, float],
                         ids=['bool', 'int', 'float'])
@pytest.mark.parametrize("data_type", get_all_dtypes())
@pytest.mark.parametrize("func",
                         ['add', 'multiply', 'subtract', 'divide'])
@pytest.mark.parametrize("val",
                         [0, 1, 5],
                         ids=['0', '1', '5'])
@pytest.mark.parametrize("array",
                         [[[0, 0], [0, 0]],
                          [[1, 2], [1, 2]],
                          [[1, 2], [3, 4]],
                          [[[1, 2], [3, 4]], [[1, 2], [2, 1]], [[1, 3], [3, 1]]],
                          [[[[1, 2], [3, 4]], [[1, 2], [2, 1]]], [[[1, 3], [3, 1]], [[0, 1], [1, 3]]]]],
                         ids=['[[0, 0], [0, 0]]',
                              '[[1, 2], [1, 2]]',
                              '[[1, 2], [3, 4]]',
                              '[[[1, 2], [3, 4]], [[1, 2], [2, 1]], [[1, 3], [3, 1]]]',
                              '[[[[1, 2], [3, 4]], [[1, 2], [2, 1]]], [[[1, 3], [3, 1]], [[0, 1], [1, 3]]]]'])
def test_op_with_scalar(array, val, func, data_type, val_type):
    np_a = numpy.array(array, dtype=data_type)
    dpnp_a = dpnp.array(array, dtype=data_type)
    val_ = val_type(val)

    if func == 'subtract' and val_type == bool and data_type == dpnp.bool:
        with pytest.raises(TypeError):
            result = getattr(dpnp, func)(dpnp_a, val_)
            expected = getattr(numpy, func)(np_a, val_)

            result = getattr(dpnp, func)(val_, dpnp_a)
            expected = getattr(numpy, func)(val_, np_a)
    else:
        result = getattr(dpnp, func)(dpnp_a, val_)
        expected = getattr(numpy, func)(np_a, val_)
        assert_allclose(result, expected)

        result = getattr(dpnp, func)(val_, dpnp_a)
        expected = getattr(numpy, func)(val_, np_a)
        assert_allclose(result, expected)


@pytest.mark.parametrize("shape",
                         [(), (3, 2)],
                         ids=['()', '(3, 2)'])
@pytest.mark.parametrize("dtype", get_all_dtypes())
def test_multiply_scalar(shape, dtype):
    np_a = numpy.ones(shape, dtype=dtype)
    dpnp_a = dpnp.ones(shape, dtype=dtype)

    result = 0.5 * dpnp_a * 1.7
    expected = 0.5 * np_a * 1.7
    assert_allclose(result, expected)


@pytest.mark.parametrize("shape",
                         [(), (3, 2)],
                         ids=['()', '(3, 2)'])
@pytest.mark.parametrize("dtype", get_all_dtypes())
def test_add_scalar(shape, dtype):
    np_a = numpy.ones(shape, dtype=dtype)
    dpnp_a = dpnp.ones(shape, dtype=dtype)

    result = 0.5 + dpnp_a + 1.7
    expected = 0.5 + np_a + 1.7
    assert_allclose(result, expected)


@pytest.mark.parametrize("shape",
                         [(), (3, 2)],
                         ids=['()', '(3, 2)'])
@pytest.mark.parametrize("dtype", get_all_dtypes())
def test_subtract_scalar(shape, dtype):
    np_a = numpy.ones(shape, dtype=dtype)
    dpnp_a = dpnp.ones(shape, dtype=dtype)

    result = 0.5 - dpnp_a - 1.7
    expected = 0.5 - np_a - 1.7
    assert_allclose(result, expected)


@pytest.mark.parametrize("shape",
                         [(), (3, 2)],
                         ids=['()', '(3, 2)'])
@pytest.mark.parametrize("dtype", get_all_dtypes())
def test_divide_scalar(shape, dtype):
    np_a = numpy.ones(shape, dtype=dtype)
    dpnp_a = dpnp.ones(shape, dtype=dtype)

    result = 0.5 / dpnp_a / 1.7
    expected = 0.5 / np_a / 1.7
    assert_allclose(result, expected)


@pytest.mark.usefixtures("allow_fall_back_on_numpy")
@pytest.mark.parametrize("array", [[1, 2, 3, 4, 5],
                                   [1, 2, numpy.nan, 4, 5],
                                   [[1, 2, numpy.nan], [3, -4, -5]]])
def test_nancumprod(array):
    np_a = numpy.array(array)
    dpnp_a = dpnp.array(np_a)

    result = dpnp.nancumprod(dpnp_a)
    expected = numpy.nancumprod(np_a)
    assert_array_equal(expected, result)


@pytest.mark.usefixtures("allow_fall_back_on_numpy")
@pytest.mark.parametrize("array", [[1, 2, 3, 4, 5],
                                   [1, 2, numpy.nan, 4, 5],
                                   [[1, 2, numpy.nan], [3, -4, -5]]])
def test_nancumsum(array):
    np_a = numpy.array(array)
    dpnp_a = dpnp.array(np_a)

    result = dpnp.nancumsum(dpnp_a)
    expected = numpy.nancumsum(np_a)
    assert_array_equal(expected, result)


@pytest.mark.parametrize("data",
                         [[[1., -1.], [0.1, -0.1]], [-2, -1, 0, 1, 2]],
                         ids=['[[1., -1.], [0.1, -0.1]]', '[-2, -1, 0, 1, 2]'])
@pytest.mark.parametrize("dtype", get_all_dtypes(no_bool=True, no_complex=True))
def test_negative(data, dtype):
    np_a = numpy.array(data, dtype=dtype)
    dpnp_a = dpnp.array(data, dtype=dtype)

    result = dpnp.negative(dpnp_a)
    expected = numpy.negative(np_a)
    assert_array_equal(result, expected)


@pytest.mark.usefixtures("allow_fall_back_on_numpy")
@pytest.mark.parametrize("val_type", get_all_dtypes(no_bool=True, no_complex=True, no_none=True))
@pytest.mark.parametrize("data_type", get_all_dtypes(no_bool=True, no_complex=True))
@pytest.mark.parametrize("val",
                         [0, 1, 5],
                         ids=['0', '1', '5'])
@pytest.mark.parametrize("array",
                         [[[0, 0], [0, 0]],
                          [[1, 2], [1, 2]],
                          [[1, 2], [3, 4]],
                          [[[1, 2], [3, 4]], [[1, 2], [2, 1]], [[1, 3], [3, 1]]],
                          [[[[1, 2], [3, 4]], [[1, 2], [2, 1]]], [[[1, 3], [3, 1]], [[0, 1], [1, 3]]]]],
                         ids=['[[0, 0], [0, 0]]',
                              '[[1, 2], [1, 2]]',
                              '[[1, 2], [3, 4]]',
                              '[[[1, 2], [3, 4]], [[1, 2], [2, 1]], [[1, 3], [3, 1]]]',
                              '[[[[1, 2], [3, 4]], [[1, 2], [2, 1]]], [[[1, 3], [3, 1]], [[0, 1], [1, 3]]]]'])
def test_power(array, val, data_type, val_type):
    np_a = numpy.array(array, dtype=data_type)
    dpnp_a = dpnp.array(array, dtype=data_type)
    val_ = val_type(val)
    result = dpnp.power(dpnp_a, val_)
    expected = numpy.power(np_a, val_)
    assert_array_equal(expected, result)


class TestEdiff1d:
    @pytest.mark.parametrize("data_type", get_all_dtypes(no_bool=True, no_complex=True))
    @pytest.mark.parametrize("array", [[1, 2, 4, 7, 0],
                                       [],
                                       [1],
                                       [[1, 2, 3], [5, 2, 8], [7, 3, 4]], ])
    def test_ediff1d_int(self, array, data_type):
        np_a = numpy.array(array, dtype=data_type)
        dpnp_a = dpnp.array(array, dtype=data_type)

        result = dpnp.ediff1d(dpnp_a)
        expected = numpy.ediff1d(np_a)
        assert_array_equal(expected, result)

    
    @pytest.mark.usefixtures("allow_fall_back_on_numpy")
    def test_ediff1d_args(self):
        np_a = numpy.array([1, 2, 4, 7, 0])

        to_begin = numpy.array([-20, -30])
        to_end = numpy.array([20, 15])

        result = dpnp.ediff1d(np_a, to_end=to_end, to_begin=to_begin)
        expected = numpy.ediff1d(np_a, to_end=to_end, to_begin=to_begin)
        assert_array_equal(expected, result)


@pytest.mark.usefixtures("allow_fall_back_on_numpy")
class TestTrapz:
    @pytest.mark.parametrize("data_type", get_all_dtypes(no_bool=True, no_complex=True))
    @pytest.mark.parametrize("array", [[1, 2, 3],
                                       [[1, 2, 3], [4, 5, 6]],
                                       [1, 4, 6, 9, 10, 12],
                                       [],
                                       [1]])
    def test_trapz_default(self, array, data_type):
        np_a = numpy.array(array, dtype=data_type)
        dpnp_a = dpnp.array(array, dtype=data_type)

        result = dpnp.trapz(dpnp_a)
        expected = numpy.trapz(np_a)
        assert_array_equal(expected, result)

    @pytest.mark.parametrize("data_type_y", get_all_dtypes(no_bool=True, no_complex=True))
    @pytest.mark.parametrize("data_type_x", get_all_dtypes(no_bool=True, no_complex=True))
    @pytest.mark.parametrize("y_array", [[1, 2, 4, 5],
                                         [1., 2.5, 6., 7.]])
    @pytest.mark.parametrize("x_array", [[2, 5, 6, 9]])
    def test_trapz_with_x_params(self, y_array, x_array, data_type_y, data_type_x):
        np_y = numpy.array(y_array, dtype=data_type_y)
        dpnp_y = dpnp.array(y_array, dtype=data_type_y)

        np_x = numpy.array(x_array, dtype=data_type_x)
        dpnp_x = dpnp.array(x_array, dtype=data_type_x)

        result = dpnp.trapz(dpnp_y, dpnp_x)
        expected = numpy.trapz(np_y, np_x)
        assert_array_equal(expected, result)

    @pytest.mark.parametrize("array", [[1, 2, 3], [4, 5, 6]])
    def test_trapz_with_x_param_2ndim(self, array):
        np_a = numpy.array(array)
        dpnp_a = dpnp.array(array)

        result = dpnp.trapz(dpnp_a, dpnp_a)
        expected = numpy.trapz(np_a, np_a)
        assert_array_equal(expected, result)

    @pytest.mark.parametrize("y_array", [[1, 2, 4, 5],
                                         [1., 2.5, 6., 7., ]])
    @pytest.mark.parametrize("dx", [2, 3, 4])
    def test_trapz_with_dx_params(self, y_array, dx):
        np_y = numpy.array(y_array)
        dpnp_y = dpnp.array(y_array)

        result = dpnp.trapz(dpnp_y, dx=dx)
        expected = numpy.trapz(np_y, dx=dx)
        assert_array_equal(expected, result)


@pytest.mark.usefixtures("allow_fall_back_on_numpy")
class TestCross:

    @pytest.mark.parametrize("axis", [None, 0],
                             ids=['None', '0'])
    @pytest.mark.parametrize("axisc", [-1, 0],
                             ids=['-1', '0'])
    @pytest.mark.parametrize("axisb", [-1, 0],
                             ids=['-1', '0'])
    @pytest.mark.parametrize("axisa", [-1, 0],
                             ids=['-1', '0'])
    @pytest.mark.parametrize("x1", [[1, 2, 3],
                                    [1., 2.5, 6.],
                                    [2, 4, 6]],
                             ids=['[1, 2, 3]',
                                  '[1., 2.5, 6.]',
                                  '[2, 4, 6]'])
    @pytest.mark.parametrize("x2", [[4, 5, 6],
                                    [1., 5., 2.],
                                    [6, 4, 3]],
                             ids=['[4, 5, 6]',
                                  '[1., 5., 2.]',
                                  '[6, 4, 3]'])
    def test_cross_3x3(self, x1, x2, axisa, axisb, axisc, axis):
        np_x1 = numpy.array(x1)
        dpnp_x1 = dpnp.array(x1)

        np_x2 = numpy.array(x2)
        dpnp_x2 = dpnp.array(x2)

        result = dpnp.cross(dpnp_x1, dpnp_x2, axisa, axisb, axisc, axis)
        expected = numpy.cross(np_x1, np_x2, axisa, axisb, axisc, axis)
        assert_array_equal(expected, result)


class TestGradient:

    @pytest.mark.parametrize("array", [[2, 3, 6, 8, 4, 9],
                                       [3., 4., 7.5, 9.],
                                       [2, 6, 8, 10]])
    def test_gradient_y1(self, array):
        np_y = numpy.array(array)
        dpnp_y = dpnp.array(array)

        result = dpnp.gradient(dpnp_y)
        expected = numpy.gradient(np_y)
        assert_array_equal(expected, result)

    @pytest.mark.usefixtures("allow_fall_back_on_numpy")
    @pytest.mark.parametrize("array", [[2, 3, 6, 8, 4, 9],
                                       [3., 4., 7.5, 9.],
                                       [2, 6, 8, 10]])
    @pytest.mark.parametrize("dx", [2, 3.5])
    def test_gradient_y1_dx(self, array, dx):
        np_y = numpy.array(array)
        dpnp_y = dpnp.array(array)

        result = dpnp.gradient(dpnp_y, dx)
        expected = numpy.gradient(np_y, dx)
        assert_array_equal(expected, result)


class TestCeil:

    def test_ceil(self):
        array_data = numpy.arange(10)
        out = numpy.empty(10, dtype=numpy.float64)

        # DPNP
        dp_array = dpnp.array(array_data, dtype=dpnp.float64)
        dp_out = dpnp.array(out, dtype=dpnp.float64)
        result = dpnp.ceil(dp_array, out=dp_out)

        # original
        np_array = numpy.array(array_data, dtype=numpy.float64)
        expected = numpy.ceil(np_array, out=out)

        assert_array_equal(expected, result)

    @pytest.mark.parametrize("dtype",
                             [numpy.float32, numpy.int64, numpy.int32],
                             ids=['numpy.float32', 'numpy.int64', 'numpy.int32'])
    def test_invalid_dtype(self, dtype):

        dp_array = dpnp.arange(10, dtype=dpnp.float64)
        dp_out = dpnp.empty(10, dtype=dtype)

        with pytest.raises(ValueError):
            dpnp.ceil(dp_array, out=dp_out)

    @pytest.mark.parametrize("shape",
                             [(0,), (15, ), (2, 2)],
                             ids=['(0,)', '(15, )', '(2,2)'])
    def test_invalid_shape(self, shape):

        dp_array = dpnp.arange(10, dtype=dpnp.float64)
        dp_out = dpnp.empty(shape, dtype=dpnp.float64)

        with pytest.raises(ValueError):
            dpnp.ceil(dp_array, out=dp_out)


class TestFloor:

    def test_floor(self):
        array_data = numpy.arange(10)
        out = numpy.empty(10, dtype=numpy.float64)

        # DPNP
        dp_array = dpnp.array(array_data, dtype=dpnp.float64)
        dp_out = dpnp.array(out, dtype=dpnp.float64)
        result = dpnp.floor(dp_array, out=dp_out)

        # original
        np_array = numpy.array(array_data, dtype=numpy.float64)
        expected = numpy.floor(np_array, out=out)

        assert_array_equal(expected, result)

    @pytest.mark.parametrize("dtype",
                             [numpy.float32, numpy.int64, numpy.int32],
                             ids=['numpy.float32', 'numpy.int64', 'numpy.int32'])
    def test_invalid_dtype(self, dtype):

        dp_array = dpnp.arange(10, dtype=dpnp.float64)
        dp_out = dpnp.empty(10, dtype=dtype)

        with pytest.raises(ValueError):
            dpnp.floor(dp_array, out=dp_out)

    @pytest.mark.parametrize("shape",
                             [(0,), (15, ), (2, 2)],
                             ids=['(0,)', '(15, )', '(2,2)'])
    def test_invalid_shape(self, shape):

        dp_array = dpnp.arange(10, dtype=dpnp.float64)
        dp_out = dpnp.empty(shape, dtype=dpnp.float64)

        with pytest.raises(ValueError):
            dpnp.floor(dp_array, out=dp_out)


class TestTrunc:

    def test_trunc(self):
        array_data = numpy.arange(10)
        out = numpy.empty(10, dtype=numpy.float64)

        # DPNP
        dp_array = dpnp.array(array_data, dtype=dpnp.float64)
        dp_out = dpnp.array(out, dtype=dpnp.float64)
        result = dpnp.trunc(dp_array, out=dp_out)

        # original
        np_array = numpy.array(array_data, dtype=numpy.float64)
        expected = numpy.trunc(np_array, out=out)

        assert_array_equal(expected, result)

    @pytest.mark.parametrize("dtype",
                             [numpy.float32, numpy.int64, numpy.int32],
                             ids=['numpy.float32', 'numpy.int64', 'numpy.int32'])
    def test_invalid_dtype(self, dtype):

        dp_array = dpnp.arange(10, dtype=dpnp.float64)
        dp_out = dpnp.empty(10, dtype=dtype)

        with pytest.raises(ValueError):
            dpnp.trunc(dp_array, out=dp_out)

    @pytest.mark.parametrize("shape",
                             [(0,), (15, ), (2, 2)],
                             ids=['(0,)', '(15, )', '(2,2)'])
    def test_invalid_shape(self, shape):

        dp_array = dpnp.arange(10, dtype=dpnp.float64)
        dp_out = dpnp.empty(shape, dtype=dpnp.float64)

        with pytest.raises(ValueError):
            dpnp.trunc(dp_array, out=dp_out)


class TestPower:

    def test_power(self):
        array1_data = numpy.arange(10)
        array2_data = numpy.arange(5, 15)
        out = numpy.empty(10, dtype=numpy.float64)

        # DPNP
        dp_array1 = dpnp.array(array1_data, dtype=dpnp.float64)
        dp_array2 = dpnp.array(array2_data, dtype=dpnp.float64)
        dp_out = dpnp.array(out, dtype=dpnp.float64)
        result = dpnp.power(dp_array1, dp_array2, out=dp_out)

        # original
        np_array1 = numpy.array(array1_data, dtype=numpy.float64)
        np_array2 = numpy.array(array2_data, dtype=numpy.float64)
        expected = numpy.power(np_array1, np_array2, out=out)

        assert_array_equal(expected, result)

    @pytest.mark.parametrize("dtype",
                             [numpy.float32, numpy.int64, numpy.int32],
                             ids=['numpy.float32', 'numpy.int64', 'numpy.int32'])
    def test_invalid_dtype(self, dtype):

        dp_array1 = dpnp.arange(10, dtype=dpnp.float64)
        dp_array2 = dpnp.arange(5, 15, dtype=dpnp.float64)
        dp_out = dpnp.empty(10, dtype=dtype)

        with pytest.raises(ValueError):
            dpnp.power(dp_array1, dp_array2, out=dp_out)

    @pytest.mark.parametrize("shape",
                             [(0,), (15, ), (2, 2)],
                             ids=['(0,)', '(15, )', '(2,2)'])
    def test_invalid_shape(self, shape):

        dp_array1 = dpnp.arange(10, dtype=dpnp.float64)
        dp_array2 = dpnp.arange(5, 15, dtype=dpnp.float64)
        dp_out = dpnp.empty(shape, dtype=dpnp.float64)

        with pytest.raises(ValueError):
            dpnp.power(dp_array1, dp_array2, out=dp_out)
