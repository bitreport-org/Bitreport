# frozen_string_literal: true

class ProcessRecentTweets < ApplicationJob
  QUERY = '+Bitreport_org +@Bitreport_org +to:Bitreport_org -from:Bitreport_org -filter:retweets'.freeze

  def perform
    Rails.logger.info('Processing new Tweets')
    recent_mentions.each do |tweet|
      next if tweet.user.screen_name == 'Bitreport_org'
      next if tweet.id == latest_replied_tweet_id

      RespondToTweet.perform_later(tweet_id: tweet.id,
                                   text: tweet.text,
                                   symbols: tweet.symbols.map(&:text),
                                   screen_name: tweet.user.screen_name)
    end
  end

  private

  def recent_mentions
    @recent_mentions ||= client.search(QUERY,
                                       result_type: :recent,
                                       include_entities: true,
                                       since_id: latest_replied_tweet_id)
  end

  def latest_replied_tweet_id
    @latest_replied_tweet_id ||= TwitterPost.order(in_reply_to: :desc).pluck(:in_reply_to).first
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
