# frozen_string_literal: true

class Plotter
  attr_reader :candles, :patterns, :indicators, :filename

  def initialize(candles, patterns, indicators)
    @candles = candles
    @patterns = patterns || {}
    @indicators = indicators || {}
    @filename = SecureRandom.uuid + '.png'
  end

  def plot
    step = timestamps[0].to_i - timestamps[1].to_i
    margin = (5 * (highs.max.to_f - lows.min.to_f) / 100)
    # io = IO::popen('gnuplot -persist', 'w+')
    # io << <<~TXT
    #   set terminal png truecolor font Verdana 9 size 1280,720 enhanced
    #   set output "#{output}"
    #
    #   set xdata time
    #   set timefmt '%s'
    #   set format x '%d-%m-%y %H:%M'
    #   set autoscale fix
    #   set offsets #{step / 2},#{(0.5 + 10 * timestamps.length / 100) * step},#{margin},#{margin}
    #
    #   set palette defined (-1 '#db2828', 1 '#21ba45')
    #   set cbrange [-1:1]
    #   unset colorbox
    #
    #   set style fill transparent solid 0.3 border
    #   set boxwidth #{0.5 * step}
    #   set grid xtics ytics
    #
    #   set y2range [0:#{5 * volumes.max}]
    #
    #   plot '-' using 1:4:(#{0.95 * step}):($3 < $2 ? -1 : 1) axes x1y2 notitle with boxes palette
    # TXT
    # timestamps.zip(opens, closes, volumes).each do |candle|
    #   io << "#{candle[0]} #{candle[1]} #{candle[2]} #{candle[3]}\n"
    # end
    # io << "e\n"
    # if indicators['BB']
    #   io << "plot \"-\" using 1:2:3 notitle with filledcu linecolor \"#8fb6d8\"\n"
    #   timestamps.zip(indicators['BB']['upperband'], indicators['BB']['lowerband']).each do |candle|
    #     io << "#{candle[0]} #{candle[1]} #{candle[2]}\n"
    #   end
    #   io << "e\n"
    # end
    # io.close_write
    # puts io.read
    Gnuplot.open do |gp|
      Gnuplot::Plot.new(gp) do |plot|
        if indicators['BB']
          plot.data << Gnuplot::DataSet.new([timestamps, indicators['BB']['upperband'], indicators['BB']['lowerband']]) do |ds|
            ds.using = '1:2:3'
            ds.title = 'notitle'
            ds.with = 'filledcu'
            ds.linecolor = '"#8fb6d8"'
          end
          plot.data << Gnuplot::DataSet.new([timestamps, indicators['BB']['upperband']]) do |ds|
            ds.using = '1:2'
            ds.title = 'notitle'
            ds.with = 'lines'
            ds.linecolor = '"#8fb6d8"'
          end
          plot.data << Gnuplot::DataSet.new([timestamps, indicators['BB']['lowerband']]) do |ds|
            ds.using = '1:2'
            ds.title = 'notitle'
            ds.with = 'lines'
            ds.linecolor = '"#8fb6d8"'
          end
        end

        plot.data << Gnuplot::DataSet.new([timestamps, opens, lows, highs, closes]) do |ds|
          ds.using = '1:2:3:4:5:($5 < $2 ? -1 : 1)'
          ds.title = 'notitle'
          ds.with = 'candlesticks palette fs solid 1.0'
        end

        if indicators['BB']
          plot.data << Gnuplot::DataSet.new([timestamps, indicators['BB']['middleband']]) do |ds|
            ds.using = '1:2'
            ds.title = 'notitle'
            ds.with = 'line'
            ds.linecolor = '"#3189d6"'
          end
        end
      end

      Gnuplot::Plot.new(gp) do |plot|
        plot.size '1.0,0.3'
        plot.origin '0.0,0.0'
        plot.xdata 'time'
        plot.timefmt '"%s"'
        plot.format 'x "%d-%m-%y\n%H:%M"'
        plot.autoscale 'fix'
        plot.offsets "#{step}, #{(1 + 10 * timestamps.length / 100) * step}, #{margin}, #{margin}"

        plot.grid 'xtics ytics'

        if indicators['MACD'] #date, signal, hist, macd
          plot.data << Gnuplot::DataSet.new([timestamps, indicators['MACD']['hist']]) do |ds|
            ds.using = "1:2"
            ds.title = 'notitle'
            ds.with = 'impulses'
          end
          plot.data << Gnuplot::DataSet.new([timestamps, indicators['MACD']['signal']]) do |ds|
            ds.using = "1:2"
            ds.title = 'notitle'
            ds.with = 'lines'
          end
          plot.data << Gnuplot::DataSet.new([timestamps, indicators['MACD']['macd']]) do |ds|
            ds.using = "1:2"
            ds.title = 'notitle'
            ds.with = 'lines'
          end
        end
      end
    end
    self
  end

  def output
    File.join(Rails.root, 'public', 'uploads', filename)
  end

  private

  def timestamps
    candles[:timestamps]
  end

  def opens
    candles[:opens]
  end

  def closes
    candles[:closes]
  end

  def highs
    candles[:highs]
  end

  def lows
    candles[:lows]
  end

  def volumes
    candles[:volumes]
  end
end
