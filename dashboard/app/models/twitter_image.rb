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

  def preview_image
    @preview_image ||= OverlayGenerator.new(self, plot).generate
  end

  def image_file
    image = Tempfile.new(%w(plot .png), encoding: 'ascii-8bit')
    image.write(preview_image)
    image
  end

  def timestamp
    (created_at || Time.zone.now).strftime("%Y-%m-%d %H:%M UTC")
  end

  def raw_data
    fetch_data
  end

  private

  def data_url
    "http://core/#{symbol}?timeframe=#{timeframe}&limit=#{limit}"
  end

  def plot
    body = fetch_data
    @price = body['indicators']['price']['close'].last
    @change = body['indicators']['price']['close'].last - body['indicators']['price']['open'].first
    Plotter.new(body['dates'],
                body['indicators'].slice(*(%w(price volume) + indicators)),
                body['indicators']['levels'].values.flatten.uniq & (levels&.map(&:to_f) || [])).plot
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
