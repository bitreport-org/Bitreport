# frozen_string_literal: true

class CreateReports < ActiveRecord::Migration[5.2]
  def change
    create_table :reports do |t|
      t.references :pair, foreign_key: true, null: false
      t.integer :limit, null: false, default: 100
      t.integer :timeframe, null: false, default: 6
      t.string :indicators, array: true, null: false, default: []
      t.text :comment
      t.text :image_data

      t.timestamps
    end

    add_reference :twitter_images, :report, foreign_key: true, null: false
  end
end
