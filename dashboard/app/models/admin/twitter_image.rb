module Admin
  class TwitterImage < ApplicationRecord
    attr_reader :price

    include TwitterImageUploader[:image]

    validates :symbol, presence: true, inclusion: { in: %w[BTCUSD] }
    validates :timeframe, presence: true, inclusion: { in: %w[30m 1h 3h 12h] }
    validates :limit, numericality: true, inclusion: { in: 20..200 }

    before_create :generate_image

    def preview_image
      generate_image(false)
    end

    private

    def data_url
      "http://127.0.0.1:5000/data/#{symbol}/#{timeframe}/?limit=#{limit}&patterns=#{patterns.reject(&:empty?).join(',')}&indicators=#{indicators.join(',')}&levels=#{levels}"
    end

    def generate_image(save = true)
      response = HTTParty.get(data_url)
      body = JSON.parse(response.body)
      @price = body['candles']['close'].last
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
  end
end
