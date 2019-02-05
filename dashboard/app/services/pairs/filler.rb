# frozen_string_literal: true

module Pairs
  class Filler < Service
    validates :pair, presence: true

    before_execute :make_fill_request

    def initialize(pair:)
      @pair = pair
    end

    private

    attr_reader :pair

    def run
      pair.touch(:last_updated_at)
    end

    def make_fill_request
      HTTParty.post('http://core/fill', query: { pair: pair.symbol, exchange: pair.exchange })
    end
  end
end
