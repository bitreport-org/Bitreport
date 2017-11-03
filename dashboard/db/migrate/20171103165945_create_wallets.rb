class CreateWallets < ActiveRecord::Migration[5.1]
  def change
    create_table :wallets do |t|
      t.boolean :used, default: false

      t.timestamps
    end
  end
end
