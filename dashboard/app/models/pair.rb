# frozen_string_literal: true

class Pair < ApplicationRecord
  has_many :reports, dependent: :restrict_with_error

  validates :symbol, presence: true, uniqueness: true, format: /\A[A-Z0-9]+\z/
  validates :name, presence: true

  def self.find_matching(val)
    where('symbol LIKE ?', "#{val.upcase}%").first!
  end

  def tags=(val)
    val.is_a?(Array) ? super : super(val&.split)
  end
end
