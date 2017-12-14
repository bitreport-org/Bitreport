class HomeController < ApplicationController
  def index; end

  def show
    @address = session[:address] ||= initialize_wallet.address
    render params[:page]
  end

  private

  def initialize_wallet
    wallet = Wallet.create
    session[:wallet_id] = wallet.id
    wallet
  end
end
