# frozen_string_literal: true

module Reports
  class DataPreparer < Service
    validates :pair, presence: true

    before_execute :request_data_fill

    def initialize(pair:, timeframe:)
      @pair = pair
      @timeframe = timeframe
    end

    private

    attr_reader :pair, :timeframe

    def run
      Rails.cache.fetch(data_url, expires_in: 15.minutes) { fetch_data }
    end

    def request_data_fill
      return if pair.last_updated_at > timeframe.to_i.hours.ago

      pair.fill
    end

    def data_url
      "http://core:5001/#{pair.symbol}?timeframe=#{timeframe}h&limit=200"
    end

    def fetch_data
      response = HTTParty.get(data_url)
      # TODO: Handle failures
      JSON.parse(response.body)
    end
  end
end
