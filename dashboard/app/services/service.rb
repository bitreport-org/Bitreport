# frozen_string_literal: true

class Service
  class ValidationError < StandardError; end

  include ActiveModel::Validations
  extend ActiveModel::Callbacks

  define_model_callbacks :validation, :execute

  def call
    run_callbacks(:validation) { validate! }
    run_callbacks(:execute) { run }
  rescue ActiveRecord::RecordInvalid => e
    raise ValidationError, e.message
  rescue ActiveModel::ValidationError => e
    raise ValidationError, e.message
  end

  private

  def run; end
end
