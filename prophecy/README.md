# Prophets
‘The Inner Eye does not See upon command!'
We shall See..

## Model 11.02.19
Model file: `size20future1_110219.h5`

Model name: `prophets.OHLC_prophecy`
```
INFO:

Size: 20
Prediction range: 1
Trained on: LTCUSD 1,3,6
Validated on: NEOUSD 6

LOSS:
training   (min:    0.003, max:    0.120, cur:    0.003)
validation (min:    0.001, max:    0.041, cur:    0.002)

PARAMS:
Dimensions: 4 (OHLC)
Trainable params: 226,849
lstm_size = 200,
size_dense=64,
num_dense=12,
p_loss='mean_squared_error',
p_optimizer='adam',
```

## Portfolio
Portfolio simulator is a simple model for market simulations. 
```python
from porfolio import portfolio
model = YourKerasModel

# Initiates portfolio with start amount 1000$
port = portfolio(start_amount=1000, model=model, fee=0.04)

# pd.DataFrame with close, open, high, low values
df = SampleDataFrame

# Size is the size of the model
port.simulate(df, size)
```

As a result you get simulation of trades and a simple summary of models achievements.
```python
# ...
# Epoch: 170 : SELL - actual: 8.93 predicted: 8.745857120895385
# Epoch: 178 : BUY - actual: 7.8983 predicted: 7.934674224315584
# Epoch: 179 : SELL - actual: 7.967 predicted: 7.82992694517672
# Portfolio summary
# Transaction fee: 0.04
# Start amount: 1000
# Final amount: 2001.6254798198934
# Earnings : 1001.63
# Profit : 100.16%
# Decision points: 180
# Decisions made : 61, buy: 30 sell: 30

```