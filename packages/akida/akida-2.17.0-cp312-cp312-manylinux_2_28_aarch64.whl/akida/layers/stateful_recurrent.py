from akida.core import Layer, LayerType, LayerParams, ActivationType


class StatefulRecurrent(Layer):
    """This represents the Akida StatefulRecurrent layer.

    To store the previous state of the layer, this time dependent layer has an internal state
    variable that is updated at each run.

    This main layer operation is preceded by a matmul (input) projection and followed by another
    matmul (output) projection followed by a bias addition.

    Optional shaping operations: a downshape can be done before the input projection, a timesteps
    subsampling can be done before output projection and an upshape can be done after the output
    projection. Subsampling drops timesteps from the (T, C) tensors while upshaping and downshaping
    are reshaping operations that change the shape of the output tensor by applying a factor to
    the timesteps and channels.

    The StatefulRecurrent layer operations can be described as follows:

        >>> Input shift:
        >>>     inputs = inputs << input_shift
        >>> Downshape:
        >>>     inputs = reshape(inputs, [timestep / downshape, downshape * channels])
        >>> Input projection:
        >>>     input_proj = matmul(inputs, B)
        >>>     new_state = scale_out(input_proj, new_state_shift, new_state_scale)
        >>> Stateful recurrent:
        >>>     output_state_real = zeros((timesteps, new_state.shape[-1]))
        >>>     foreach timestep:
        >>>         updated_real = multiply(state_real, A_real) - multiply(state_imag, A_imag)
        >>>         updated_real += new_state[timestep]
        >>>         updated_imag = multiply(state_real, A_imag) + multiply(state_imag, A_real)
        >>>         state_real = updated_real >> shift_out
        >>>         state_imag = updated_imag >> shift_out
        >>>         output_state_real[timestep] = state_real
        >>> Subsampling:
        >>>     outputs = output_state_real[:, (subsample - 1)::subsample, :]
        >>> Output projection:
        >>>     output_proj = matmul(outputs, C)
        >>>     bias = bias << bias_shift
        >>>     output = output_proj + bias
        >>> Upshape:
        >>>     output = reshape(output, [timestep * upshape, channels / upshape])
        >>> Activation:
        >>>     output = relu(output)
        >>>     output = scale_out(output, output_proj_shift, output_proj_scale)

    Note that output values will be saturated on the range that can be represented
    with output_bits.

    Args:
        stateful_channels (int): the size of the internal state and also the number of output
            channels for the input projection.
        output_channels (int): number of output channels.
        subsample (int, optional): subsampling value that defines rate at which outputs are
            produced. Defaults to 1.
        downshape (int, optional): value by which time steps are divided and channels are
            multiplied before input projection. Defaults to 1.
        upshape (int, optional): value by which time steps are multiplied and channels are divided.
            after output projection. Defaults to 1.
        activation (:obj:`ActivationType`, optional): activation type. Defaults to
            `ActivationType.ReLU`.
        output_bits (int, optional): output bitwidth. Defaults to 8.
        buffer_bits (int, optional): buffer bitwidth for input and output projection operations.
            Defaults to 28.
        post_op_buffer_bits (int, optional): internal bitwidth for stateful and post operations.
            Defaults to 32.
        internal_state_bits (int, optional): internal state bitwidth. Defaults to 16.
        name (str, optional): name of the layer. Defaults to empty string.

    """

    def __init__(self,
                 stateful_channels,
                 output_channels,
                 subsample=1,
                 downshape=1,
                 upshape=1,
                 activation=ActivationType.ReLU,
                 output_bits=8,
                 buffer_bits=28,
                 post_op_buffer_bits=32,
                 internal_state_bits=16,
                 name=""):
        try:
            params = LayerParams(
                LayerType.StatefulRecurrent, {
                    "stateful_channels": stateful_channels,
                    "output_channels": output_channels,
                    "subsample": subsample,
                    "downshape": downshape,
                    "upshape": upshape,
                    "activation": activation,
                    "output_bits": output_bits,
                    "post_op_buffer_bits": post_op_buffer_bits,
                    "buffer_bits": buffer_bits,
                    "internal_state_bits": internal_state_bits
                })
            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except BaseException:
            self = None
            raise
