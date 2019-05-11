# frozen_string_literal: true

require 'image_processing/vips'

module Reports
  class OverlayGenerator
    class TextLayerGenerator
      def initialize(x_offset:, y_offset:, font_size: 22)
        @base = Vips::Image.black(2048, 1024)
        @x_offset = x_offset
        @y_offset = y_offset
        @font_size = font_size
      end

      def image
        @base
      end

      def add_header(text)
        write(text, font: "PT Sans Bold #{@font_size}")
      end

      def add_line(text)
        write(text, font: "PT Sans #{@font_size}")
      end

      def add_text(text, float: :left)
        write(text, font: "PT Sans #{@font_size}", align: :low, width: 410, spacing: 6, float: float)
      end

      private

      def write(text, float: :left, **kwargs)
        @y_offset += 40
        layer = Vips::Image.text(text, **kwargs)
        x_offset = float == :left ? @x_offset : @x_offset - layer.width
        @base = @base.insert(layer, x_offset, @y_offset)
      end
    end
  end
end
