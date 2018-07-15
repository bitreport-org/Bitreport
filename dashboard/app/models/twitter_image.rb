class TwitterImage < ApplicationRecord
  TIMEFRAMES = %w[30m 1h 2h 3h 6h 12h 24h 168h].freeze
  attr_reader :price, :change

  include TwitterImageUploader[:image]

  def self.available_pairs
    Pair.order(name: :asc).map { |pair| ["#{pair.name} (#{pair.symbol})", pair.symbol] }.to_h
  end

  validates :symbol, presence: true, inclusion: { in: -> (_) { Pair.pluck(:symbol) } }
  validates :timeframe, presence: true, inclusion: { in: TIMEFRAMES }
  validates :limit, numericality: true, inclusion: { in: 20..200 }

  before_create :save_image

  def preview_image
    plotter = generate_image(true)
    OverlayGenerator.new(self, plotter.output).generate
  end

  def raw_data
    fetch_data
  end

  private

  def data_url
    "http://core/#{symbol}?timeframe=#{timeframe}&limit=#{limit}"
  end

  def generate_image(save = true)
    body = fetch_data
    @price = body['indicators']['price']['close'].last
    @change = body['indicators']['price']['close'].last - body['indicators']['price']['open'].first
    Plotter.new(body['dates'],
                body['indicators'].slice(*(%w(price volume) + indicators)),
                body['indicators']['levels'].values.flatten.uniq & (levels&.map(&:to_f) || [])).plot(save)
  end

  def save_image
    plotter = generate_image(true)
    self.image = File.open(plotter.output)
  end

  def fetch_data
    Rails.logger.debug("Requesting: #{data_url}")
    # TODO: Fetch API prices if not updated for a long time
    Rails.cache.fetch(data_url, expires_in: 10.minutes) do
      Rails.logger.debug("Fetching: #{data_url}")
      response = HTTParty.get(data_url)
      JSON.parse(response.body)
    end
  end
end
