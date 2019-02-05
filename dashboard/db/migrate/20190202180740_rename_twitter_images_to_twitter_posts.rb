# frozen_string_literal: true

class RenameTwitterImagesToTwitterPosts < ActiveRecord::Migration[5.2]
  def change
    rename_table :twitter_images, :twitter_posts
  end
end
