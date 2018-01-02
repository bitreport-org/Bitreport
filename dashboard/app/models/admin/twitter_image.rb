module Admin
  class TwitterImage < ApplicationRecord
    SYMBOLS = %w[BTCUSD ETHUSD LTCUSD].freeze
    TIMEFRAMES = %w[30m 1h 3h 6h 12h 24h 168h].freeze
    PATTERNS = {
      CDL2CROWS: 'Two Crows',
      CDL3BLACKCROWS: 'Three Black Crows',
      CDL3INSIDE: 'Three Inside Up/Down',
      CDL3LINESTRIKE: 'Three Line Strikes',
      CDL3OUTSIDE: 'Three Outside Up/Down',
      CDL3STARSINSOUTH: 'Three Stars In The South',
      CDL3WHITESOLDIERS: 'Three Advancing White Soldiers',
      CDLABANDONEDBABY: 'Abandoned Baby',
      CDLADVANCEBLOCK: 'Advance Block',
      CDLBELTHOLD: 'Belt hold',
      CDLBREAKAWAY: 'Breakaway',
      CDLCLOSINGMARUBOZU: 'Closing Marubozu',
      CDLCONCEALBABYSWALL: 'Concealing Baby Swallow',
      CDLCOUNTERATTACK: 'Counterattack',
      CDLDARKCLOUDCOVER: 'Dark Cloud Cover',
      CDLDOJI: 'Doji',
      CDLDOJISTAR: 'Doji Star',
      CDLDRAGONFLYDOJI: 'Dragonfly Doji',
      CDLENGULFING: 'Engulfing Pattern',
      CDLEVENINGDOJISTAR: 'Evening Doji Star',
      CDLEVENINGSTAR: 'Evening Star',
      CDLGAPSIDESIDEWHITE: 'Up/Down Gap Side Side White',
      CDLGRAVESTONEDOJI: 'Gravestone Doji',
      CDLHAMMER: 'Hammer',
      CDLHANGINGMAN: 'Hanging Man',
      CDLHARAMI: 'Harami Pattern',
      CDLHARAMICROSS: 'Harami Cross Pattern',
      CDLHIGHWAVE: 'High',
      CDLHIKKAKE: 'Hikkake Pattern',
      CDLHIKKAKEMOD: 'Modified Hikkake Pattern',
      CDLHOMINGPIGEON: 'Homing Pigeon',
      CDLIDENTICAL3CROWS: 'Identical Three Crows',
      CDLINNECK: 'In Neck',
      CDLINVERTEDHAMMER: 'Inverted Hammer',
      CDLKICKING: 'Kicking',
      CDLKICKINGBYLENGTH: 'Kicking by length',
      CDLLADDERBOTTOM: 'Ladder Bottom',
      CDLLONGLEGGEDDOJI: 'Long Legged Doji',
      CDLLONGLINE: 'Long Line Candle',
      CDLMARUBOZU: 'Marubozu',
      CDLMATCHINGLOW: 'Matching Low',
      CDLMATHOLD: 'Mat Hold',
      CDLMORNINGDOJISTAR: 'Morning Doji Star',
      CDLMORNINGSTAR: 'Morning Star',
      CDLONNECK: 'On Neck',
      CDLPIERCING: 'Piercing Pattern',
      CDLRICKSHAWMAN: 'Rickshaw Man',
      CDLRISEFALL3METHODS: 'Rising/Falling Three Methods',
      CDLSEPARATINGLINES: 'Separating Lines',
      CDLSHOOTINGSTAR: 'Shooting Star',
      CDLSHORTLINE: 'Short Line Candle',
      CDLSPINNINGTOP: 'Spinning Top',
      CDLSTALLEDPATTERN: 'Stalled Pattern',
      CDLSTICKSANDWICH: 'Stick Sandwich',
      CDLTAKURI: 'Takuri (Dragonfly Doji with very long lower shadow)',
      CDLTASUKIGAP: 'Tasuki Gap',
      CDLTHRUSTING: 'Thrusting Pattern',
      CDLTRISTAR: 'Tristar Pattern',
      CDLUNIQUE3RIVER: 'Unique 3 River',
      CDLUPSIDEGAP2CROWS: 'Upside Gap Two Crows',
      CDLXSIDEGAP3METHODS: 'Upside/Downside Gap Three Methods'
    }.with_indifferent_access.freeze
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
      "http://127.0.0.1:5000/data/#{symbol}/#{timeframe}/?limit=#{limit}"
    end

    def generate_image(save = true)
      body = fetch_data
      @price = body['candles']['close'].last
      @change = body['candles']['close'].last - body['candles']['open'].first
      Plotter.new(body['dates'],
                  body['candles'],
                  body['patterns'].slice(*patterns),
                  body['indicators'].slice(*indicators),
                  body['levels'].values.flatten.uniq & (levels&.map(&:to_f) || [])).plot(save)
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
