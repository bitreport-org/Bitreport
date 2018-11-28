# frozen_string_literal: true

class Wallet < ApplicationRecord
  def address
    @address ||= BtcWallet.new(id).derive
  end
end
