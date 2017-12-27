module Admin
  class TwitterImage < ApplicationRecord
    attr_reader :price, :change

    include TwitterImageUploader[:image]

    validates :symbol, presence: true, inclusion: { in: %w[BTCUSD ETHUSD LTCUSD] }
    validates :timeframe, presence: true, inclusion: { in: %w[30m 1h 3h 6h 12h 24h 168h] }
    validates :limit, numericality: true, inclusion: { in: 20..200 }

    before_create :generate_image

    def preview_image
      generate_image(false)
    end

    def raw_data
      fetch_data
    end

    private

    def data_url
      "http://127.0.0.1:5000/data/#{symbol}/#{timeframe}/?limit=#{limit}&patterns=#{patterns}&indicators=#{indicators.reject(&:empty?).join(',')}&levels=#{levels}"
    end

    def generate_image(save = true)
      body = fetch_data
      @price = body['candles']['close'].last
      @change = body['candles']['close'].last - body['candles']['open'].first
      Plotter.new(body['dates'],
                  body['candles'],
                  body['patterns'],
                  body['indicators'],
                  body['levels']).plot(save)
    end

    def save_image
      plotter = generate_image(true)
      self.image = File.open(plotter.output)
    end

    def fetch_data
      Rails.cache.fetch(data_url, expires_in: 10.minutes) do
        response = HTTParty.get(data_url)
        JSON.parse(response.body)
      end
    end
  end
end
