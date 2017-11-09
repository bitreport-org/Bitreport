# frozen_string_literal: true

class Plotter
  attr_reader :timestamps, :opens, :lows, :highs, :closes, :filename

  def initialize(timestamps, opens, lows, highs, closes)
    @timestamps = timestamps
    @opens = opens
    @lows = lows
    @highs = highs
    @closes = closes
    @filename = SecureRandom.uuid + '.png'
  end

  def plot
    step = timestamps[0].to_i - timestamps[1].to_i
    margin = (5 * (highs.max.to_f - lows.min.to_f) / 100)
    Gnuplot.open do |gp|
      Gnuplot::Plot.new(gp) do |plot|
        plot.terminal 'png font Verdana 9 size 1280,720 enhanced'
        plot.output output

        plot.xdata 'time'
        plot.timefmt '"%s"'
        plot.format 'x "%d-%m-%y\n%H:%M"'
        plot.autoscale 'fix'
        plot.offsets "#{step / 2}, #{(0.5 + 10 * @timestamps.length / 100) * step}, #{margin}, #{margin}"

        plot.palette 'defined (-1 "#db2828", 1 "#21ba45")'
        plot.cbrange '[-1:1]'
        plot.unset 'colorbox'

        plot.style 'fill solid noborder'
        plot.boxwidth "#{0.5 * step}"
        plot.grid 'xtics ytics'

        plot.data << Gnuplot::DataSet.new([timestamps, opens, lows, highs, closes]) do |ds|
          ds.using = '1:2:3:4:5:($5 < $2 ? -1 : 1)'
          ds.title = 'notitle'
          ds.with = 'candlesticks palette'
        end
      end
    end
    self
  end

  def output
    File.join(Rails.root, 'public', 'uploads', filename)
  end
end
