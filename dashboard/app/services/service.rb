# frozen_string_literal: true

class Service
  include ActiveModel::Validations
  extend ActiveModel::Callbacks

  define_model_callbacks :execute

  def call
    validate!
    run_callbacks :execute do
      ActiveRecord::Base.transaction { run }
    end
  end

  private

  def run; end
end
