module Admin
  class TwitterImage < ApplicationRecord
    SYMBOLS = %w[STRATBTC EDOUSD ZCLBTC LENDBTC XELBTC PASCBTC PINKBTC IOTBTC DATUSD EMC2BTC SHIFTBTC ETCBTC SCBTC NEOBTC XRPUSD BTCUSD SANUSD ZECUSD ZECBTC TRUSTBTC EOSBTC LTCUSD DOGEBTC IOSBTC].freeze
    TIMEFRAMES = %w[30m 1h 2h 3h 6h 12h 24h 168h].freeze
    attr_reader :price, :change

    include TwitterImageUploader[:image]

    validates :symbol, presence: true, inclusion: { in: SYMBOLS }
    validates :timeframe, presence: true, inclusion: { in: TIMEFRAMES }
    validates :limit, numericality: true, inclusion: { in: 20..200 }

    before_create :save_image

    def preview_image
      generate_image(false)
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
      @price = body['candles']['close'].last
      @change = body['candles']['close'].last - body['candles']['open'].first
      Plotter.new(body['dates'],
                  body['candles'],
                  body['indicators'].slice(*indicators),
                  body['levels'].values.flatten.uniq & (levels&.map(&:to_f) || [])).plot(save)
    end

    def save_image
      plotter = generate_image(true)
      self.image = File.open(plotter.output)
    end

    def fetch_data
      Rails.cache.fetch(data_url, expires_in: 10.minutes) do
        Rails.logger.debug("Fetching: #{data_url}")
        response = HTTParty.get(data_url)
        JSON.parse(response.body)
      end
    end
  end
end
