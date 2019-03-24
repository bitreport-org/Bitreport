# frozen_string_literal: true

module Admin
  class PairsController < AdminController
    def index
      @pairs = Pair.order(symbol: :asc)
    end

    def new
      @pair = Pair.new
    end

    def edit
      @pair = pair
    end

    def create
      @pair = Pairs::Creator.new(symbol: pair_params[:symbol],
                                 name: pair_params[:name],
                                 tags: pair_params[:tags]).call

      redirect_to pairs_path, notice: "#{@pair.symbol} created"
    rescue Service::ValidationError => e
      @pair = Pair.new(pair_params)
      @pair.errors.add(:base, e.message)
      render :new
    end

    def update
      if pair.update(pair_params)
        redirect_to pairs_path, notice: "#{@pair.symbol} updated"
      else
        render :edit
      end
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
