require 'image_processing/vips'

class OverlayGenerator
  def initialize(plot_image)
    @plot_image = Vips::Image.new_from_file(plot_image, access: :sequential)
  end

  def generate
    Rails.logger.info "Rendering #{@plot_image} with text: #{text}"
    img = Vips::Image.new_from_file(background, access: :sequential)
              .insert(@plot_image, 0, 110)
    Rails.logger.info img
    text.ifthenelse([238], img, blend: true).write_to_buffer('.png')
  end

  private

  def background
    @background ||= Rails.root.join('app', 'assets', 'images', 'template.png').to_s
  end

  def text
    t = Vips::Image.text('Some symbol, something like BTCUSD', font: 'PT Sans Bold 56', align: :centre)
    t.embed(820 - t.width / 2, 80 - t.height, 2048, 1024)
  end
end