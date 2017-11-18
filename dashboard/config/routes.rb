Rails.application.routes.draw do
  get 'home/index'
  post 'wallet/use'

  namespace 'admin' do
    resources :twitter_images
    get :twitter_image_preview, to: 'twitter_images#preview'
  end

  # devise_for :users
  # For details on the DSL available within this file, see http://guides.rubyonrails.org/routing.html
  root to: 'home#index'
end
