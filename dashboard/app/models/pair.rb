class Pair < ApplicationRecord
  EXCHANGES = %w[bitfinex bittrex poloniex binance]

  has_many :twitter_images

  validates :symbol, presence: true, uniqueness: true
  validates :name, presence: true
  validates :exchange, presence: true, inclusion: { in: EXCHANGES }
  validates :tags, length: { minimum: 1 } #, format: /\A([#$])[a-z](\w+)\z/i

  after_create :request_data_fill

  def request_data_fill
    HTTParty.post('http://core/fill', query: { pair: symbol, exchange: exchange })
    touch(:last_updated_at)
  end

  def tags=(val)
    super(val.split(' ').map(&:strip))
  end
end
