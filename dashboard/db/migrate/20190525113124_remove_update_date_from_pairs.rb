# frozen_string_literal: true

class RemoveUpdateDateFromPairs < ActiveRecord::Migration[5.2]
  def change
    remove_column :pairs, :last_updated_at, :datetime
  end
end
