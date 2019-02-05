# frozen_string_literal: true

class AllowNullTagsInPairs < ActiveRecord::Migration[5.2]
  def change
    change_column_null :pairs, :tags, true
  end
end
