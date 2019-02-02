# frozen_string_literal: true

class Report < ApplicationRecord
  include ImageUploader[:plot]

  belongs_to :pair

  validates :limit, numericality: true, inclusion: { in: 80..200 }
  validates :timeframe, presence: true, inclusion: { in: %[1, 2, 3, 6, 12, 24].freeze }
  validate :indicators, presence: true
  validate :levels, presence: true
end
