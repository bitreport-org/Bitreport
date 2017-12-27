class CreateTwitterImages < ActiveRecord::Migration[5.1]
  def change
    create_table :twitter_images do |t|
      t.string :symbol, null: false
      t.string :timeframe, null: false
      t.integer :limit
      t.string :patterns
      t.string :indicators, array: true
      t.string :levels
      t.text :comment
      t.text :image_data

      t.timestamps
    end
  end
end
