class TwitterResponse < ApplicationRecord
  attr_reader :url
  attr_accessor :timeframe

  belongs_to :twitter_image
  validates :in_reply_to, presence: true

  def url=(val)
    @url = URI(val)
    self.in_reply_to = url.path.split('/').last
  end

  def cashtag=(val)
    return unless val.present?
    if(val.length > 3 && %w(btc usd).include?(val[-3..-1]))
      super(val)
    else
      super(val + 'USD')
    end
  end

  def cashtag
    @cashtag ||= fetch_cashtags.first
  end

  private

  def fetch_cashtags
    return [] unless in_reply_to
    client = Twitter::REST::Client.new do |config|
      config.consumer_key = Settings.twitter.api_key
      config.consumer_secret = Settings.twitter.api_secret
      config.access_token = Settings.twitter.access_token
      config.access_token_secret = Settings.twitter.access_token_secret
    end
    response = client.status(in_reply_to, include_entities: true)
    response.symbols? ? response.symbols.map(&:text) : []
  end
end
