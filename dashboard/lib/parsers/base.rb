# frozen_string_literal: true

module Parsers
  class Base
    def initialize(tokens)
      @tokens = tokens
    end

    def parse
      @tokens.map { |token| data[token] }
    end
  end
end
