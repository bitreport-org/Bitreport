# frozen_string_literal: true

module Reports
  class CommentGenerator < Service
    validates :data, presence: true

    def initialize(data:, indicators:)
      @data = data
      @indicators = indicators
    end

    private

    attr_reader :data, :indicators

    def run
      indicators_data.flat_map { |indicator, data| text_for(indicator, data) }.compact.join("\n")
    end

    def indicators_data
      data['indicators'].slice(*indicators)
    end

    def text_for(indicator, data)
      return unless data['info'].any?

      [indicator.upcase, TextGenerator.new(indicator, data['info']).details]
    end
  end
end
