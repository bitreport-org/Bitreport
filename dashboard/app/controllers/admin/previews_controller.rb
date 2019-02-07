# frozen_string_literal: true

module Admin
  class PreviewsController < AdminController
    def show
      report = Reports::Creator.new(pair: pair,
                                    timeframe: params[:timeframe] || 6,
                                    indicators: (params[:indicators] || 'RSI,wedge').split(',')).call
      send_data(report.image[:original].read, disposition: 'inline', type: 'image/png')
    end

    private

    def pair
      @pair ||= Pairs::Finder.new(symbol: params[:symbol]).call
    end
  end
end
