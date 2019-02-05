# frozen_string_literal: true

module Pairs
  class Creator < Service
    validates :symbol, :exchange, :full_symbol, presence: true

    before_validation :extract_parts, :extract_exchange
    after_execute :request_data_fill

    def initialize(symbol:, name: nil, tags: [], exchange: nil)
      @symbol = symbol
      @name = name
      @tags = tags
      @exchange = exchange
    end

    private

    attr_reader :symbol, :exchange, :first_part, :second_part, :pair

    def run
      @pair = Pair.create!(symbol: full_symbol, name: name, tags: tags, exchange: exchange)
    end

    def extract_parts
      regex = /(\w{3,})(BTC|USD[TC]?|ETH|EUR)$/i
      @first_part = symbol.gsub(regex, '\1').upcase
      @second_part = (symbol.match(regex).try(:[], 2) || (first_part == 'BTC' ? 'USD' : 'BTC')).upcase
    end

    def extract_exchange
      return if Pair::EXCHANGES.include?(exchange)

      @exchange = HTTParty.get('http://core/exchange', query: { pair: full_symbol }).strip
    end

    def request_data_fill
      Pairs::Filler.new(pair: pair).call
    end

    def full_symbol
      @full_symbol ||= "#{first_part}#{second_part}".upcase
    end

    def name
      @name ||= first_part
    end

    def tags
      return @tags if @tags.presence

      @tags = %W[##{name} ##{first_part} $#{first_part}].uniq
    end
  end
end
