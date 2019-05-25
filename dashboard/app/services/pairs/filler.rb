# frozen_string_literal: true

module Pairs
  class Filler < Service
    validates :pair, presence: true
    validate :fill_successful

    before_validation :request_core_data

    def initialize(pair:)
      @pair = pair
      @fill = false
    end

    private

    attr_reader :pair, :fill

    def request_core_data
      @fill = HTTParty.post('http://core:5001/fill', query: { pair: pair.symbol }).success?
    rescue SocketError
      nil
    end

    def fill_successful
      return if fill

      errors.add(:pair, :invalid)
    end
  end
end
