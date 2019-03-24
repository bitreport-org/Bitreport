# frozen_string_literal: true

def stub_core_fill
  stub_request(:post, 'http://core:5001/fill')
    .with(query: hash_including(:pair))
    .to_return(status: 200, body: '{}', headers: { 'Content-Type' => 'application/json' })
end

def stub_core_fill_failure
  stub_request(:post, 'http://core:5001/fill')
    .with(query: hash_including(:pair))
    .to_return(status: 404, body: '{}', headers: { 'Content-Type' => 'application/json' })
end

def stub_core_get(symbol)
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
  stub_request(:get, "http://core:5001/#{symbol}")
    .with(query: hash_including(:limit, :timeframe))
    .to_return(status: 200, body: response, headers: { 'Content-Type' => 'application/json' })
end
