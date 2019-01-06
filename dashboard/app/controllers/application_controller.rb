# frozen_string_literal: true

class ApplicationController < ActionController::Base
  before_action :set_raven_context, if: -> { defined?(Raven) }
  protect_from_forgery with: :exception

  private

  def set_raven_context
    Raven.extra_context(params: params.to_unsafe_h, url: request.url)
  end
end
