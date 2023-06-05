# flake8: noqa
import numpy as np
from absl.testing import parameterized

from keras_core import backend
from keras_core import layers
from keras_core import testing


class UpSampling2dTest(testing.TestCase, parameterized.TestCase):
    @parameterized.product(
        data_format=["channels_first", "channels_last"],
        length_row=[2],
        length_col=[2, 3],
    )
    def test_upsampling_2d(self, data_format, length_row, length_col):
        num_samples = 2
        stack_size = 2
        input_num_row = 11
        input_num_col = 12

        if data_format == "channels_first":
            inputs = np.random.rand(
                num_samples, stack_size, input_num_row, input_num_col
            )
        else:
            inputs = np.random.rand(
                num_samples, input_num_row, input_num_col, stack_size
            )

        # basic test
        self.run_layer_test(
            layers.UpSampling2D,
            init_kwargs={"size": (2, 2), "data_format": data_format},
            input_shape=inputs.shape,
        )

        layer = layers.UpSampling2D(
            size=(length_row, length_col),
            data_format=data_format,
        )
        layer.build(inputs.shape)
        np_output = layer(inputs=backend.Variable(inputs))
        if data_format == "channels_first":
            assert np_output.shape[2] == length_row * input_num_row
            assert np_output.shape[3] == length_col * input_num_col
        else:
            assert np_output.shape[1] == length_row * input_num_row
            assert np_output.shape[2] == length_col * input_num_col

        # compare with numpy
        if data_format == "channels_first":
            expected_out = np.repeat(inputs, length_row, axis=2)
            expected_out = np.repeat(expected_out, length_col, axis=3)
        else:
            expected_out = np.repeat(inputs, length_row, axis=1)
            expected_out = np.repeat(expected_out, length_col, axis=2)

        np.testing.assert_allclose(np_output, expected_out)

    @parameterized.product(
        data_format=["channels_first", "channels_last"],
        length_row=[2],
        length_col=[2, 3],
    )
    def test_upsampling_2d_bilinear(self, data_format, length_row, length_col):
        num_samples = 2
        stack_size = 2
        input_num_row = 11
        input_num_col = 12
        if data_format == "channels_first":
            inputs = np.random.rand(
                num_samples, stack_size, input_num_row, input_num_col
            )
        else:
            inputs = np.random.rand(
                num_samples, input_num_row, input_num_col, stack_size
            )

        self.run_layer_test(
            layers.UpSampling2D,
            init_kwargs={
                "size": (2, 2),
                "data_format": data_format,
                "interpolation": "bilinear",
            },
            input_shape=inputs.shape,
        )

        layer = layers.UpSampling2D(
            size=(length_row, length_col),
            data_format=data_format,
        )
        layer.build(inputs.shape)
        np_output = layer(inputs=backend.Variable(inputs))
        if data_format == "channels_first":
            self.assertEqual(np_output.shape[2], length_row * input_num_row)
            self.assertEqual(np_output.shape[3], length_col * input_num_col)
        else:
            self.assertEqual(np_output.shape[1], length_row * input_num_row)
            self.assertEqual(np_output.shape[2], length_col * input_num_col)

    def test_upsampling_2d_correctness(self):
        input_shape = (2, 2, 1, 3)
        x = np.arange(np.prod(input_shape)).reshape(input_shape)
        np.testing.assert_array_equal(
            layers.UpSampling2D(size=(1, 2))(x),
            # fmt: off
            np.array(
                [[[[ 0.,  1.,  2.],
                   [ 0.,  1.,  2.]],
                  [[ 3.,  4.,  5.],
                   [ 3.,  4.,  5.]]],
                 [[[ 6.,  7.,  8.],
                   [ 6.,  7.,  8.]],
                  [[ 9., 10., 11.],
                   [ 9., 10., 11.]]]]
            ),
            # fmt: on
        )

    def test_upsampling_2d_various_interpolation_methods(self):
        input_shape = (2, 2, 1, 3)
        x = np.arange(np.prod(input_shape)).reshape(input_shape)
        for interpolation in [
            "bicubic",
            "bilinear",
            "lanczos3",
            "lanczos5",
            "nearest",
        ]:
            layers.UpSampling2D(size=(1, 2), interpolation=interpolation)(x)
