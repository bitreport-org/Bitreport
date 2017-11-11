# frozen_string_literal: true

module Admin
  class TwitterImagesController < AdminController
    before_action :set_twitter_image, only: %i[show destroy]

    # GET /twitter_images
    def index
      @twitter_images = TwitterImage.order(created_at: :desc).limit(20)
    end

    # GET /twitter_images/1
    def show; end

    # GET /twitter_images/new
    def new
      @twitter_image = TwitterImage.new
    end

    # POST /twitter_images
    def create
      @twitter_image = TwitterImage.new(twitter_image_params)

      if @twitter_image.save
        redirect_to @twitter_image, notice: 'Twitter image was successfully created.'
      else
        render :new
      end
    end

    # DELETE /twitter_images/1
    def destroy
      @twitter_image.destroy
      redirect_to admin_twitter_images_url, notice: 'Twitter image was successfully destroyed.'
    end

    private

    # Use callbacks to share common setup or constraints between actions.
    def set_twitter_image
      @twitter_image = TwitterImage.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def twitter_image_params
      params.require(:admin_twitter_image).permit(:symbol, :timeframe, :limit, :levels,
                                            indicators: [], patterns: [])
    end
  end
end
