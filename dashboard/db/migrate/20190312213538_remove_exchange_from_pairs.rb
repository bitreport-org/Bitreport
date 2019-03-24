# frozen_string_literal: true

class RemoveExchangeFromPairs < ActiveRecord::Migration[5.2]
  def change
    remove_column :pairs, :exchange, :string
  end
end
