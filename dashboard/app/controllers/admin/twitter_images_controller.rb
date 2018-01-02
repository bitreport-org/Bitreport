# frozen_string_literal: true

module Admin
  class TwitterImagesController < AdminController
    before_action :set_twitter_image, only: %i[show edit update preview destroy]

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
        redirect_to edit_admin_twitter_image_path(@twitter_image)
      else
        render :new
      end
    end

    def update
      if @twitter_image.update(twitter_image_params)
        redirect_to @twitter_image, notice: 'Twitter image was successfully created.'
      else
        render :edit
      end
    end

    def edit
      @levels = @twitter_image.raw_data['levels'].map do |type, levels|
        levels.map do |level|
          [type.capitalize, level]
        end
      end.flatten
      @patterns = @twitter_image.raw_data['patterns'].flat_map do |name, directions|
        directions.flat_map do |direction, timestamps|
          timestamps.map do |timestamp|
            [TwitterImage::PATTERNS[name], direction == 'up' ? '➚' : '➘', Time.at(timestamp).utc.strftime('%F %H:%M')]
          end
        end
      end.sort { |x, y| x[2] <=> y[2] }.flatten
    end

    def preview
      @twitter_image.assign_attributes(twitter_image_params)

      if @twitter_image.valid?
        img = @twitter_image.preview_image
        send_data(img, disposition: 'inline', type: 'image/png')
      else
        send_data('', disposition: 'inline', type: 'image/png')
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
      @twitter_image = params[:id] ? TwitterImage.find(params[:id]) : TwitterImage.new
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def twitter_image_params
      params.require(:admin_twitter_image).permit(:symbol, :timeframe, :limit, :comment,
                                                  patterns: [], indicators: [], levels: [])
    end
  end
end
