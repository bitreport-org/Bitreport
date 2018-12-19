from keras.models import Model
from keras.layers import Dense, Embedding, Dropout, Activation, Concatenate, Input, LSTM, CuDNNLSTM, concatenate, Reshape


def prophet1(ts_input_shape=100,
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

def prophet2(ts_input_shape_short=168,
                ts_input_shape_long=7,
                lstm_size = 32,
                lstm_dense = 32,
                size_dense=64,
                num_dense=2,
                p_loss='mean_squared_error',
                p_optimizer='sgd',
                use_gpu_specifics=False):
    """
    Takes two time series as an input.
    Shorter and longer timeframes on the same time period.
    """

    # Declare inputs
    ts_input_short = Input(shape=(ts_input_shape_short, 1))

    ts_input_long = Input(shape=(ts_input_shape_long, 1))
    
    # Build the ts_part of the network
    if use_gpu_specifics:
        ts_lstm_long = CuDNNLSTM(lstm_size)(ts_input_long)
        ts_lstm_short = CuDNNLSTM(lstm_size)(ts_input_short)
    else:
        ts_lstm_short = LSTM(lstm_size)(ts_input_short)
        ts_lstm_long = LSTM(lstm_size)(ts_input_long)


    # Denses
    ts_dense_short = Dense(lstm_dense)(ts_lstm_short)
    ts_dense_long = Dense(lstm_dense)(ts_lstm_long)

    merged_magic = concatenate([ts_dense_short, ts_dense_long])

    ts_dense = Dense(size_dense)(merged_magic)
    for _ in range(num_dense):
        ts_dense = Dense(size_dense)(ts_dense)

    # Output dense
    output = Dense(1, activation='linear')(ts_dense)
    
    model = Model(inputs=[ts_input_short, ts_input_long], outputs=output)
    model.compile(loss=p_loss, optimizer=p_optimizer)

    return model