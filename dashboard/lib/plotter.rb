# frozen_string_literal: true

class Plotter
  attr_reader :timestamps, :candles, :patterns, :indicators, :levels, :step, :margin, :filename

  WHITE = 'e6e6e6'
  BLACK = '383834'
  YELLOW = 'f6d60e'
  BLUE = '5bc0eb'
  GREEN = 'b0db43'
  RED = 'db504a'
  PURPLE = 'f455c7'

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
    prepare_ichimoku_bg
    prepare_candles
    prepare_bands_fg
    prepare_ichimoku_fg
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
    out = ["set terminal pngcairo truecolor font 'Verdana,12' size 1280,720 background rgb '##{BLACK}'"]
    out << (save ? "set output '#{output}'" : 'unset output')
    out
  end

  def preamble
    <<~GNU
      set lmargin at screen 0.05
      set rmargin at screen 0.99

      set xdata time
      set timefmt '%s'
      set format x ""

      set multiplot

      set key left

      set bmargin 0

      set size 1.0,0.7
      set origin 0.0,0.3

      set autoscale fix
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [#{lows.min - margin}:#{highs.max + margin}]

      set palette defined (-1 '##{RED}', 0 '##{YELLOW}', 1 '##{GREEN}')
      set cbrange [-1:1]
      unset colorbox

      set style fill solid border
      set boxwidth #{0.5 * step}
      set grid xtics ytics lc rgb '##{WHITE}'

      set border lc rgb '##{WHITE}'
      set xtics textcolor rgb '##{WHITE}'
      set ytics textcolor rgb '##{WHITE}'
      set key textcolor rgb '##{WHITE}'

      set y2range [0:#{5 * volumes.max}]
    GNU
  end

  def draw_levels
    return unless levels['support'] || levels['resistance']
    out = []
    [levels['support'], levels['resistance']].flatten.each_with_index do |level, i|
      next unless (lows.min..highs.max).cover?(level)
      out << <<~TXT
        set arrow #{i + 1} from #{timestamps.first},#{level} to #{timestamps.last},#{level} nohead lc rgb "#33#{YELLOW}" lw 2
      TXT
    end
    out
  end

  def prepare_volume
    @plots << "using 1:4:(#{0.95 * step}):($3 < $2 ? -1 : 1) axes x1y2 notitle with boxes palette fs transparent solid 0.1 noborder"
    @data << timestamps.zip(opens, closes, volumes).map { |candle| candle.join(' ') }.push('e')
  end

  def prepare_bands_bg
    if indicators['BB']
      @plots << "using 1:2:4 notitle with filledcurves linecolor '#f2#{BLUE}'" <<
                "using 1:2 notitle with lines linecolor '#66#{BLUE}' lw 1.5" <<
                "using 1:4 notitle with lines linecolor '#66#{BLUE}' lw 1.5"
      @data << timestamps.zip(indicators['BB']['upperband'], indicators['BB']['middleband'], indicators['BB']['lowerband']).map { |candle| candle.join(' ') }.push('e') * 3
    end
    if indicators['KC']
      @plots << "using 1:2:4 notitle with filledcurves linecolor '#f4#{YELLOW}'" <<
                "using 1:2 notitle with lines linecolor '#40#{YELLOW}' lw 1.5" <<
                "using 1:4 notitle with lines linecolor '#40#{YELLOW}' lw 1.5"
      @data << timestamps.zip(indicators['KC']['upperband'], indicators['KC']['middleband'], indicators['KC']['lowerband']).map { |candle| candle.join(' ') }.push('e') * 3
    end
  end

  def prepare_ichimoku_bg
    return unless indicators['ICM']
    @plots << "using 1:2:3 notitle with filledcurves above linecolor '#dd#{GREEN}'" <<
              "using 1:2:3 notitle with filledcurves below linecolor '#dd#{RED}'" <<
              "using 1:2 notitle with lines linecolor '#88#{GREEN}' lw 1.5" <<
              "using 1:3 notitle with lines linecolor '#88#{RED}' lw 1.5"
    @data << timestamps.zip(indicators['ICM']['leading span A'], indicators['ICM']['leading span B']).map { |candle| candle.join(' ') }.push('e') * 4
  end

  def prepare_candles
    @plots << 'using 1:2:3:4:5:($5 < $2 ? -1 : 1) notitle with candlesticks palette lw 1.5'
    @data << timestamps.zip(opens, lows, highs, closes).map { |candle| candle.join(' ') }.push('e')
  end

  def prepare_bands_fg
    if indicators['BB']
      @plots << "using 1:3 title 'Bollinger Bands' with lines linecolor '#66#{BLUE}' lw 1.5"
      @data << timestamps.zip(indicators['BB']['upperband'], indicators['BB']['middleband'], indicators['BB']['lowerband']).map { |candle| candle.join(' ') }.push('e')
    end
    if indicators['KC']
      @plots << "using 1:3 title 'Keltner Channel' with lines linecolor '#40#{YELLOW}' lw 1.5"
      @data << timestamps.zip(indicators['KC']['upperband'], indicators['KC']['middleband'], indicators['KC']['lowerband']).map { |candle| candle.join(' ') }.push('e')
    end
  end

  def prepare_ichimoku_fg
    return unless indicators['ICM']
    @plots << "using 1:2 title 'Tenkan-sen' with lines linecolor '##{BLUE}' lw 1.5" <<
              "using 1:3 title 'Kijun-sen' with lines linecolor '##{YELLOW}' lw 1.5" <<
              "using 1:4 title 'Chikou' with lines linecolor '#40#{GREEN}' lw 1.5"
    @data << timestamps.zip(indicators['ICM']['conversion line'], indicators['ICM']['base line'], indicators['ICM']['lagging span']).map { |candle| candle.join(' ') }.push('e') * 3
  end

  def prepare_sar
    return unless indicators['SAR']
    @plots << "using 1:2 title 'SAR' with points lt 6 ps 0.3 lc '##{BLUE}'"
    @data << timestamps.zip(indicators['SAR']['sar']).map { |candle| candle.join(' ') }.push('e')
  end

  def prepare_sma
    #TODO: Set colors
    return unless indicators['SMA']
    @plots << "using 1:2 title 'SMA slow' with lines lw 1.5 lc '#c0#{YELLOW}'" <<
              "using 1:3 title 'SMA medium' with lines lw 1.5 lc '#70#{YELLOW}'" <<
              "using 1:4 title 'SMA fast' with lines lw 1.5 lc '#00#{YELLOW}'"
    @data << timestamps.zip(indicators['SMA']['slow'], indicators['SMA']['medium'], indicators['SMA']['fast']).map { |candle| candle.join(' ') }.push('e') * 3
  end

  def prepare_ema
    #TODO: Set colors
    return unless indicators['EMA']
    @plots << "using 1:2 title 'EMA slow' with lines lw 1.5 lc '#c0#{BLUE}'" <<
              "using 1:3 title 'EMA medium' with lines lw 1.5 lc '#70#{BLUE}'" <<
              "using 1:4 title 'EMA fast' with lines lw 1.5 lc '#00#{BLUE}'"
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
    @data << timestamps.zip(prices, vals, counts).select { |el| el[1] && el[3] >= 9 }.map { |candle| candle[0..2].join(' ') }.push('e')
  end

  def prepare_patterns
    return unless patterns.any?
    @plots << "using 1:2 notitle with points lc '##{WHITE}' ps 1.5" <<
              "using 1:2 notitle with points lc '##{WHITE}' ps 1.5"
    @data << patterns.first[1]['up'].map { |t| "#{t} #{highs[timestamps.index(t) || 0]}" }.push('e') <<
             patterns.first[1]['down'].map { |t| "#{t} #{lows[timestamps.index(t) || 0]}" }.push('e')
  end

  def commands
    "plot '-' " + @plots.join(",\\\n'-' ") + "\n" + @data.join("\n")
  end

  def ewo
    margin = 10 * (indicators['EWO']['ewo'].max - indicators['EWO']['ewo'].min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%d-%m-%y\\n%H:%M"

      set bmargin 1
      set tmargin 0

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [*:*]

      plot '-' using 1:2:($2 < 0 ? -1 : 1) notitle with impulses palette lw 1.5
    GNU
    out << timestamps.zip(indicators['EWO']['ewo']).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def macd
    data = [indicators['MACD']['hist'], indicators['MACD']['signal'], indicators['MACD']['macd']].flatten
    margin = 10 * (data.max - data.min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%d-%m-%y\\n%H:%M"

      set bmargin 1
      set tmargin 0

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [*:*]

      plot '-' using 1:2 notitle with impulses lc '##{PURPLE}' lw 1.5, \\
           '-' using 1:3 notitle with lines lc '##{YELLOW}' lw 1.5, \\
           '-' using 1:4 notitle with lines lc '##{BLUE}' lw 1.5
    GNU
    out << timestamps.zip(indicators['MACD']['hist'], indicators['MACD']['signal'], indicators['MACD']['macd']).map { |candle| candle.join(' ') }.push('e') * 3
    out
  end

  def rsi
    margin = 10 * (indicators['RSI']['rsi'].max - indicators['RSI']['rsi'].min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%d-%m-%y\\n%H:%M"

      set bmargin 1
      set tmargin 0

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [0:100]

      set object 1 rect from #{timestamps.first},20 to #{timestamps.last},80 fc rgb '#ee#{PURPLE}' fs solid noborder
      set arrow 1 from #{timestamps.first},20 to #{timestamps.last},20 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2
      set arrow 2 from #{timestamps.first},80 to #{timestamps.last},80 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2

      plot '-' using 1:2 notitle with lines lc '##{PURPLE}' lw 1.5
    GNU
    out << timestamps.zip(indicators['RSI']['rsi']).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def stoch
    data = [indicators['STOCH']['slowk'], indicators['STOCH']['slowd']].flatten
    margin = 10 * (data.max - data.min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%d-%m-%y\\n%H:%M"

      set bmargin 1
      set tmargin 0

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [0:100]

      set object 1 rect from #{timestamps.first},20 to #{timestamps.last},80 fc rgb '#ee#{PURPLE}' fs solid noborder
      set arrow 1 from #{timestamps.first},20 to #{timestamps.last},20 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2
      set arrow 2 from #{timestamps.first},80 to #{timestamps.last},80 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2

      plot '-' using 1:2 notitle with lines linecolor '##{BLUE}' lw 1.5, \\
           '-' using 1:3 notitle with lines linecolor '##{YELLOW}' lw 1.5
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
