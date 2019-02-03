# frozen_string_literal: true

module Tweets
  class Responder < Service
    validates :tweet_id, :tweet_text, presence: true

    def initialize(tweet_id:, tweet_text:)
      @tweet_id = tweet_id
      @tweet_text = tweet_text
    end

    private

    attr_reader :tweet_id, :tweet_text

    def run
      return unless symbols

      # Pass report to some twitter poster service
      report = Reports::Creator.new(pair: pair, timeframe: 6, indicators: %w[RSI wedge]).call
      new_tweet = publish(report)
      TwitterPost.create!(report: report, in_reply_to: tweet_id, tweet_id: new_tweet.id)
    end

    def pair
      @pair ||= Pair.find_matching(symbols.first)
    end

    def symbols
      @symbols ||= tweet_text.scan(/\$(\w+)/).flatten
    end

    def publish(report)
      return Twitter::Tweet.new(id: 0) unless Settings.twitter.post_to_twitter

      @posted_tweet ||= client.update_with_media("Hi. Here is your report for #{pair.symbol}",
                                                 report.image[:original].download,
                                                 in_reply_to_status_id: tweet_id)
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
