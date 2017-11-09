class TwitterImage < ApplicationRecord
  include ImageUploader[:image]
end
