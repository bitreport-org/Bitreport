# frozen_string_literal: true

class RespondToTweet < ApplicationJob
  discard_on Service::ValidationError

  def perform(tweet_id:, text:, screen_name:)
    Rails.logger.debug("Responding to @#{screen_name}'s (#{tweet_id}): #{text}")
    Tweets::Responder.new(tweet_id: tweet_id, tweet_text: text, screen_name: screen_name).call
  end
end
