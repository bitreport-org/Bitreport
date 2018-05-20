class Pair < ApplicationRecord
  EXCHANGES = %w[bitfinex bittrex poloniex binance]

  validates :symbol, presence: true, uniqueness: true
  validates :name, presence: true
  validates :exchange, presence: true, inclusion: { in: EXCHANGES }

  after_create :request_data_fill

  def request_data_fill
    HTTParty.post('http://core/fill', query: { pair: symbol, exchange: exchange })
    update(last_updated_at: Time.zone.now)
  end
end
