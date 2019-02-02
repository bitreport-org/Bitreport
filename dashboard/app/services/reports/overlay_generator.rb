# frozen_string_literal: true

require 'image_processing/vips'

module Reports
  class OverlayGenerator < Service
    validates :pair, :timeframe, :comment, presence: true

    def initialize(pair:, plot:, timeframe:, comment:)
      @pair = pair
      @timeframe = timeframe
      @plot = Vips::Image.new_from_buffer(plot, '', access: :sequential)
      @comment = comment
    end

    def run
      image = Tempfile.new(%w[plot .png], encoding: 'ascii-8bit')
      image.write(generate)
      image
    end

    private

    attr_reader :pair, :plot, :timeframe, :comment

    def generate
      image = Vips::Image.new_from_file(background, access: :sequential).insert(@plot, 0, 110)
      image = timestamp.ifthenelse([54, 54, 49], symbol.ifthenelse([238], image, blend: true), blend: true)
      image = description.ifthenelse([54, 54, 49], image, blend: true)
      image.write_to_buffer('.png')
    end

    def background
      @background ||= Rails.root.join('app', 'assets', 'images', 'template.png').to_s
    end

    def symbol
      symbol = Vips::Image.text("#{pair.symbol} #{timeframe}h", font: 'PT Sans Bold 56', align: :centre)
      symbol.embed(820 - symbol.width / 2, 80 - symbol.height, 2048, 1024)
    end

    def timestamp
      timestamp = Vips::Image.text(pair.last_updated_at.strftime('%Y-%m-%d %H:%M UTC'), font: 'PT Sans Bold 32', align: :centre)
      timestamp.embed(1810 - timestamp.width / 2, 200 - timestamp.height, 2048, 1024)
    end

    def description
      description = TextLayerGenerator.new(x_offset: 1610, y_offset: 200)
      description.add_header('Comment')
      description.add_text(comment.strip)
      description.image
    end
  end
end
