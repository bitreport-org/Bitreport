# frozen_string_literal: true

def stub_fill
  stub_request(:post, 'http://core/fill')
    .with(query: hash_including(:exchange, :pair))
    .to_return(status: 200, body: '{}')
end

def stub_get(symbol)
  response = <<~JSON
    {
      "dates": [],
      "indicators": {
        "price": {
          "close": [110],
          "open": [100],
          "high": [120],
          "low": [90],
          "info": []
        },
        "volume": {
          "volume": [10],
          "info": ["VOLUME_SPIKE"]
        },
        "RSI": {
          "rsi": [50],
          "info": []
        }
      }
    }
  JSON
  stub_request(:get, "http://core/#{symbol}")
    .with(query: hash_including(:limit, :timeframe))
    .to_return(status: 200, body: response)
end
