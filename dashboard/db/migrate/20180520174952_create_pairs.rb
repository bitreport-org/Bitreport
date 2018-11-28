# frozen_string_literal: true

class CreatePairs < ActiveRecord::Migration[5.1]
  def change
    create_table :pairs do |t|
      t.string :symbol, null: false, index: true, unique: true
      t.string :name
      t.string :exchange
      t.timestamp :last_updated_at
    end
  end
end
