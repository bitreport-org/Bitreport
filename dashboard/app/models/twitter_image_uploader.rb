require 'image_processing/mini_magick'

class TwitterImageUploader < Shrine
  plugin :pretty_location, namespace: '/'
  plugin :moving
  plugin :processing
  plugin :versions
  plugin :delete_raw
  plugin :delete_promoted

  process(:store) do |io|
    original = io.download

    thumbnail = ImageProcessing::MiniMagick.source(original).resize_to_limit!(300, 300)

    { original: io, thumbnail: thumbnail }
  end
end
