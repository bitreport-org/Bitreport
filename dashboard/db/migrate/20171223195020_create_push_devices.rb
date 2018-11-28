# frozen_string_literal: true

class CreatePushDevices < ActiveRecord::Migration[5.1]
  def change
    create_table :push_devices do |t|
      t.string :endpoint, null: false, index: true, unique: true
      t.string :p256dh
      t.string :auth

      t.timestamps
    end
  end
end
