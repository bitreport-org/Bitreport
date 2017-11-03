class HomeController < ApplicationController
  def index
    @address = session[:address] ||= initialize_wallet.address
  end

  private

  def initialize_wallet
    wallet = Wallet.create
    session[:wallet_id] = wallet.id
    wallet
  end
end
