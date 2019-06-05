# frozen_string_literal: true

class HomeController < ApplicationController
  def show
    render params[:page]
  end
end
