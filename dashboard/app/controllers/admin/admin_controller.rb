# frozen_string_literal: true

module Admin
  class AdminController < ApplicationController
    http_basic_authenticate_with name: 'admin', password: 'password'

    layout 'admin'
  end
end
