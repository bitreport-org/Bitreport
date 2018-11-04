class AddMediaIdToTwitterImages < ActiveRecord::Migration[5.2]
  def change
    add_column :twitter_images, :media_id, :string
  end
end
