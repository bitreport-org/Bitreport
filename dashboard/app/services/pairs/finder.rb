# frozen_string_literal: true

module Pairs
  class Finder < Service
    validates :symbol, presence: true

    def initialize(symbol:)
      @symbol = symbol
    end

    private

    attr_reader :symbol

    def run
      find_pair || create_pair
    end

    def find_pair
      Pair.where('symbol LIKE ?', "#{symbol.upcase}%").first
    end

    def create_pair
      Pairs::Creator.new(symbol: symbol).call
    end
  end
end
