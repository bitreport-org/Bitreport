# frozen_string_literal: true

class MigrateTwitterResponsesIntoTwitterImages < ActiveRecord::Migration[5.2]
  def up
    add_column :twitter_images, :in_reply_to, :string

    execute <<~SQL
      UPDATE twitter_images
         SET in_reply_to = twitter_responses.in_reply_to
        FROM twitter_responses
       WHERE twitter_images.id = twitter_responses.twitter_image_id
    SQL

    drop_table :twitter_responses
  end

  def down
    create_table :twitter_responses do |t|
      t.references :twitter_image, foreign_key: true
      t.string :in_reply_to
    end

    execute <<~SQL
      INSERT INTO twitter_responses (twitter_image_id, in_reply_to)
           SELECT id, in_reply_to
             FROM twitter_images
            WHERE twitter_images.in_reply_to IS NOT NULL
    SQL

    remove_column :twitter_images, :in_reply_to
  end
end
