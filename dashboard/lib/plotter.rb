# frozen_string_literal: true

class Plotter
  attr_reader :timestamps, :candles, :patterns, :indicators, :levels, :step, :margin, :filename

  def initialize(timestamps, candles, patterns, indicators, levels)
    @timestamps = timestamps
    @candles = candles
    @patterns = patterns || {}
    @indicators = indicators || {}
    @levels = levels || {}
    @step = timestamps[1].to_i - timestamps[0].to_i
    @margin = (5 * (highs.max.to_f - lows.min.to_f) / 100)
    @filename = 'plot-' + SecureRandom.uuid + '.png'
    @plots = []
    @data = []
  end

  def plot(save = true)
    out = []
    out << terminal(save)
    out << preamble
    out << draw_levels
    prepare_volume
    prepare_bands_bg
    prepare_candles
    prepare_bands_fg
    prepare_sar
    prepare_sma
    prepare_ema
    prepare_tds
    prepare_patterns
    out << commands
    out << send((indicators.keys & %w[EWO MACD RSI STOCH]).first.downcase.to_sym)
    io = IO.popen('gnuplot -persist', 'w+')
    io << out.join("\n")
    io.close_write
    if save
      Rails.logger.info io.read
      self
    else
      io.read
    end
  end

  def output
    File.join(Rails.root, 'tmp', filename)
  end

  private

  def terminal(save)
    out = ['set terminal pngcairo truecolor font "Verdana,12" size 1280,720']
    out << (save ? "set output \"#{output}\"" : 'unset output')
    out
  end

  def preamble
    <<~GNU
      set lmargin at screen 0.05
      set rmargin at screen 0.95

      set xdata time
      set timefmt '%s'
      set format x ""

      set multiplot

      set key left

      set bmargin 0

      set size 1.0,0.7
      set origin 0.0,0.3

      set autoscale fix
      set offsets #{- step / 2},#{(0.5 + 10 * timestamps.length / 100) * step},#{margin},#{margin}

      set palette defined (-1 '#db2828', 0 '#ffc700', 1 '#21ba45')
      set cbrange [-1:1]
      unset colorbox

      set style fill solid border
      set boxwidth #{0.5 * step}
      set grid xtics ytics

      set y2range [0:#{5 * volumes.max}]
    GNU
  end

  def draw_levels
    return unless levels['support'] || levels['resistance']
    out = []
    [levels['support'], levels['resistance']].flatten.each_with_index do |level, i|
      out << <<~TXT
        set arrow #{i + 1} from #{timestamps.first},#{level} to #{timestamps.last + (1 + 10 * timestamps.length / 100) * step},#{level} nohead lc rgb "#66eab631" lw 2
      TXT
    end
    out
  end

  def prepare_volume
    @plots << "using 1:4:(#{0.95 * step}):($3 < $2 ? -1 : 1) axes x1y2 notitle with boxes palette fs transparent solid 0.15 noborder"
    @data << timestamps.zip(opens, closes, volumes).map { |candle| candle.join(' ') }.push('e')
  end

  def prepare_bands_bg
    if indicators['BB']
      @plots << 'using 1:2:4 title "Bollinger Bands" with filledcurves linecolor "#cc8fb6d8"' <<
                'using 1:2 notitle with lines linecolor "#663189d6" lw 1.5' <<
                'using 1:4 notitle with lines linecolor "#663189d6" lw 1.5'
      @data << timestamps.zip(indicators['BB']['upperband'], indicators['BB']['middleband'], indicators['BB']['lowerband']).map { |candle| candle.join(' ') }.push('e') * 3
    end
    if indicators['KC']
      @plots << 'using 1:2:4 title "Keltner Channel" with filledcurves linecolor "#ccffd728"' <<
        'using 1:2 notitle with lines linecolor "#66f9bb0e" lw 1.5' <<
        'using 1:4 notitle with lines linecolor "#66f9bb0e" lw 1.5'
      @data << timestamps.zip(indicators['KC']['upperband'], indicators['KC']['middleband'], indicators['KC']['lowerband']).map { |candle| candle.join(' ') }.push('e') * 3
    end
  end

  def prepare_candles
    @plots << 'using 1:2:3:4:5:($5 < $2 ? -1 : 1) notitle with candlesticks palette'
    @data << timestamps.zip(opens, lows, highs, closes).map { |candle| candle.join(' ') }.push('e')
  end

  def prepare_bands_fg
    if indicators['BB']
      @plots << 'using 1:3 notitle with lines linecolor "#663189d6" lw 1.5'
      @data << timestamps.zip(indicators['BB']['upperband'], indicators['BB']['middleband'], indicators['BB']['lowerband']).map { |candle| candle.join(' ') }.push('e')
    end
    if indicators['KELTNER']
      @plots << 'using 1:3 notitle with lines linecolor "#66f9bb0e" lw 1.5'
      @data << timestamps.zip(indicators['KELTNER']['upperband'], indicators['KELTNER']['middleband'], indicators['KELTNER']['lowerband']).map { |candle| candle.join(' ') }.push('e')
    end
  end

  def prepare_sar
    return unless indicators['SAR']
    @plots << 'using 1:2 title "SAR" with points lt 6 ps 0.3'
    @data << timestamps.zip(indicators['SAR']['sar']).map { |candle| candle.join(' ') }.push('e')
  end

  def prepare_sma
    return unless indicators['SMA']
    @plots << 'using 1:2 title "SMA slow" with lines lw 1.5' <<
              'using 1:3 title "SMA medium" with lines lw 1.5' <<
              'using 1:4 title "SMA fast" with lines lw 1.5'
    @data << timestamps.zip(indicators['SMA']['slow'], indicators['SMA']['medium'], indicators['SMA']['fast']).map { |candle| candle.join(' ') }.push('e') * 3
  end

  def prepare_ema
    return unless indicators['EMA']
    @plots << 'using 1:2 title "EMA slow" with lines lw 1.5' <<
              'using 1:3 title "EMA medium" with lines lw 1.5' <<
              'using 1:4 title "EMA slow" with lines lw 1.5'
    @data << timestamps.zip(indicators['EMA']['slow'], indicators['EMA']['medium'], indicators['EMA']['fast']).map { |candle| candle.join(' ') }.push('e') * 3
  end

  def prepare_tds
    return unless indicators['TDS']
    # 💩💩💩
    tdsvals = { 'pbuy' => -1, 'buy' => 0, 'sell' => 0, 'psell' => 1 }
    vals = indicators['TDS']['tds'].map { |v| tdsvals[v] }
    prices = indicators['TDS']['tds'].each_with_index.map do |v, i|
      v.include?('buy') ? lows[i] - @margin/2 : highs[i] + @margin/2
    end
    @plots << 'using 1:2:3 title "TD Sequential" with points pt 6 palette' <<
              'using 1:2:3 notitle with points pt 7 palette'
    @data << timestamps.zip(prices, vals).map { |candle| candle.join(' ') }.push('e')
    counts = [1]
    (1..indicators['TDS']['tds'].count).each do |i|
      counts << ((indicators['TDS']['tds'][i] == indicators['TDS']['tds'][i - 1] || (indicators['TDS']['tds'][i] == 'buy' && indicators['TDS']['tds'][i - 1] == 'pbuy') || (indicators['TDS']['tds'][i] == 'pbuy' && indicators['TDS']['tds'] == 'buy') || (indicators['TDS']['tds'][i] == 'sell' && indicators['TDS']['tds'][i - 1] == 'psell') || (indicators['TDS']['tds'][i] == 'psell' && indicators['TDS']['tds'][i - 1] == 'sell')) ? counts.last + 1 : 1)
    end
    @data << timestamps.zip(prices, vals, counts).select { |el| el[3] >= 9 }.map { |candle| candle[0..2].join(' ') }.push('e')
  end

  def prepare_patterns
    return unless patterns.any?
    @plots << 'using 1:2 notitle with points lc "#000000" ps 1.5' <<
              'using 1:2 notitle with points lc "#000000" ps 1.5'
    @data << patterns.first[1]['up'].map { |t| "#{t} #{highs[timestamps.index(t) || 0]}" }.push('e') <<
             patterns.first[1]['down'].map { |t| "#{t} #{lows[timestamps.index(t) || 0]}" }.push('e')
  end

  def commands
    "plot '-' " + @plots.join(",\\\n'-' ") + "\n" + @data.join("\n")
  end

  def ewo
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set bmargin 0
      set tmargin 0

      set offsets 0,#{(1 + 10 * timestamps.length / 100) * step},10,10

      plot '-' using 1:2:($2 < 0 ? -1 : 1) notitle with impulses palette
    GNU
    out << timestamps.zip(indicators['EWO']['ewo']).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def macd
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%d-%m-%y\\n%H:%M"

      set tmargin 0

      set offsets 0,#{(1 + 10 * timestamps.length / 100) * step},10,10

      plot '-' using 1:2 notitle with impulses linecolor "#f455c7", \\
           '-' using 1:3 notitle with lines linecolor "#ff9b38", \\
           '-' using 1:4 notitle with lines linecolor "#2e99f7"
    GNU
    out << timestamps.zip(indicators['MACD']['hist'], indicators['MACD']['signal'], indicators['MACD']['macd']).map { |candle| candle.join(' ') }.push('e') * 3
    out
  end

  def rsi
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%d-%m-%y\\n%H:%M"

      set tmargin 0

      set offsets 0,#{(1 + 10 * timestamps.length / 100) * step},10,10
      set object 1 rect from #{timestamps.first},20 to #{timestamps.last + (1 + 10 * timestamps.length / 100) * step},80 fc rgb "#dd9526c1" fs solid noborder
      set arrow 1 from #{timestamps.first},20 to #{timestamps.last + (1 + 10 * timestamps.length / 100) * step},20 nohead lc rgb "#669526c1" lw 1.5 dt 2
      set arrow 2 from #{timestamps.first},80 to #{timestamps.last + (1 + 10 * timestamps.length / 100) * step},80 nohead lc rgb "#669526c1" lw 1.5 dt 2

      set yrange [0:100]

      plot '-' using 1:2 notitle with lines linecolor "#9526c1"
    GNU
    out << timestamps.zip(indicators['RSI']['rsi']).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def stoch
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%d-%m-%y\\n%H:%M"

      set tmargin 0

      set offsets 0,#{(1 + 10 * timestamps.length / 100) * step},10,10
      set object 1 rect from #{timestamps.first},20 to #{timestamps.last + (1 + 10 * timestamps.length / 100) * step},80 fc rgb "#dd9526c1" fs solid noborder
      set arrow 1 from #{timestamps.first},20 to #{timestamps.last + (1 + 10 * timestamps.length / 100) * step},20 nohead lc rgb "#669526c1" lw 1.5 dt 2
      set arrow 2 from #{timestamps.first},80 to #{timestamps.last + (1 + 10 * timestamps.length / 100) * step},80 nohead lc rgb "#669526c1" lw 1.5 dt 2

      set yrange [0:100]

      plot '-' using 1:2 notitle with lines linecolor "#4286f4", \\
           '-' using 1:3 notitle with lines linecolor "#f4a641"
    GNU
    out << timestamps.zip(indicators['STOCH']['slowk'], indicators['STOCH']['slowd']).map { |candle| candle.join(' ') }.push('e') * 2
    out
  end

  def opens
    candles['open']
  end

  def closes
    candles['close']
  end

  def highs
    candles['high']
  end

  def lows
    candles['low']
  end

  def volumes
    candles['volume']
  end
end
