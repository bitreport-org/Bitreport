# frozen_string_literal: true

class Pair < ApplicationRecord
  EXCHANGES = %w[bitfinex bittrex poloniex binance].freeze

  has_many :reports

  validates :symbol, presence: true, uniqueness: true, format: /\A[A-Z0-9]+\z/
  validates :name, presence: true
  validates :exchange, presence: true, inclusion: { in: EXCHANGES }
  validates :tags, length: { minimum: 1 } # , format: /\A([#$])[a-z](\w+)\z/i

  after_create :request_data_fill

  def request_data_fill
    HTTParty.post('http://core/fill', query: { pair: symbol, exchange: exchange })
    touch(:last_updated_at)
  end

  def tags=(val)
    super(val.is_a?(String) ? val.split(' ').map(&:strip) : val)
  end

  def self.find_matching(val)
    where('symbol LIKE ?', "#{val.upcase}%").first!
  end
end
