require 'image_processing/vips'

class OverlayGenerator
  def initialize(plot_image)
    @plot_image = plot_image
  end

  def generate
    Rails.logger.info "Rendering #{@plot_image} with text: #{text}"
    img = ImageProcessing::Vips.source(background)
              .composite(@plot_image, offset: [0, 110])
              .composite(text)
              .call
    Rails.logger.info img
    img
  end

  private

  def background
    @background ||= File.open(Rails.root.join('app', 'assets', 'images', 'template.png'))
  end

  def text
    @text ||= Vips::Image.text('Yolo Image Woah').write_to_file('/opt/project/tmp/text.png')
  end
end