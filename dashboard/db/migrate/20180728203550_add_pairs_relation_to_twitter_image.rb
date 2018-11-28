# frozen_string_literal: true

class AddPairsRelationToTwitterImage < ActiveRecord::Migration[5.2]
  def change
    add_reference :twitter_images, :pair
  end
end
