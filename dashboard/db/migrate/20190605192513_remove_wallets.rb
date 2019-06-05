# frozen_string_literal: true

class RemoveWallets < ActiveRecord::Migration[5.2]
  def up
    drop_table :wallets
  end
end
