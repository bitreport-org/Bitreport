# frozen_string_literal: true

class PushDevice < ApplicationRecord
  validates :endpoint, presence: true, uniqueness: true

  def keys=(val)
    assign_attributes(val.slice(:p256dh, :auth))
  end
end
