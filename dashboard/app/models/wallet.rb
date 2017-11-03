class Wallet < ApplicationRecord
  def address
    BtcWallet.derive(id)
  end
end
