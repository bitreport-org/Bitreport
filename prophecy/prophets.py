from keras.models import Model
from keras.layers import Dense, Embedding, Dropout, Activation, Concatenate, Input, LSTM, CuDNNLSTM, concatenate, Reshape


def Close_prophecy(ts_input_shape=100,
                lstm_size = 32,
                size_dense=64,
                num_dense=2,
                p_loss='mean_squared_error',
                p_optimizer='sgd',
                use_gpu_specifics=False):
    """
    Takes timeseries of ts_input_shape length as input
    """

    # Declare inputs
    ts_input = Input(shape=(ts_input_shape, 1))
    
    # Build the ts_part of the network
    if use_gpu_specifics:
        ts_lstm = CuDNNLSTM(lstm_size)(ts_input)
    else:
        ts_lstm = LSTM(lstm_size)(ts_input)

    # Denses
    ts_dense = Dense(size_dense)(ts_lstm)
    for _ in range(num_dense):
        ts_dense = Dense(size_dense)(ts_dense)

    # Output dense
    output = Dense(1, activation='linear')(ts_dense)
    
    model = Model(inputs=ts_input, outputs=output)
    model.compile(loss=p_loss, optimizer=p_optimizer)

    return model


def OHLC_prophecy(ts_input_shape,
                  lstm_size=32,
                  size_dense=64,
                  num_dense=2,
                  p_loss='mean_squared_error',
                  p_optimizer='adam',
                  use_gpu_specifics=False):
    """
    Uses OHLC input
    """

    # Declare inputs
    net_input = Input(shape=(ts_input_shape, 4))

    # Build the ts_part of the network
    if use_gpu_specifics:
        lstm_out = CuDNNLSTM(lstm_size)(net_input)
    else:
        lstm_out = LSTM(lstm_size)(net_input)

    # Denses
    dense_out = Dense(size_dense)(lstm_out)
    for _ in range(num_dense):
        dense_out = Dense(size_dense)(dense_out)

    # Output dense
    output = Dense(1, activation='linear')(dense_out)

    model = Model(inputs=net_input, outputs=output)
    model.compile(loss=p_loss, optimizer=p_optimizer)

    return model