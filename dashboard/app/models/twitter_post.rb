# frozen_string_literal: true

class TwitterPost < ApplicationRecord
  belongs_to :report

  def self.latest_replied_tweet_id
    order(in_reply_to: :desc).pluck(:in_reply_to).first
  end
end
