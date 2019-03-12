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
      pair.request_data_fill
      redirect_to pairs_path, notice: 'Pair filled'
    end

    def destroy
      pair.destroy!
      redirect_to pairs_path, notice: 'Pair destroyed.'
    end

    private

    def pair
      @pair ||= Pair.find(params[:id])
    end

    def pair_params
      params.require(:pair).permit(:symbol, :name, :tags)
    end
  end
end
