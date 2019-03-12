# frozen_string_literal: true

module Tweets
  class Responder < Service
    validates :tweet_id, presence: true

    def initialize(tweet_id:, symbols:, screen_name: nil)
      @tweet_id = tweet_id
      @symbols = symbols
      @screen_name = screen_name
    end

    private

    attr_reader :tweet_id, :symbols, :screen_name

    def run
      return if screen_name == 'Bitreport_org'
      return unless symbols.any?

      # TODO: Pass report to some twitter poster service
      report = Reports::Creator.new(pair: pair, timeframe: 6, indicators: %w[RSI wedge]).call
      new_tweet = publish(report)
      TwitterPost.create!(report: report, in_reply_to: tweet_id, tweet_id: new_tweet.id)
    rescue Service::ValidationError => e # we should actually look what's inside :P
      send_instructions
      Raven.capture_exception(e) if defined?(Raven)
    end

    def pair
      @pair ||= Pairs::Finder.new(symbol: symbols.first).call
    end

    def publish(report)
      return Twitter::Tweet.new(id: 0) unless Settings.twitter.post_to_twitter

      client.update_with_media(formatted("Hi. Here is your report for #{pair.symbol}"),
                               report.image[:original].download,
                               tweet_params)
    end

    def send_instructions
      return Twitter::Tweet.new(id: 0) unless Settings.twitter.post_to_twitter

      client.update(formatted("Hi. It seems like we had some trouble with your request. Our developers will take a look at it now"),
                    tweet_params)
    end

    def formatted(text)
      return text if screen_name.blank?

      "@#{screen_name} #{text}"
    end

    def tweet_params
      @tweet_params ||= {
        in_reply_to_status_id: tweet_id,
        auto_populate_reply_metadata: screen_name.blank?
      }
    end

    # TODO: Extract twitter client globally
    def client
      @client ||= Twitter::REST::Client.new do |config|
        config.consumer_key = Settings.twitter.api_key
        config.consumer_secret = Settings.twitter.api_secret
        config.access_token = Settings.twitter.access_token
        config.access_token_secret = Settings.twitter.access_token_secret
      end
    end
  end
end
