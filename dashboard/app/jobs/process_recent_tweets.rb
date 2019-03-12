# frozen_string_literal: true

class ProcessRecentTweets < ApplicationJob
  QUERY = '+Bitreport_org +@Bitreport_org +to:Bitreport_org -from:Bitreport_org -filter:retweets'.freeze

  def perform
    Rails.logger.info('Processing new Tweets')
    recent_mentions.each do |tweet|
      RespondToTweet.perform_later(tweet_id: tweet.id,
                                   text: tweet.text,
                                   symbols: tweet.symbols.map(&:text),
                                   user_screen_name: tweet.user.screen_name)
    end
  end

  private

  def recent_mentions
    @recent_mentions ||= client.search(QUERY,
                                       count: 100, # This is twitter API maximum
                                       result_type: :recent,
                                       include_entities: true,
                                       since_id: TwitterPost.latest_replied_tweet_id)
  end

  def client
    @client ||= Twitter::REST::Client.new do |config|
      config.consumer_key = Settings.twitter.api_key
      config.consumer_secret = Settings.twitter.api_secret
      config.access_token = Settings.twitter.access_token
      config.access_token_secret = Settings.twitter.access_token_secret
    end
  end
end
