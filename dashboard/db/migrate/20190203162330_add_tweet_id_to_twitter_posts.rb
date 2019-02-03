# frozen_string_literal: true

class AddTweetIdToTwitterPosts < ActiveRecord::Migration[5.2]
  def change
    add_column :twitter_posts, :tweet_id, :string
  end
end
