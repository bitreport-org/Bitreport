# frozen_string_literal: true

class CreateTwitterResponses < ActiveRecord::Migration[5.2]
  def change
    create_table :twitter_responses do |t|
      t.references :twitter_image, foreign_key: true
      t.string :in_reply_to
    end
  end
end
