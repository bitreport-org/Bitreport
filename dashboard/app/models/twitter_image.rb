class TwitterImage < ApplicationRecord
  include ImageUploader[:image]

  validates :symbol, presence: true, inclusion: { in: %w[BTCUSD] }
  validates :timeframe, presence: true, inclusion: { in: %w[30m 1h 3h 12h] }
  validates :limit, numericality: true, inclusion: { in: 20..200 }

  before_create :generate_image

  private

  def generate_image
    response = HTTParty.get("http://127.0.0.1:5000/data/#{symbol}/#{timeframe}?limit=#{limit}&patterns=#{patterns.join(',')}&indicators=#{indicators.join(',')}")
    body = JSON.parse(response.body)
    plotter = Plotter.new(body['dates'], body['candles'], body['patterns'], body['indicators']).plot
    self.image = File.open(plotter.output)
  end
end
