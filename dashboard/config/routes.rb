Rails.application.routes.draw do
  get 'soon/landing', to: 'home#show', page: :landing
  post 'wallet/use'

  namespace :admin do
    resources :twitter_images
    get :twitter_image_preview, to: 'twitter_images#preview'
  end

  root to: 'home#index'
end
