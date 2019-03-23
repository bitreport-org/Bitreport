# frozen_string_literal: true

module Admin
  class AdminController < ApplicationController
    http_basic_authenticate_with name: Settings.admin_panel.login,
                                 password: Settings.admin_panel.password

    layout 'admin'
  end
end
