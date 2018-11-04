# frozen_string_literal: true

module Admin
  class TwitterResponsesController < AdminController
    skip_before_action :verify_authenticity_token, if: :allowed_by_magic_token?

    def index
      redirect_to new_twitter_response_path
    end

    def new
      @twitter_response = TwitterResponse.new
    end

    def show
      @twitter_response = TwitterResponse.find(params[:id])
      @twitter_image = @twitter_response.twitter_image
    end

    def create
      @twitter_response = TwitterResponse.new(twitter_response_params)
      tag = @twitter_response.cashtag

      @twitter_image = TwitterImage.new(symbol: tag + 'USD',
                                        timeframe: @twitter_response.timeframe || TwitterImage::TIMEFRAMES.sample,
                                        limit: 100 + rand(100),
                                        indicators: [%w(RSI MACD).sample, [%w(SMA wedge), %w(BB wedge), %w(BB levels), %w(ICM levels)].sample].flatten)

      @twitter_image.validate!

      if @twitter_image.indicators.include?('levels')
        levels = @twitter_image.raw_data['indicators']['levels']
        @twitter_image.levels = [levels['support'].sort.last, levels['resistance'].sort.first]
      end

      @twitter_image.comment ||= @twitter_image.raw_data['indicators'].slice(*(%w(price volume) + @twitter_image.indicators)).flat_map do |indicator, params|
        if params['info'].any?
          [indicator.upcase, TextGenerator.new(indicator, params['info']).details]
        end
      end.compact.join("\n")
      @twitter_image.image = @twitter_image.image_file

      @twitter_response.twitter_image = @twitter_image

      if @twitter_response.save
        respond_to do |format|
          format.html { redirect_to @twitter_response }
          format.json { render json: { id: @twitter_response.id, preview:  @twitter_image.reload.image_url(:original)} }
        end
      else
        render :new
      end
    rescue => e
      respond_to do |format|
        format.html { raise e }
        format.json { render json: { error: e.full_message } }
      end
    end

    def publish
      @twitter_response = TwitterResponse.find(params[:id])
      @twitter_image = @twitter_response.twitter_image

      client = Twitter::REST::Client.new do |config|
        config.consumer_key = Settings.twitter.api_key
        config.consumer_secret = Settings.twitter.api_secret
        config.access_token = Settings.twitter.access_token
        config.access_token_secret = Settings.twitter.access_token_secret
      end
      response = client.update_with_media(tweet_message,
                               @twitter_image.image[:original].download,
                               in_reply_to_status_id: @twitter_response.in_reply_to,
                               auto_populate_reply_metadata: true)
      @twitter_image.touch(:published_at)
      respond_to do |format|
        format.html { redirect_to twitter_response_path(@twitter_response) }
        format.json { render json: { url: response.uri } }
      end
    end

    private

    def tweet_message
      [
        "Beep-a-boop 🤖 Our TA bot created this chart for #{twitter_pair}. It's still in very early beta, so there are many things that can break. What do you think about it? Feel free to share your thoughts as a reply or via DM 🙌",
        "We've analyzed #{twitter_pair} for you. We'd like to hear your thoughts about it.",
        "Here is #{twitter_pair} analysis done by ou TA bot. Do you have any thoughts about it?",
        "We've been working on automating TA for crypto. This is what our bot generates for #{twitter_pair}. If you have any thoughts about it drop us a DM or write a reply to this tweet.",
        "Hi. I'm a bot that charts crypto automatically. What do you think about this one?"
      ].sample
    end

    def twitter_pair
      @twitter_image.pair.tags.sample || @twitter_image.pair.name
    end

    def allowed_by_magic_token?
      %w(create publish).include?(params[:action]) && params[:magic_token] && Digest::SHA256.hexdigest(params[:magic_token]) == 'bbd88faacbe8df40efe7689c1f1b99c3ebf5bb2bf695f33d263f5e8ea7c76a20'
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def twitter_response_params
      params.require(:twitter_response).permit(:url, :cashtag, :timeframe)
    end
  end
end
