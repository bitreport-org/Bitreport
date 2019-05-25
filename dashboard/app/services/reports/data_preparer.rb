# frozen_string_literal: true

module Reports
  class DataPreparer < Service
    class ConnectionError < StandardError; end

    validates :pair, presence: true

    def initialize(pair:, timeframe:)
      @pair = pair
      @timeframe = timeframe
    end

    private

    attr_reader :pair, :timeframe

    def run
      Rails.cache.fetch(data_url, expires_in: 15.minutes) { fetch_data }
    end

    def data_url
      "http://core:5001/#{pair.symbol}?timeframe=#{timeframe}h&limit=200"
    end

    def fetch_data
      response = HTTParty.get(data_url)
      JSON.parse(response.body)
    rescue SocketError
      raise ConnectionError
    end
  end
end
