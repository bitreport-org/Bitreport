class WalletController < ApplicationController
  def use
    wallet = Wallet.find(session[:wallet_id])
    wallet&.update(used: true)
    head :success
  end
end
