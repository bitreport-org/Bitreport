# frozen_string_literal: true

class RespondToTweet < ApplicationJob
  discard_on Service::ValidationError

  def perform(tweet_id:, text:, symbols:, screen_name:)
    Rails.logger.debug("Responding to @#{screen_name}'s (#{tweet_id}): #{text}")
    Rails.logger.debug("Found following symbols: #{symbols}")
    Tweets::Responder.new(tweet_id: tweet_id,
                          symbols: symbols,
                          screen_name: screen_name,
                          original_message: text).call
  end
end
