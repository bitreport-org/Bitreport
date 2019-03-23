# frozen_string_literal: true

class AddOriginalMessageToTwitterPosts < ActiveRecord::Migration[5.2]
  def change
    add_column :twitter_posts, :original_message, :string
  end
end
