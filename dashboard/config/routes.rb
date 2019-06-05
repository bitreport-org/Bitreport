# frozen_string_literal: true

Rails.application.routes.draw do
  scope module: :admin, path: '/admin' do
    root to: 'pairs#index'
    resources :pairs, only: %i[index new edit create update destroy]
    resources :posts, only: %i[index]
    get 'preview', to: 'previews#show'
  end

  namespace :api, constraints: { ip: /127\.0\.0\.1/ } do
    resource :events, only: %i[create]
  end

  root to: 'home#show', page: :landing
end
