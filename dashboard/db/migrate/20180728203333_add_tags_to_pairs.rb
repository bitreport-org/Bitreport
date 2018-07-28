class AddTagsToPairs < ActiveRecord::Migration[5.2]
  def change
    add_column :pairs, :tags, :string, array: true, null: false
  end
end
