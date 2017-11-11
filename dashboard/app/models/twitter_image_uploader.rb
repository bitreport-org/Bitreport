require 'image_processing/mini_magick'

class TwitterImageUploader < Shrine
  include ImageProcessing::MiniMagick
  plugin :processing
  plugin :versions
  plugin :delete_raw
  plugin :delete_promoted

  process(:store) do |io|
    original = io.download

    thumbnail = resize_to_limit!(original, 300, 300)

    { original: io, thumbnail: thumbnail }
  end
end
