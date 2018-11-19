# frozen_string_literal: true

Config.setup do |config|
  config.const_name = 'Settings'
  config.use_env = true

  # config.schema do
  #   required(:name).filled
  #   required(:age).maybe(:int?)
  #   required(:email).filled(format?: EMAIL_REGEX)
  # end
end
