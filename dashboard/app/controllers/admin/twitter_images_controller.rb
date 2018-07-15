# frozen_string_literal: true

module Admin
  class TwitterImagesController < AdminController
    before_action :set_twitter_image, only: %i[edit update preview destroy]

    def index
      redirect_to new_twitter_image_path
    end

    def new
      @twitter_image = TwitterImage.new
    end

    def create
      @twitter_image = TwitterImage.new(twitter_image_params)

      if @twitter_image.save
        redirect_to edit_twitter_image_path(@twitter_image)
      else
        render :new
      end
    end

    def update
      @twitter_image.assign_attributes(twitter_image_params)
      @twitter_image.image = @twitter_image.image_file

      if @twitter_image.save
        redirect_to @twitter_image.image_url(:original)
      else
        render :edit
      end
    end

    def edit
      @levels = @twitter_image.raw_data['indicators']['levels'].map do |type, levels|
        levels.map do |level|
          [type.capitalize, level]
        end
      end.flatten
      @twitter_image.comment ||= @twitter_image.raw_data['indicators'].slice(*(%w(price volume) + @twitter_image.indicators).shuffle).flat_map do |indicator, params|
        TextGenerator.new(indicator, params['info']) if params['info']
      end
    end

    def preview
      @twitter_image.assign_attributes(twitter_image_params)

      if @twitter_image.valid?
        send_data(@twitter_image.preview_image, disposition: 'inline', type: 'image/png')
      else
        Rails.logger.debug("Image generation error: #{@twitter_image.errors.full_messages}")
        send_data('', disposition: 'inline', type: 'image/png')
      end
    end

    def destroy
      @twitter_image.destroy
      redirect_to twitter_images_path, notice: 'Twitter image was successfully destroyed.'
    end

    private

    # Use callbacks to share common setup or constraints between actions.
    def set_twitter_image
      @twitter_image = params[:id] ? TwitterImage.find(params[:id]) : TwitterImage.new
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def twitter_image_params
      params.require(:twitter_image).permit(:symbol, :timeframe, :limit, :comment,
                                            indicators: [], levels: [])
    end
  end
end
