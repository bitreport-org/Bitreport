# frozen_string_literal: true

class Pair < ApplicationRecord
  EXCHANGES = %w[bitfinex bittrex poloniex binance].freeze

  has_many :reports, dependent: :restrict_with_error

  validates :symbol, presence: true, uniqueness: true, format: /\A[A-Z0-9]+\z/
  validates :name, presence: true
  validates :exchange, presence: true, inclusion: { in: EXCHANGES }

  def self.find_matching(val)
    where('symbol LIKE ?', "#{val.upcase}%").first!
  end
end
