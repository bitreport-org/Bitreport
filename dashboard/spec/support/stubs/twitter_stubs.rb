# frozen_string_literal: true

def stub_twitter_login
  stub_request(:post, 'https://api.twitter.com/oauth2/token')
    .to_return(status: 200,
               body: { token_type: 'bearer', access_token: 'access_token' }.to_json,
               headers: { 'Content-Type' => 'application/json' })
end

def stub_twitter_upload
  stub_request(:post, 'https://upload.twitter.com/1.1/media/upload.json')
    .to_return(status: 200,
               body: { media_id: SecureRandom.uuid }.to_json,
               headers: { 'Content-Type' => 'application/json' })
end

def stub_twitter_update
  stub_twitter_login
  stub_twitter_upload
  stub_request(:post, 'https://api.twitter.com/1.1/statuses/update.json')
    .to_return(status: 200,
               body: { id: SecureRandom.uuid }.to_json,
               headers: { 'Content-Type' => 'application/json' })
end
