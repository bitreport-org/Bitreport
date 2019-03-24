# frozen_string_literal: true

require 'image_processing/vips'

module Reports
  class OverlayGenerator
    class TextLayerGenerator
      def initialize(x_offset:, y_offset:)
        @base = Vips::Image.black(2048, 1024)
        @x_offset = x_offset
        @y_offset = y_offset
      end

      def image
        @base
      end

      def add_header(text)
        write(text, font: 'PT Sans Bold 22')
      end

      def add_line(text)
        write(text, font: 'PT Sans 22')
      end

      def add_text(text)
        write(text, font: 'PT Sans 22', align: :low, width: 410, spacing: 6)
      end

      private

      def write(text, **kwargs)
        @y_offset += 40
        layer = Vips::Image.text(text, **kwargs)
        @base = @base.insert(layer, @x_offset, @y_offset)
      end
    end
  end
end
