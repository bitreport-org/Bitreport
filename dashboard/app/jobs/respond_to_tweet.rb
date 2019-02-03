# frozen_string_literal: true

class RespondToTweet < ApplicationJob
  def perform(tweet_id:, text:)
    Rails.logger.debug("Responding to (#{tweet_id}): #{text}")
    Tweets::Responder.new(tweet_id: tweet_id, tweet_text: text).call
  end
end
