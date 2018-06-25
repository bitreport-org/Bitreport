# frozen_string_literal: true

class TokensParser
  PARSERS = {
    BB: Parsers::Bollinger,
    RSI: Parsers::Rsi,
    wedge: Parsers::Wedge,
    channel: Parsers::Channel,
    TDS: Parsers::Tds,
    STOCH: Parsers::Stoch,
    SMA: Parsers::Sma,
    EMA: Parsers::Ema,
    ICM: Parsers::Icm,
    MACD: Parsers::Macd,
    SAR: Parsers::Sar
  }.with_indifferent_access

  def initialize(indicator, tokens)
    @indicator = indicator
    @tokens = tokens
  end

  def parse
    PARSERS[@indicator].new(tokens)
  end
end
