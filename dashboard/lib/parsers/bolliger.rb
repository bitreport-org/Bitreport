# frozen_string_literal: true

module Parsers
  class Bollinger
    private

    def data
      @data ||= {
        BANDS_SQUEEZE: {
          texts: ['Bollinger Bands are getting tight what usually leads to new big move.', 'Bollinger Bands are squeezing.'],
          direction: :unknown,
          conclusions: [:big_move]
        },
        BANDS_EXPANDED: {
          texts: ['We can see Bollinger Bands expanding.'],
          direction: :unknown,
          conclusions: [:small_correction]
        },
        PRICE_BREAK_UP: {
          texts: ['The price broke above upper band recently.'],
          direction: :down,
          conclusions: [:small_correction]
        },
        PRICE_BREAK_DOWN: {
          texts: ['The price was below lower Bollinger Bands.'],
          direction: :up,
          conclusions: [:small_correction]
        },
        PRICE_BETWEEN: {
          texts: ['Price stays in the middle of Bollinger Bands.'],
          direction: :unknown,
          conclusions: []
        },
        PRICE_ONBAND_UP: {
          texts: ['We\'re almost touching upper band now.'],
          direction: :down,
          conclusions: [:possible_reversal, :small_correction]
        },
        PRICE_ONBAND_DOWN: {
          texts: ['We\'re really close to the lower band.'],
          direction: :up,
          conclusions: [:possible_reversal, :small_correction]
        }
      }.with_indifferent_access
    end
  end
end
