require 'image_processing/vips'

class OverlayGenerator
  def initialize(twitter_image, plot_image)
    @twitter_image = twitter_image
    @plot_image = Vips::Image.new_from_file(plot_image, access: :sequential)
  end

  def generate
    img = Vips::Image.new_from_file(background, access: :sequential).insert(@plot_image, 0, 110)
    img = timestamp.ifthenelse([54, 54, 49], symbol.ifthenelse([238], img, blend: true), blend: true)
    img = comment.ifthenelse([54, 54, 49], img, blend: true) if @twitter_image.comment || @twitter_image.levels
    img.write_to_buffer('.png')
  end

  private

  def background
    @background ||= Rails.root.join('app', 'assets', 'images', 'template.png').to_s
  end

  def symbol
    symbol = Vips::Image.text("#{@twitter_image.symbol} #{@twitter_image.timeframe}", font: 'PT Sans Bold 56', align: :centre)
    symbol.embed(820 - symbol.width / 2, 80 - symbol.height, 2048, 1024)
  end

  def timestamp
    timestamp = Vips::Image.text(report_date.strftime("%Y-%m-%d %H:%M UTC"), font: 'PT Sans Bold 32', align: :centre)
    timestamp.embed(1810 - timestamp.width / 2, 200 - timestamp.height, 2048, 1024)
  end

  def comment
    offset = 200
    base = Vips::Image.black(2048, 1024)
    if @twitter_image.levels
      offset += 40
      levels_header = Vips::Image.text('Levels', font: 'PT Sans Bold 22')
      base = base.insert(levels_header, 1610, offset)
      offset += 40
      @twitter_image.levels.each do |value|
        type = Vips::Image.text(value.to_f > @twitter_image.price ? 'Resistance' : 'Support', font: 'PT Sans 22') # This is not right
        level = Vips::Image.text(value, font: 'PT Sans 22')
        base = base.insert(type, 1610, offset)
        base = base.insert(level, 1760, offset)
        offset += 40
      end
    end
    if @twitter_image.comment
      offset += 40
      comment_header = Vips::Image.text('Comment', font: 'PT Sans Bold 22')
      base = base.insert(comment_header, 1610, offset)
      offset += 40
      comment = Vips::Image.text(@twitter_image.comment.strip, font: 'PT Sans 22', align: :low, width: 410, spacing: 6)
      base = base.insert(comment, 1610, offset)
    end
    base
  end

  def report_date
    @twitter_image.created_at || Time.zone.now
  end
end