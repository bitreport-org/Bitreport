# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 2019_05_25_113124) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "data_migrations", primary_key: "version", id: :string, force: :cascade do |t|
  end

  create_table "pairs", force: :cascade do |t|
    t.string "symbol", null: false
    t.string "name"
    t.string "tags", array: true
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["symbol"], name: "index_pairs_on_symbol"
  end

  create_table "push_devices", force: :cascade do |t|
    t.string "endpoint", null: false
    t.string "p256dh"
    t.string "auth"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["endpoint"], name: "index_push_devices_on_endpoint"
  end

  create_table "reports", force: :cascade do |t|
    t.bigint "pair_id", null: false
    t.integer "limit", default: 100, null: false
    t.integer "timeframe", default: 6, null: false
    t.string "indicators", default: [], null: false, array: true
    t.text "comment"
    t.text "image_data"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["pair_id"], name: "index_reports_on_pair_id"
  end

  create_table "twitter_posts", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.datetime "published_at"
    t.string "in_reply_to"
    t.bigint "report_id"
    t.string "tweet_id"
    t.string "message"
    t.string "original_message"
    t.index ["in_reply_to"], name: "index_twitter_posts_on_in_reply_to"
    t.index ["report_id"], name: "index_twitter_posts_on_report_id"
  end

  create_table "wallets", force: :cascade do |t|
    t.boolean "used", default: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  add_foreign_key "reports", "pairs"
  add_foreign_key "twitter_posts", "reports"
end
