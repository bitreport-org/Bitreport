# frozen_string_literal: true

module Admin
  class TwitterImagesController < AdminController
    before_action :set_twitter_image, only: %i[show destroy]

    # GET /twitter_images
    def index
      redirect_to new_admin_twitter_image_path
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

    def preview
      twitter_image = TwitterImage.new(twitter_image_params)

      if twitter_image.valid?
        img = twitter_image.preview_image
        send_data(img, disposition: 'inline', type: 'image/png')
      else
        send_data('', disposition: 'inline', type: 'image/png')
      end
    end

    def data
      twitter_image = TwitterImage.new(twitter_image_params)

      if twitter_image.valid?
        render json: twitter_image.raw_data
      else
        head :bad_request
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
      params.require(:admin_twitter_image).permit(:symbol, :timeframe, :limit, :levels, :comment,
                                                  :patterns, indicators: [])
    end
  end
end
