# frozen_string_literal: true

class RemoveUnusedMethodsFromTwitterImages < ActiveRecord::Migration[5.2]
  def up
    remove_reference :twitter_images, :pair
    remove_column :twitter_images, :symbol
    remove_column :twitter_images, :timeframe
    remove_column :twitter_images, :limit
    remove_column :twitter_images, :indicators
    remove_column :twitter_images, :levels
    remove_column :twitter_images, :patterns
    remove_column :twitter_images, :comment
    remove_column :twitter_images, :image_data
  end

  def down
    raise ActiveRecord::IrreversibleMigration
  end
end
