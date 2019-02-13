# frozen_string_literal: true

class TwitterPost < ApplicationRecord
  scope :published, -> { where.not(published_at: nil) }

  belongs_to :report, optional: true

  validates :in_reply_to, presence: true, uniqueness: true

  def self.latest_replied_tweet_id
    order(in_reply_to: :desc).pluck(:in_reply_to).first
  end
end
