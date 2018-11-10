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
      OSCILLATOR_OVERSOLD: ['RSI has been low recently.', 'RSI below 30 indicates that the pair is oversold.'],
      OSCILLATOR_OVERBOUGHT: ['RSI indicates overbought area.', 'RSI above 70 indicates that the pair is overbought.'],
      DIRECTION_FALLING: ['RSI is getting lower.'],
      DIRECTION_RISING: ['RSI is getting higher.'],
      DIV_POSITIVE: ['There is a positive divergence with RSI.'],
      DIV_NEGATIVE: ['The RSI is showing a negative divergence. This may suggest trend reversal.']
    },
    wedge: {
      PRICE_BREAK_UP: ['Price broke out from the wedge.', 'Price is above the wedge.'],
      PRICE_BREAK_DOWN: ['Price broke down from the wedge.', 'Price is below the wedge.'],
      PRICE_ONBAND_UP: ['Price is moving close to the upper wedge.', 'Price is close to the upper wedge.'],
      PRICE_ONBAND_DOWN: ['Price is moving close to the lower wedge.', 'Price is close to the lower wedge.'],
      PRICE_BETWEEN: ['Price stays within the wedge.', 'Price is still moving inside the wedge.'],
      SHAPE_TRIANGLE: ['Wedge is a nice triangle.', 'Wedge looks like a triangle.'],
      SHAPE_PARALLEL: ['Wedge creates a nice channel.', 'Wedge\'s bands are parallel.'],
      SHAPE_CONTRACTING: ['Would the wedge end as channel or as a triangle?'],
      DIRECTION_UP: ['Wedge is pointing up.', 'Wedge seems to be moving up.'],
      DIRECTION_DOWN: ['Wedge is pointing down.', 'Wedge seems to be moving down.'],
      PRICE_PULLBACK: ['Price pullbacks after moving above the wedge.'],
      PRICE_THROWBACK: ['Price makes a throwback after moving below the wedge.']
    },
    channel: {
      PRICE_BREAK_UP: ['Price has broke out of the channel.', 'Price is now above the channel.'],
      PRICE_BREAK_DOWN: ['Price has broke out of the channel.', 'Price is now below the channel.'],
      PRICE_BETWEEN: ['Prices stays within channel.', 'Price is still moving within the channel.', 'Will the price stay within the channel?'],
      PRICE_ONBAND_UP: ['We are close to the upper band of the channel.', 'Price is close to the upper band of the channel.'],
      PRICE_ONBAND_DOWN: ['We are close to the lower band of the channel.', 'Price is close to the lower band of the channel.'],
      DIRECTION_UP: ['The channel is steady moving up.', 'Channel is pointing up.'],
      DIRECTION_DOWN: ['The channel is steady moving down.', 'Channel is pointing down.'],
      DIRECTION_HORIZONTAL: ['The channel moves roughly horizontally.'],
      FALSE_BREAK_UP: ['Price made a false break of the upper band.'],
      FALSE_BREAK_DOWN: ['Price made a false break of the lower band.']
    },
    TDS: {

    },
    STOCH: {
      OSCILLATOR_OVERSOLD: ['Stochastic oscillator looks really low.', 'Stochastic oscillator has bead low recently.', 'Stochastic oscillator below 20 indicates that the pair is oversold.'],
      OSCILLATOR_OVERBOUGHT: ['Stoch has been in an overbought area.', 'Stochastic oscillator indicates overbought area.', 'Stochastic oscillator above 80 indicates that the pair is overbought.']
    },
    SMA: {
      CROSS_UP_FAST: ['We\'re already above fast SMA.', 'Price has crossed up the fast SMA recently.'],
      CROSS_UP_MEDIUM: ['We\'re already above medium SMA.', 'Price has crossed up the medium SMA recently.'],
      CROSS_UP_SLOW: ['We\'re already above slow SMA.', 'Price has crossed up the slow SMA recently.'],
      CROSS_DOWN_SLOW: ['The price went below slow SMA.', 'Price has crossed down the slow SMA recently.'],
      CROSS_DOWN_MEDIUM: ['The price went below medium SMA.', 'Price has crossed down the medium SMA recently.'],
      CROSS_DOWN_FAST: ['The price went below fast SMA.', 'Price has crossed down the fast SMA recently.'],
      POSITION_UP_FAST: ['The price is above fast SMA.', 'Price is above fast SMA.', 'Price stays above the fast SMA recently.'],
      POSITION_UP_MEDIUM: ['The price is above medium SMA.', 'Price is above medium SMA.', 'Price stays above the medium SMA recently.'],
      POSITION_UP_SLOW: ['The price is above slow SMA.', 'Price stays above the slow SMA recently.'],
      POSITION_DOWN_FAST: ['The price is below fast SMA.',  'Price stays below the fast SMA recently.'],
      POSITION_DOWN_MEDIUM: ['The price is below medium SMA.', 'Price stays below the medium SMA recently.'],
      POSITION_DOWN_SLOW: ['The price is below slow SMA.', 'Price stays below the slow SMA recently.'],
      CROSS_BEARISH: ['We have seen a bearish cross on SMA.', 'We have observed a bearish cross recently.', 'The bearish cross signals possible downtrend.', 'Fast SMA crossed down slow what means a bearish cross.'],
      CROSS_BULLISH: ['There was a bullish cross on SMA.', 'We have observed a bullish cross recently.', 'The bullish cross signals possible downtrend.', 'Fast SMA crossed up what means a bullish cross.']
    },
    EMA: {
      CCROSS_UP_FAST: ['We\'re already above fast EMA.', 'Price has crossed up the fast EMA recently.'],
      CROSS_UP_MEDIUM: ['We\'re already above medium EMA.', 'Price has crossed up the medium EMA recently.'],
      CROSS_UP_SLOW: ['We\'re already above slow EMA.', 'Price has crossed up the slow EMA recently.'],
      CROSS_DOWN_SLOW: ['The price went below slow EMA.', 'Price has crossed down the slow EMA recently.'],
      CROSS_DOWN_MEDIUM: ['The price went below medium EMA.', 'Price has crossed down the medium EMA recently.'],
      CROSS_DOWN_FAST: ['The price went below fast EMA.', 'Price has crossed down the fast EMA recently.'],
      POSITION_UP_FAST: ['The price is above fast EMA.', 'Price is above fast EMA.', 'Price stays above the fast EMA recently.'],
      POSITION_UP_MEDIUM: ['The price is above medium EMA.', 'Price is above medium EMA.', 'Price stays above the medium EMA recently.'],
      POSITION_UP_SLOW: ['The price is above slow EMA.', 'Price stays above the slow EMA recently.'],
      POSITION_DOWN_FAST: ['The price is below fast EMA.',  'Price stays below the fast EMA recently.'],
      POSITION_DOWN_MEDIUM: ['The price is below medium EMA.', 'Price stays below the medium EMA recently.'],
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
    price: {
      VOLUME_SPIKE: ['The big volume suggests potential changes.'],
      VOLUME_DIRECTION_DOWN: ['Volume is getting higher.'],
      VOLUME_DIRECTION_UP: ['Volume is getting lower'],
      PRICE_HIGHEST_DAY: ['We are observing highest price in last 24h'],
      PRICE_LOWEST_DAY: ['We are observing lowest price in last 24h'],
      PRICE_HIGHEST_WEEK: ['We are observing highest price in this week'],
      PRICE_LOWEST_WEEK: ['We are observing lowest price in this week'],
      PRICE_HIGHEST_MONTH: ['We are observing highest price in this month'],
      PRICE_LOWEST_MONTH: ['We are observing lowest price in this week'],
      # CHART_NONE: [],
      CHART_DOWN: ['Price is still moving down.', 'We have a downtrend.'],
      CHART_UP: ['Price is still moving up.', 'We have an uptrend.'],
      CHART_UD_REV: ['Uptrend to downtrend reversal.'],
      CHART_DU_REV: ['Downtrend to uptrend reversal'],
      # STRONG_UP: [],
      # STRONG_DOWN: [],
      # SMALL_MOVE_UP: [],
      # SMALL_MOVE_DOWN: [],
      # BIG_MOVE_UP: [],
      # BIG_MOVE_DOWN: [],
    }
  }.with_indifferent_access

  DETAILS = {
    BB: {
      BANDS: {
        SQUEEZE: ['getting tight', 'getting squeezed'],
        EXPANDED: ['expanding', 'getting wider']
      },
      PRICE: {
        BREAK_UP: ['price broke above upper band'],
        BREAK_DOWN: ['price below lower band'],
        BETWEEN: ['price stays in the middle'],
        ONBAND_UP: ['price almost touching upper band'],
        ONBAND_DOWN: ['price really close to the lower band']
      }
    },
    RSI: {
      OSCILLATOR: {
        OVERSOLD: ['low', 'below 30', 'oversold'],
        OVERBOUGHT: ['overbought', 'above 70', 'high']
      },
      DIRECTION: {
        FALLING: ['getting lower'],
        RISING: ['getting higher']
      },
      DIV: {
        POSITIVE: ['positive divergence'],
        NEGATIVE: ['negative divergence']
      }
    },
    wedge: {
      PRICE: {
        BREAK_UP: ['price broke out', 'price is above'],
        BREAK_DOWN: ['price broke down', 'price is below'],
        ONBAND_UP: ['price is close to the upper wedge', 'price stays high'],
        ONBAND_DOWN: ['price is close to the lower wedge', 'price stays low'],
        BETWEEN: ['price stays within the wedge'],
        PULLBACK: ['pullback after moving above the wedge'],
        THROWBACK: ['throwback after moving below the wedge']
      },
      SHAPE: {
        TRIANGLE: ['a triangle'],
        PARALLEL: ['a channel', 'parallel'],
        CONTRACTING: ['contracting']
      },
      BOUNCE: {
        UPPER: ['price bounced from upper wedge'],
        LOWER: ['price bounced from lower wedge']
      },
      DIRECTION: {
        UP: ['pointing up', 'moving up'],
        DOWN: ['pointing down', 'moving down'],
        HORIZONTAL: %w[sideways horizontal]
      },
      ABOUT: {
        END: ['close to end']
      }
    },
    SMA: {
      CROSS: {
        UP_FAST: ['crossed above fast SMA', 'crossed up the fast SMA'],
        UP_MEDIUM: ['crossed above medium SMA', 'crossed up the medium SMA'],
        UP_SLOW: ['crossed above slow SMA', 'crossed up the slow SMA'],
        DOWN_SLOW: ['crossed below slow SMA', 'crossed down the slow SMA'],
        DOWN_MEDIUM: ['crossed below medium SMA', 'crossed down the medium SMA'],
        DOWN_FAST: ['crossed below fast SMA', 'crossed down the fast SMA'],
        BEARISH: ['bearish cross', 'fast SMA crossed down'],
        BULLISH: ['bullish cross', 'Fast SMA crossed up']
      },
      POSITION: {
        UP_FAST: ['above fast SMA'],
        UP_MEDIUM: ['above medium SMA'],
        UP_SLOW: ['above slow SMA'],
        DOWN_FAST: ['below fast SMA'],
        DOWN_MEDIUM: ['below medium SMA'],
        DOWN_SLOW: ['below slow SMA']
      }
    },
    ICM: {
      IN: {
        CLOUD_UP: ['price moving into cloud from above'],
        CLOUD_DOWN: ['price moving into cloud from below']
      },
      PIERCED: {
        UP: ['price moved into cloud from above'],
        DOWN: ['price moved into cloud from below']
      },
      CLOUD: {
        WIDE: ['wide'],
        THIN: ['thin']
      }
    },
    MACD: {

    },
    volume: {
      VOLUME: {
        SPIKE: ['big volume spike'],
        DIRECTION_DOWN: ['getting lower'],
        DIRECTION_UP: ['getting higher']
      }
    },
    price: {
      PRICE: {
        HIGHEST_DAY: ['highest price in last 24h'],
        LOWEST_DAY: ['lowest price in last 24h'],
        HIGHEST_WEEK: ['highest price this week'],
        LOWEST_WEEK: ['lowest price this week'],
        HIGHEST_MONTH: ['highest price this month'],
        LOWEST_MONTH: ['lowest price this month']
      },
      CHART: {
        NONE: [],
        DOWN: ['moving down', 'downtrend'],
        UP: ['moving up', 'uptrend'],
        UD_REV: ['possible reversal'],
        DU_REV: ['possible reversal']
      },
      MOVE: {
        STRONG_UP: ['overall move up'],
        STRONG_DOWN: ['overall move down'],
        SMALL_UP: ['recent move up'],
        SMALL_DOWN: ['recent move down'],
        BIG_UP: ['recent move up'],
        BIG_DOWN: ['recent move down']
      }
    }
  }.with_indifferent_access

  def initialize(indicator, tokens)
    @indicator = indicator
    @tokens = tokens
  end

  def to_s
    @tokens.map { |token| TEXTS.dig(@indicator, token)&.sample }.join(' ')
  end

  def details
    tks = @tokens.group_by { |token| parts(token)[0] }
    tks.map { |type, tokens| "  - #{DETAILS.dig(@indicator, type, parts(tokens.sample)[1]).sample}" }.join("\n")
  end

  private

  def parts(token)
    p = token.split('_')
    [p.first, p[1..-1].join('_')]
  end
end
