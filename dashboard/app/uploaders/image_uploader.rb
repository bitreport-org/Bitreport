# frozen_string_literal: true

require 'image_processing/vips'

class ImageUploader < Shrine
  plugin :pretty_location, namespace: '/'
  plugin :moving
  plugin :processing
  plugin :versions
  plugin :delete_raw
  plugin :delete_promoted
  plugin :determine_mime_type

  process(:store) do |io|
    original = io.download

    thumbnail = ImageProcessing::Vips.source(original).resize_to_limit!(300, 300)

    { original: io, thumbnail: thumbnail }
  end
end
