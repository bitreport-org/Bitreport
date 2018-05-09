# frozen_string_literal: true

class TextGenerator
  TEXTS = {
    BB: {
      BANDS_SQUEEZE: ['Bollinger Bands are getting tight what usually leads to new big move.', 'Bollinger Bands are squeezing.'],
      BANDS_EXPANDED: ['We can see Bollinger Bands expanding.'],
      PRICE_BREAK_UP: ['The price broke above upper band recently.'],
      PRICE_BREAK_DOWN: ['The price was below lower Bollinger Bands.'],
      PRICE_BETWEEN: ['Price stays in the middle of Bollinger Bands.'],
      PRICE_ONBAND_UP: ['We\'re almost touching upper band now.'],
      PRICE_ONBAND_DOWN: ['We\'re really close to the lower band.']
    },
    RSI: {
      OSCILLATOR_OVERSOLD: ['RSI has beed low recently.', 'RSI below 30 indicates that the pair is oversold.'],
      OSCILLATOR_OVERBOUGHT: ['RSI indicates overbought area.', 'RSI above 70 indicates that the pair is overbought.'],
      DIRECTION_FALLING: ['RSI is getting higher.'],
      DIRECTION_RISING: ['RSI is getting lower.'],
      DIV_POISTIVE: ['There is a positive divergence with RSI.'],
      DIV_NEGATIVE: ['The RSI is showing a negative divergence. This may suggest trend reversal.']
    },
    wedge: {
      PRICE_BREAK_UP: ['Price broke out from the wedge.', 'Price is above the wedge.'],
      PRICE_BREAK_DOWN: ['Price broke down from the wedge.', 'Price is below the wedge.'],
      PRICE_ONBAND_UP: ['Price is moving close to the upper wedge.', 'Price is close to the upper wedge.'],
      PRICE_ONBAND_DOWN: ['Price is moving close to the lower wedge.', 'Price is close to the lower wedge.'],
      PRICE_BETWEEN: ['Price stays within the wedge.', 'Price is still moving inside the wedge.'],
      SHAPE_TRIANGLE: ['Wedge is a nice triangle.'],
      SHAPE_PARALLEL: ['Wedge creates a nice channel.', 'Wedge\' s bands are parallel.'],
      SHAPE_CONTRACTING: ['Would the wedge end as channel or as a triangle?'],
      DIRECTION_UP: ['Wedge is pointing up.', 'Wedge seems to be moving up.'],
      DIRECTION_DOWN: ['Wedge is pointing down.', 'Wedge seems to be moving down.'],
      PRICE_PULLBACK: ['Price pullbacks after moving above the wedge.'],
      PRICE_THROWBACK: ['Price makes a throwback after moving below the wedge.']
    },
    channel: {
      PRICE_BREAK_UP: ['Price has broke out of the channel.', 'Price is now above the channel.'],
      PRICE_BREAK_DOWN: ['Price has broke out of the channel.', 'Price is now below the channel.'],
      PRICE_BETWEEN: ['Prices stays whithin channel.', 'Price is still moving whithin the channel.'],
      PRICE_ONBAND_UP: ['We are close to the upper band of the channel.', 'Price is close to the upper band of the channel.'],
      PRICE_ONBAND_DOWN:['We are close to the lower band of the channel.', 'Price is close to the lower band of the channel.'],
      DIRECTION_UP: ['The channel is steady moving up.', 'Channel is pointing up, will the price stay within it?'],
      DIRECTION_DOWN: ['The channel is steady moving down.', 'Channel is pointing down, will the price stay within it?'],
      DIRECTION_HORIZONTAL: ['The channel moves roughly horizontally.'],
      PRICE_PULLBACK: ['Price pullbacks after moving above the channel.'],
      PRICE_THROWBACK: ['Price makes a throwback after moving below the channel.']
    },
    TDS: {

    },
    STOCH: {
      OSCILLATOR_OVERSOLD: ['Stochastic oscillator looks really low.',' Stochastic oscillator has beed low recently.', 'Stochastic oscillator below 20 indicates that the pair is oversold.'],
      OSCILLATOR_OVERBOUGHT: ['Stoch has been in an overbought area.', 'Stochastic oscillator indicates overbought area.', 'Stochastic oscillator above 80 indicates that the pair is overbought.'],
    },
    SMA: {
      CROSS_UP_FAST: ['We\'re already above fast SMA.', 'Price has crrosed up the fast SMA recently.'],
      CROSS_UP_MEDIUM: ['We\'re already above medium SMA.', 'Price has crrosed up the medium SMA recently.'],
      CROSS_UP_SLOW: ['We\'re already above slow SMA.', 'Price has crrosed up the slow SMA recently.'],
      CROSS_DOWN_SLOW: ['The price went below slow SMA.', 'Price has crrosed down the slow SMA recently.'],
      CROSS_DOWN_MEDIUM: ['The price went below medium SMA.', 'Price has crrosed down the medium SMA recently.'],
      CROSS_DOWN_FAST: ['The price went below fast SMA.', 'Price has crrosed down the fast SMA recently.'],
      POSITION_UP_FAST: ['The price is above fast SMA.' 'Price is above fast SMA.', 'Price stays above the fast SMA recently.'],
      POSITION_UP_MEDIUM: ['The price is above medium SMA.', 'Price is above medium SMA.', 'Price stays above the medium SMA recently.'],
      POSITION_UP_SLOW: ['The price is above slow SMA.', 'Price stays above the slow SMA recently.'],
      POSITION_DOWN_FAST: ['The price is below fast SMA.',  'Price stays below the fast SMA recently.'],
      POSITION_DOWN_MEDIUM: ['The price is below medium SMA.',  'Price stays below the medium SMA recently.'],
      POSITION_DOWN_SLOW: ['The price is below slow SMA.', 'Price stays below the slow SMA recently.'],
      CROSS_BEARISH: ['We have seen a bearish cross on SMA.', 'We have observed a bearish cross recently.', 'The bearish cross signals possible downtrend.', 'Fast SMA crossed down slow what means a bearish cross.'],
      CROSS_BULLISH: ['There was a bullish cross on SMA.', 'We have observed a bullish cross recently.', 'The bullish cross signals possible downtrend.', 'Fast SMA crossed up what means a bullish cross.']
    },
    EMA: {
      CCROSS_UP_FAST: ['We\'re already above fast EMA.', 'Price has crrosed up the fast EMA recently.'],
      CROSS_UP_MEDIUM: ['We\'re already above medium EMA.', 'Price has crrosed up the medium EMA recently.'],
      CROSS_UP_SLOW: ['We\'re already above slow EMA.', 'Price has crrosed up the slow EMA recently.'],
      CROSS_DOWN_SLOW: ['The price went below slow EMA.', 'Price has crrosed down the slow EMA recently.'],
      CROSS_DOWN_MEDIUM: ['The price went below medium EMA.', 'Price has crrosed down the medium EMA recently.'],
      CROSS_DOWN_FAST: ['The price went below fast EMA.', 'Price has crrosed down the fast EMA recently.'],
      POSITION_UP_FAST: ['The price is above fast EMA.' 'Price is above fast EMA.', 'Price stays above the fast EMA recently.'],
      POSITION_UP_MEDIUM: ['The price is above medium EMA.', 'Price is above medium EMA.', 'Price stays above the medium EMA recently.'],
      POSITION_UP_SLOW: ['The price is above slow EMA.', 'Price stays above the slow EMA recently.'],
      POSITION_DOWN_FAST: ['The price is below fast EMA.',  'Price stays below the fast EMA recently.'],
      POSITION_DOWN_MEDIUM: ['The price is below medium EMA.',  'Price stays below the medium EMA recently.'],
      POSITION_DOWN_SLOW: ['The price is below slow EMA.', 'Price stays below the slow EMA recently.'],
      CROSS_BEARISH: ['We have seen a bearish cross on EMA.', 'We have observed a bearish cross recently.', 'The bearish cross signals possible downtrend.', 'Fast EMA crossed down slow what means a bearish cross.'],
      CROSS_BULLISH: ['There was a bullish cross on EMA.', 'We have observed a bullish cross recently.', 'The bullish cross signals possible downtrend.', 'Fast EMA crossed up what means a bullish cross.']
    },
    ICM: {
      IN_CLOUD_UP: ['Price is moving into cloud from above.'],
      IN_CLOUD_DOWN: ['Price is moving into cloud from below.'],
      WIDE: ['Cloud is wide.'],
      THIN: ['Cloud is thin.']
    },
    MACD: {

    },
    SAR: {
      DIRECTION_DOWN: ['SAR indicates change of the trend.', 'SAR informs us about potential trend reversal.', 'According to SAR indicator it is an end of upward move.'],
      DIRECTION_UP: ['SAR indicates change of the trend.', 'SAR informs us about potential trend reversal.', 'According to SAR indicator it is an end of downward move.']

    },

  }.with_indifferent_access

  def initialize(indicator, tokens)
    @indicator = indicator
    @tokens = tokens
  end

  def to_s
    @tokens.map { |token| TEXTS.dig(@indicator, token)&.sample }.join(' ')
  end
end
