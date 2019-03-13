# frozen_string_literal: true

module Pairs
  class Filler < Service
    validates :pair, presence: true

    def initialize(pair:)
      @pair = pair
    end

    private

    attr_reader :pair

    def run
      fill_request.success? && pair.touch(:last_updated_at)
    end

    def fill_request
      @fill_request ||= HTTParty.post('http://core/fill', query: { pair: pair.symbol })
    end
  end
end
