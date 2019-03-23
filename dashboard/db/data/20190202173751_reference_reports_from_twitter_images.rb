# frozen_string_literal: true

class ReferenceReportsFromTwitterImages < ActiveRecord::Migration[5.2]
  class MigrationTwitterImage < ActiveRecord::Base
    self.table_name = :twitter_images
    belongs_to :pair
    belongs_to :report
  end

  class MigrationReport < ActiveRecord::Base
    self.table_name = :reports
    belongs_to :pair
  end

  def up
    MigrationTwitterImage.find_each do |twitter_image|
      report = MigrationReport.create!(pair: twitter_image.pair,
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
