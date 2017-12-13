# frozen_string_literal: true

module Admin
  class TwitterImagesController < AdminController
    before_action :set_twitter_image, only: %i[show destroy]

    # GET /twitter_images
    def index
      @twitter_images = TwitterImage.order(created_at: :desc).limit(9)
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
        chart = MiniMagick::Image.read(img)
        template = MiniMagick::Image.open(Rails.root.join('vendor', 'template.png'))
        ticker = "#{twitter_image_params[:symbol]} #{twitter_image_params[:timeframe]}"
        template = template.composite(chart) do |c|
          c.compose 'over'
          c.gravity 'center'
          c.geometry '1400x930-250+25'
        end
        result = template.combine_options do |c|
          c.font Rails.root.join('vendor', 'PT_Sans-Web-Bold.ttf')
          c.pointsize 50
          c.fill '#EEEEEE'
          c.region '735x110'
          c.gravity 'East'
          c.draw "text 0,0 '#{ticker}'"
          c.font Rails.root.join('vendor', 'PT_Sans-Web-Bold.ttf')
          c.pointsize 50
          c.fill '#b0db43'
          c.region '580x110+750'
          c.gravity 'West'
          c.draw "text 0,0 '#{twitter_image.price}'"
          c.font Rails.root.join('vendor', 'PT_Sans-Web-Regular.ttf')
          c.pointsize 16
          c.fill '#363631'
          c.region '500x40+1400+1020'
          c.gravity 'center'
          c.draw "text 0,0 'Generated on #{Time.zone.now}'"
        end
        out = StringIO.new
        result.write out
        send_data(out.string, disposition: 'inline', type: 'image/png')
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
      @twitter_image = TwitterImage.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def twitter_image_params
      params.require(:admin_twitter_image).permit(:symbol, :timeframe, :limit, :levels,
                                                  indicators: [], patterns: [])
    end
  end
end
