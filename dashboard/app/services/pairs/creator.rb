# frozen_string_literal: true

module Pairs
  class Creator < Service
    validates :symbol, :full_symbol, presence: true

    before_validation :extract_parts

    def initialize(symbol:, name: nil, tags: [])
      @symbol = symbol
      @name = name.presence
      @tags = tags.presence
    end

    private

    attr_reader :symbol, :first_part, :second_part, :pair

    def run
      @pair = Pair.create!(symbol: full_symbol,
                           name: name,
                           tags: Array.wrap(tags).uniq.join(' ').split)
      data_fill
      pair
    end

    def extract_parts
      regex = /(\w{3,})(BTC|USD[TC]?|ETH|EUR)$/i
      @first_part = symbol.gsub(regex, '\1').upcase
      @second_part = (symbol.match(regex).try(:[], 2) || (first_part == 'BTC' ? 'USD' : 'BTC')).upcase
    end

    def data_fill
      @data_fill ||= Pairs::Filler.new(pair: pair).call
    end

    def full_symbol
      @full_symbol ||= "#{first_part}#{second_part}".upcase
    end

    def name
      @name ||= first_part
    end

    def tags
      @tags ||= %W[##{name} ##{first_part} $#{first_part}]
    end
  end
end
