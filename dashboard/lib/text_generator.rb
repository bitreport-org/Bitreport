# frozen_string_literal: true

class TextGenerator
  TEXTS = {
    BB: {
      BANDS_SQUEEZE: ['Bollinger Bands are getting tight.'],
      BANDS_EXPANDED: ['We can see Bollinger Bands expanding.'],
      PRICE_BREAK_UP: ['The price broke above upper band recently.'],
      PRICE_BREAK_DOWN: ['The price was below lower Bollinger Bands.'],
      PRICE_BETWEEN: ['Price stays in the middle of Bollinger Bands.'],
      PRICE_ONBAND_UP: ['We\'re almost touching upper band now.'],
      PRICE_ONBAND_DOWN: ['We\'re really close to the lower band.']
    },
    RSI: {
      OSCILLATOR_OVERSOLD: ['RSI has beed low recently.'],
      OSCILLATOR_OVERBOUGHT: ['RSI indicates overbought area.'],
      DIRECTION_FALLING: ['RSI is getting higher.'],
      DIRECTION_RISING: ['RSI is getting lower.'],
      DIV_POISTIVE: ['There is a positive divergence with RSI.'],
      DIV_NEGATIVE: ['The RSI is showing a negative divergence.']
    },
    wedge: {

    },
    channel: {

    },
    TDS: {

    },
    STOCH: {

    },
    SMA: {

    },
    EMA: {

    },
    ICM: {

    },
    MACD: {

    },
    SAR: {

    }
  }.with_indifferent_access

  def initialize(indicator, tokens)
    @indicator = indicator
    @tokens = tokens
  end

  def to_s
    @tokens.map { |token| TEXTS[@indicator][token].sample }.join(' ')
  end
end
