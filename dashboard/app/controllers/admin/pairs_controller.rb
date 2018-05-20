# frozen_string_literal: true

module Admin
  class PairsController < AdminController
    def index
      @pairs = Pair.order(symbol: :asc)
    end

    def new
      @pair = Pair.new
    end

    def create
      @pair = Pair.new(pair_params)

      if @pair.save
        redirect_to pairs_path, notice: "#{@pair.symbol} created"
      else
        render :new
      end
    end

    # This one is temporary
    def fill
      @pair = Pair.find(params[:id])
      @pair.request_data_fill
      redirect_to pairs_path, notice: 'Pair filled'
    end

    def destroy
      @pair = Pair.find(params[:id])
      @pair.destroy
      redirect_to pairs_path, notice: 'Pair destroyed.'
    end

    private

    def pair_params
      params.require(:pair).permit(:symbol, :name, :exchange)
    end
  end
end
