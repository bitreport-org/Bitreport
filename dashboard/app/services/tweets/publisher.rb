# frozen_string_literal: true

module Tweets
  class Publisher < Service
    validates :twitter_post, :message, presence: true

    def initialize(twitter_post:, message:, report: nil)
      @twitter_post = twitter_post
      @message = message
      @report = report
    end

    private

    attr_reader :twitter_post, :message, :report

    def run
      tweet = post_to_twitter
      twitter_post.update!(tweet_id: tweet.id,
                           message: message,
                           report: report,
                           published_at: Time.current)
    end

    def post_to_twitter
      return Twitter::Tweet.new(id: 0) unless Settings.twitter.post_to_twitter

      report ? post_with_media : post_text
    end

    def post_with_media
      client.update_with_media(message, report.image[:original].download, tweet_params)
    end

    def post_text
      client.update(message, tweet_params)
    end

    def tweet_params
      @tweet_params ||= {
        in_reply_to_status_id: twitter_post.in_reply_to,
        auto_populate_reply_metadata: true
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
