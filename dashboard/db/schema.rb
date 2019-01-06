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

ActiveRecord::Schema.define(version: 2019_01_06_193901) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "pairs", force: :cascade do |t|
    t.string "symbol", null: false
    t.string "name"
    t.string "exchange"
    t.datetime "last_updated_at"
    t.string "tags", null: false, array: true
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

  create_table "twitter_images", force: :cascade do |t|
    t.string "symbol", null: false
    t.string "timeframe", null: false
    t.integer "limit"
    t.string "indicators", array: true
    t.string "levels", array: true
    t.string "patterns", array: true
    t.text "comment"
    t.text "image_data"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "pair_id"
    t.datetime "published_at"
    t.string "media_id"
    t.string "in_reply_to"
    t.index ["pair_id"], name: "index_twitter_images_on_pair_id"
  end

  create_table "wallets", force: :cascade do |t|
    t.boolean "used", default: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

end
