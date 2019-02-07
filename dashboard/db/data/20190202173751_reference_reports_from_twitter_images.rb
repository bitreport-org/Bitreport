# frozen_string_literal: true

class ReferenceReportsFromTwitterImages < ActiveRecord::Migration[5.2]
  class TwitterImage < ActiveRecord::Base
    belongs_to :pair
    belongs_to :report
  end

  class Report < ActiveRecord::Base
    belongs_to :pair
  end

  def up
    TwitterImage.find_each do |twitter_image|
      report = Report.create!(pair: twitter_image.pair,
                              limit: twitter_image.limit,
                              timeframe: twitter_image.timeframe,
                              indicators: twitter_image.indicators,
                              comment: twitter_image.comment,
                              image_data: twitter_image.image_data)
      twitter_image.update!(report: report)
    end
  end

  def down
    raise ActiveRecord::IrreversibleMigration
  end
end
