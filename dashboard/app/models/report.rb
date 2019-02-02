# frozen_string_literal: true

class Report < ApplicationRecord
  include ImageUploader[:image]

  belongs_to :pair

  validates :limit, numericality: true, inclusion: { in: 80..200 }
  validates :timeframe, presence: true, inclusion: { in: [1, 2, 3, 6, 12, 24].freeze }
  validates :indicators, presence: true
  validates :comment, presence: true
end
