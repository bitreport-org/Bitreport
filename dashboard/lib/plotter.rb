# frozen_string_literal: true

class Plotter
  attr_reader :timestamps, :candles, :patterns, :indicators, :step, :margin, :filename

  def initialize(timestamps, candles, patterns, indicators)
    @timestamps = timestamps
    @candles = candles
    @patterns = patterns || {}
    @indicators = indicators || {}
    @step = timestamps[1].to_i - timestamps[0].to_i
    @margin = (5 * (highs.max.to_f - lows.min.to_f) / 100)
    @filename = SecureRandom.uuid + '.png'
  end

  def plot
    out = []
    out << <<~TXT
      set terminal png truecolor font Verdana 9 size 1280,720
      set output "#{output}"

      set lmargin at screen 0.05
      set rmargin at screen 0.95

      set xdata time
      set timefmt '%s'
      set format x ""

      set multiplot

      set bmargin 0

      set size 1.0,0.7
      set origin 0.0,0.3

      set autoscale fix
      set offsets #{- step / 2},#{(0.5 + 10 * timestamps.length / 100) * step},#{margin},#{margin}

      set palette defined (-1 '#db2828', 1 '#21ba45')
      set cbrange [-1:1]
      unset colorbox

      set style fill transparent solid 0.3 border
      set boxwidth #{0.5 * step}
      set grid xtics ytics

      set y2range [0:#{5 * volumes.max}]

      plot '-' using 1:4:(#{0.95 * step}):($3 < $2 ? -1 : 1) axes x1y2 notitle with boxes palette, \\
           '-' using 1:2:4 notitle with filledcurves linecolor "#8fb6d8", \\
           '-' using 1:2 notitle with lines linecolor "#3189d6", \\
           '-' using 1:4 notitle with lines linecolor "#3189d6", \\
           '-' using 1:2:3:4:5:($5 < $2 ? -1 : 1) notitle with candlesticks palette fs solid 1.0, \\
           '-' using 1:3 notitle with lines linecolor "#3189d6"
    TXT
    out << timestamps.zip(opens, closes, volumes).map { |candle| candle.join(' ') }.push('e')
    out << timestamps.zip(indicators['BB']['upperband'], indicators['BB']['middleband'], indicators['BB']['lowerband']).map { |candle| candle.join(' ') }.push('e') * 3
    out << timestamps.zip(opens, lows, highs, closes).map { |candle| candle.join(' ') }.push('e')
    out << timestamps.zip(indicators['BB']['upperband'], indicators['BB']['middleband'], indicators['BB']['lowerband']).map { |candle| candle.join(' ') }.push('e')
    # out << ewo
    # out << macd
    out << rsi
    io = IO::popen('gnuplot -persist', 'w+')
    io << out.join("\n")
    io.close_write
    puts io.read
    # puts out.join("\n")
    self
  end

  def output
    File.join(Rails.root, 'public', 'uploads', filename)
  end

  private

  def ewo
    out = []
    out << <<~TXT
      set size 1.0,0.25
      set origin 0.0,0.05

      set bmargin 0
      set tmargin 0

      set offsets 0,#{(1 + 10 * timestamps.length / 100) * step},10,10

      plot '-' using 1:2:($2 < 0 ? -1 : 1) notitle with impulses palette
    TXT
    out << timestamps.zip(indicators['EWO']['ewo']).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def macd
    out = []
    out << <<~TXT
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%d-%m-%y\\n%H:%M"

      set tmargin 0

      set offsets 0,#{(1 + 10 * timestamps.length / 100) * step},10,10

      plot '-' using 1:2 notitle with impulses linecolor "#f455c7", \\
           '-' using 1:3 notitle with lines linecolor "#ff9b38", \\
           '-' using 1:4 notitle with lines linecolor "#2e99f7"
    TXT
    out << timestamps.zip(indicators['MACD']['hist'], indicators['MACD']['signal'], indicators['MACD']['macd']).map { |candle| candle.join(' ') }.push('e') * 3
    out
  end

  def rsi
    out = []
    out << <<~TXT
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%d-%m-%y\\n%H:%M"

      set tmargin 0

      set offsets 0,#{(1 + 10 * timestamps.length / 100) * step},10,10
      set arrow 1 from #{timestamps.first},20 to #{timestamps.last + (1 + 10 * timestamps.length / 100) * step},20 nohead lc rgb "#669526c1" lw 1.5
      set arrow 2 from #{timestamps.first},80 to #{timestamps.last + (1 + 10 * timestamps.length / 100) * step},80 nohead lc rgb "#669526c1" lw 1.5

      set yrange [0:100]

      plot '-' using 1:2 notitle with lines linecolor "#9526c1"
    TXT
    out << timestamps.zip(indicators['RSI']['rsi']).map { |candle| candle.join(' ') }.push('e')
    out
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
