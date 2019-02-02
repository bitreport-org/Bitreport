# frozen_string_literal: true

module Reports
  class ChartGenerator < Service
    validates :data, :indicators, presence: true

    def initialize(data:, indicators:)
      @data = data
      @indicators = indicators
    end

    private

    attr_reader :data, :indicators

    def run
      Plotter.new(timestamps: data['dates'], indicators: data['indicators'].slice(*indicators)).plot # TODO: chart_data should be wrapped in an object that filters indicators automatically
    end
  end
end
