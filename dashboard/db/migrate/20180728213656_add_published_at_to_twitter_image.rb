class AddPublishedAtToTwitterImage < ActiveRecord::Migration[5.2]
  def change
    add_column :twitter_images, :published_at, :timestamp
  end
end
