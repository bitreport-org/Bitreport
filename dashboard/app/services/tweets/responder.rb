# frozen_string_literal: true

module Tweets
  class Responder < Service
    validates :tweet_id, :symbols, :original_message, presence: true
    validates :screen_name, exclusion: { in: ['Bitreport_org'] }

    before_execute :create_twitter_post

    def initialize(tweet_id:, symbols:, screen_name:, original_message:)
      @tweet_id = tweet_id
      @symbols = symbols
      @screen_name = screen_name
      @original_message = original_message
    end

    private

    attr_reader :tweet_id, :symbols, :screen_name, :original_message, :twitter_post

    def run
      return if symbols.blank?

      report = Reports::Creator.new(pair: pair,
                                    timeframe: 6,
                                    indicators: %w[RSI wedge double_top double_bottom levels]).call
      Tweets::Publisher.new(twitter_post: twitter_post,
                            message: "Hi. Here is your report for #{pair.symbol}",
                            report: report).call
    rescue Service::ValidationError => e
      Tweets::Publisher.new(twitter_post: twitter_post, message: "We had some trouble with your request. #{e.message}").call
    rescue StandardError => e
      Raven.capture_exception(e)
      Tweets::Publisher.new(twitter_post: twitter_post, message: "Something is broken on our end. Our developers will take a look at it. If you meet them ask them about issue #{Raven.last_event_id}").call
    end

    def create_twitter_post
      @twitter_post = TwitterPost.create!(in_reply_to: tweet_id, original_message: original_message)
    end

    def pair
      @pair ||= Pairs::Finder.new(symbol: symbols.first).call
    end
  end
end
