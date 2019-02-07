# frozen_string_literal: true

class AddMissingTimestamps < ActiveRecord::Migration[5.2]
  def change
    add_timestamps :pairs, default: Time.zone.now
    change_column_default :pairs, :created_at, from: Time.zone.now, to: nil
    change_column_default :pairs, :updated_at, from: Time.zone.now, to: nil
  end
end
