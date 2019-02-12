# frozen_string_literal: true

class RefactorTwitterPosts < ActiveRecord::Migration[5.2]
  def change
    remove_column :twitter_posts, :media_id, :string
    remove_index :twitter_posts, :report_id
    change_column_null :twitter_posts, :report_id, true
    add_index :twitter_posts, :report_id
    add_column :twitter_posts, :message, :string
    add_index :twitter_posts, :in_reply_to
  end
end
