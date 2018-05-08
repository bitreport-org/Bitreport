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
      OSCILLATOR_OVERSOLD: ['RSI has been low recently.'],
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
      OSCILLATOR_OVERSOLD: ['Stochastic oscillator looks really low.'],
      OSCILLATOR_OVERBOUGHT: ['Stoch has been in an overbought area.']
    },
    SMA: {
      CROSS_UP_FAST: ['We\'re already above fast SMA.'],
      CROSS_UP_MEDIUM: ['We\'re already above medium SMA.'],
      CROSS_UP_SLOW: ['We\'re already above slow SMA.'],
      CROSS_DOWN_SLOW: ['The price went below slow SMA.'],
      CROSS_DOWN_MEDIUM: ['The price went below medium SMA.'],
      CROSS_DOWN_FAST: ['The price went below fast SMA.'],
      POSITION_UP_FAST: ['The price is above fast SMA.'],
      POSITION_UP_MEDIUM: ['The price is above medium SMA.'],
      POSITION_UP_SLOW: ['The price is above slow SMA.'],
      POSITION_DOWN_FAST: ['The price is below fast SMA.'],
      POSITION_DOWN_MEDIUM: ['The price is below medium SMA.'],
      POSITION_DOWN_SLOW: ['The price is below slow SMA.'],
      CROSS_BEARISH: ['We have seen a bearish cross on SMA.'],
      CROSS_BULLISH: ['There was a bullish cross on SMA.']
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
    @tokens.map { |token| TEXTS.dig(@indicator, token)&.sample }.join(' ')
  end
end
