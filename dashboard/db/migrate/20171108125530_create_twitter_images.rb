class CreateTwitterImages < ActiveRecord::Migration[5.1]
  def change
    create_table :twitter_images do |t|
      t.string :name
      t.text :image_data

      t.timestamps
    end
  end
end
