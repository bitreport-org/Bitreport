# frozen_string_literal: true

class Plotter
  attr_reader :timestamps, :candles, :indicators, :levels, :step, :margin, :filename

  WHITE = 'e6e6e6'
  BLACK = '363631'
  YELLOW = 'f6d60e'
  BLUE = '5bc0eb'
  GREEN = 'b0db43'
  RED = 'db504a'
  PURPLE = 'f455c7'

  def initialize(timestamps, candles, indicators, levels)
    @timestamps = timestamps
    @candles = candles
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
    prepare_wedge_bg
    prepare_candles
    prepare_bands_fg
    prepare_ichimoku_fg
    prepare_wedge_fg
    prepare_sar
    prepare_sma
    prepare_ema
    prepare_lin
    prepare_tds
    out << commands
    out << send((indicators.keys & %w[EWO MACD RSI STOCH LINO OBV MOM STOCHRSI HTphasor HTmode HTsin CORRO]).first.downcase.to_sym)
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
    out = ["set terminal pngcairo truecolor font 'PT Sans,15' size 1570,890 background rgb '##{BLACK}'"]
    out << (save ? "set output '#{output}'" : 'unset output')
    out
  end

  def price_length
    m = [lows.min - margin, highs.max + margin]
    (Math.log10((m.max - m.min) / 10).round.abs + 3).clamp(6, 12)
  end

  def preamble
    <<~GNU
      set lmargin #{price_length + 1}
      set rmargin at screen 0.99

      set xdata time
      set timefmt '%s'
      set format x ""

      set multiplot

      set key center top outside horizontal Left reverse samplen 1

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
    return unless levels
    out = []
    levels.each_with_index do |level, i|
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
      @plots << "using 1:2:4 notitle with filledcurves linecolor '#f6#{YELLOW}'" <<
                "using 1:2 notitle with lines linecolor '#40#{YELLOW}' lw 1.5" <<
                "using 1:4 notitle with lines linecolor '#40#{YELLOW}' lw 1.5"
      @data << timestamps.zip(indicators['KC']['upperband'], indicators['KC']['middleband'], indicators['KC']['lowerband']).map { |candle| candle.join(' ') }.push('e') * 3
    end
    if indicators['parabola']
      name = 'parabola'
      @plots << "using 1:2:4 notitle with filledcurves linecolor '#f6#{RED}'" <<
                "using 1:2 notitle with lines linecolor '#40#{RED}' lw 1.5" <<
                "using 1:4 notitle with lines linecolor '#40#{RED}' lw 1.5"
      @data << timestamps.zip(indicators[name]['upperband'], indicators[name]['middleband'], indicators[name]['lowerband']).map { |candle| candle.join(' ') }.push('e') * 3
    end
    if indicators['channel']
      name = 'channel'
      @plots << "using 1:2:4 notitle with filledcurves linecolor '#f6#{YELLOW}'" <<
                "using 1:2 notitle with lines linecolor '#40#{YELLOW}' lw 1.5" <<
                "using 1:4 notitle with lines linecolor '#40#{YELLOW}' lw 1.5"
      @data << timestamps.zip(indicators[name]['upperband'], indicators[name]['middleband'], indicators[name]['lowerband']).map { |candle| candle.join(' ') }.push('e') * 3
    end
    if indicators['linear']
      name = 'linear'
      @plots << "using 1:2:4 notitle with filledcurves linecolor '#f6#{YELLOW}'" <<
                "using 1:2 notitle with lines linecolor '#40#{YELLOW}' lw 1.5" <<
                "using 1:4 notitle with lines linecolor '#40#{YELLOW}' lw 1.5"
      @data << timestamps.zip(indicators[name]['upperband'], indicators[name]['middleband'], indicators[name]['lowerband']).map { |candle| candle.join(' ') }.push('e') * 3
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

  def prepare_wedge_bg
    if indicators['wedge']
      @plots << "using 1:2:3 notitle with filledcurves linecolor '#f6#{YELLOW}'" <<
        "using 1:2 notitle with lines linecolor '#40#{YELLOW}' lw 1.5" <<
        "using 1:3 notitle with lines linecolor '#40#{YELLOW}' lw 1.5"
      @data << timestamps.zip(indicators['wedge']['upperband'], indicators['wedge']['lowerband']).map { |candle| candle.join(' ') }.push('e') * 3
    end
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
    if indicators['linear']
      name = 'linear'
      @plots << "using 1:3 title 'Linear Channel' with lines linecolor '#40#{YELLOW}' lw 1.5"
      @data << timestamps.zip(indicators[name]['upperband'], indicators[name]['middleband'], indicators[name]['lowerband']).map { |candle| candle.join(' ') }.push('e')
    end
    if indicators['channel']
      name = 'channel'
      @plots << "using 1:3 title 'Auto Channel' with lines linecolor '#40#{YELLOW}' lw 1.5"
      @data << timestamps.zip(indicators[name]['upperband'], indicators[name]['middleband'], indicators[name]['lowerband']).map { |candle| candle.join(' ') }.push('e')
    end
    if indicators['parabola']
      name = 'parabola'
      @plots << "using 1:3 title 'Parabolic Channel' with lines linecolor '#40#{RED}' lw 1.5"
      @data << timestamps.zip(indicators[name]['upperband'], indicators[name]['middleband'], indicators[name]['lowerband']).map { |candle| candle.join(' ') }.push('e')
    end
  end

  def prepare_ichimoku_fg
    return unless indicators['ICM']
    # @plots << "using 1:2 title 'Tenkan-sen' with lines linecolor '##{BLUE}' lw 1.5" <<
    #           "using 1:3 title 'Kijun-sen' with lines linecolor '##{YELLOW}' lw 1.5" <<
    #           "using 1:4 title 'Chikou' with lines linecolor '#40#{GREEN}' lw 1.5"
    # @data << timestamps.zip(indicators['ICM']['conversion line'], indicators['ICM']['base line'], indicators['ICM']['lagging span']).map { |candle| candle.join(' ') }.push('e') * 3
  end

  def prepare_wedge_fg
    if indicators['wedge']
      @plots << "using 1:3 title 'Wedge' with lines linecolor '#40#{YELLOW}' lw 1.5"
      @data << timestamps.zip(indicators['wedge']['upperband'], indicators['wedge']['middleband'], indicators['wedge']['lowerband']).map { |candle| candle.join(' ') }.push('e')
    end
  end

  def prepare_sar
    return unless indicators['SAR']
    @plots << "using 1:2 title 'SAR' with points lt 6 ps 0.3 lc '##{BLUE}'"
    @data << timestamps.zip(indicators['SAR']['sar']).map { |candle| candle.join(' ') }.push('e')
  end

  def prepare_lin
    #TODO: Set colors
    return unless indicators['LIN']
    @plots << "using 1:2 title 'Linear' with lines lw 1.5 lc '#00#{YELLOW}'"
    @data << timestamps.zip(indicators['LIN']['lin']).map { |candle| candle.join(' ') }.push('e')
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

  def commands
    "plot '-' " + @plots.join(",\\\n'-' ") + "\n" + @data.join("\n")
  end

  def ewo
    margin = 10 * (indicators['EWO']['ewo'].max - indicators['EWO']['ewo'].min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%Y-%m-%d\\n%H:%M"
      set ytics("0" 0)

      set bmargin 1
      set tmargin 0

      set label 'EWO' at graph 0.5, graph 0.51 center font ',46' front textcolor '#e6#{WHITE}'

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

      set format x "%Y-%m-%d\\n%H:%M"
      set ytics("0" 0)

      set bmargin 1
      set tmargin 0

      set label 'MACD' at graph 0.5, graph 0.51 center font ',46' front textcolor '#e6#{WHITE}'

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

  def htphasor
    data = [indicators['HTphasor']['inphase'], indicators['HTphasor']['quadrature']].flatten
    margin = 10 * (data.max - data.min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%Y-%m-%d\\n%H:%M"

      set bmargin 1
      set tmargin 0

      set label 'HTPHASOR' at graph 0.5, graph 0.51 center font ',46' front textcolor '#e6#{WHITE}'

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [*:*]

      plot '-' using 1:2 notitle with lines lc '##{YELLOW}' lw 1.5, \\
           '-' using 1:3 notitle with lines lc '##{BLUE}' lw 1.5
    GNU
    out << timestamps.zip(indicators['HTphasor']['inphase'], indicators['HTphasor']['quadrature']).map { |candle| candle.join(' ') }.push('e') * 2
    out
  end

  def htsin
    data = [indicators['HTsin']['sine'], indicators['HTsin']['leadsine']].flatten
    margin = 10 * (data.max - data.min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%Y-%m-%d\\n%H:%M"

      set bmargin 1
      set tmargin 0

      set label 'HTSIN' at graph 0.5, graph 0.51 center font ',46' front textcolor '#e6#{WHITE}'

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [*:*]

      plot '-' using 1:2 notitle with lines lc '##{YELLOW}' lw 1.5, \\
           '-' using 1:3 notitle with lines lc '##{BLUE}' lw 1.5
    GNU
    out << timestamps.zip(indicators['HTsin']['sine'], indicators['HTsin']['leadsine']).map { |candle| candle.join(' ') }.push('e') * 2
    out
  end

  def htmode
    margin = 10 * (indicators['HTmode']['htmode'].max - indicators['HTmode']['htmode'].min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%Y-%m-%d\\n%H:%M"

      set bmargin 1
      set tmargin 0

      set label 'HTMODE' at graph 0.5, graph 0.51 center font ',46' front textcolor '#e6#{WHITE}'

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [-0.5:1.5]

      plot '-' using 1:2 notitle with lines lc '##{PURPLE}' lw 1.5
    GNU
    out << timestamps.zip(indicators['HTmode']['htmode']).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def rsi
    margin = 10 * (indicators['RSI']['rsi'].max - indicators['RSI']['rsi'].min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%Y-%m-%d\\n%H:%M"
      set ytics("30" 30, "70" 70)

      set bmargin 1
      set tmargin 0

      set label 'RSI' at graph 0.5, graph 0.51 center font ',46' front textcolor '#e6#{WHITE}'

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [0:100]

      set object 1 rect from #{timestamps.first},30 to #{timestamps.last},70 fc rgb '#ee#{PURPLE}' fs solid noborder
      set arrow 1 from #{timestamps.first},30 to #{timestamps.last},30 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2
      set arrow 2 from #{timestamps.first},70 to #{timestamps.last},70 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2

      plot '-' using 1:2 notitle with lines lc '##{PURPLE}' lw 1.5
    GNU
    out << timestamps.zip(indicators['RSI']['rsi']).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def mom
    bname = 'MOM'
    sname = bname.downcase
    margin = 10 * (indicators[bname][sname].max - indicators[bname][sname].min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%Y-%m-%d\\n%H:%M"
      set ytics("0" 0)

      set bmargin 1
      set tmargin 0

      set label 'MOM' at graph 0.5, graph 0.51 center font ',46' front textcolor '#e6#{WHITE}'

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [*:*]

      plot '-' using 1:2 notitle with lines lc '##{GREEN}' lw 1.5
    GNU
    out << timestamps.zip(indicators[bname][sname]).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def obv
    bname = 'OBV'
    sname = bname.downcase
    margin = 10 * (indicators[bname][sname].max - indicators[bname][sname].min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%Y-%m-%d\\n%H:%M"
      unset ytics

      set bmargin 1
      set tmargin 0

      set label 'OBV' at graph 0.5, graph 0.51 center font ',46' front textcolor '#e6#{WHITE}'

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [*:*]

      plot '-' using 1:2 notitle with lines lc '##{BLUE}' lw 1.5
    GNU
    out << timestamps.zip(indicators[bname][sname]).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def lino
    dic_name = 'LINO'
    indicator = dic_name.downcase
    margin = 10 * (indicators[dic_name][indicator].max - indicators[dic_name][indicator].min) / 100
    maxi = indicators[dic_name][indicator].max
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%Y-%m-%d\\n%H:%M"

      set bmargin 1
      set tmargin 0

      set label 'LINO' at graph 0.5, graph 0.51 center font ',46' front textcolor '#e6#{WHITE}'

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [-100:100]

      set object 1 rect from #{timestamps.first},-45 to #{timestamps.last},45 fc rgb '#ee#{PURPLE}' fs solid noborder
      set arrow 1 from #{timestamps.first},-45 to #{timestamps.last},-45 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2
      set arrow 2 from #{timestamps.first},45 to #{timestamps.last},45 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2

      plot '-' using 1:2 notitle with lines lc '##{PURPLE}' lw 1.5
    GNU
    out << timestamps.zip(indicators[dic_name][indicator]).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def corro
    margin = 10 * (indicators['CORRO']['corro'].max - indicators['CORRO']['corro'].min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%Y-%m-%d\\n%H:%M"
      set ytics("90%%" 0.9, "-90%%" -0.9)

      set bmargin 1
      set tmargin 0

      set label 'CORRO' at graph 0.5, graph 0.51 center font ',46' front textcolor '#e6#{WHITE}'

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [-1.1:1.1]

      set object 1 rect from #{timestamps.first},-0.9 to #{timestamps.last},0.9 fc rgb '#ee#{PURPLE}' fs solid noborder
      set arrow 1 from #{timestamps.first},-0.9 to #{timestamps.last},-0.9 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2
      set arrow 2 from #{timestamps.first},0.9 to #{timestamps.last},0.9 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2

      plot '-' using 1:2 notitle with lines lc '##{PURPLE}' lw 1.5
    GNU
    out << timestamps.zip(indicators['CORRO']['corro']).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def stoch
    data = [indicators['STOCH']['slowk'], indicators['STOCH']['slowd']].flatten
    margin = 10 * (data.max - data.min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%Y-%m-%d\\n%H:%M"
      set ytics("20" 20, "80" 80)

      set bmargin 1
      set tmargin 0

      set label 'STOCH' at graph 0.5, graph 0.51 center font ',46' front textcolor '#e6#{WHITE}'

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

  def stochrsi
    bname = 'STOCHRSI'
    sname = bname.downcase
    data = [indicators[bname]['fastk'], indicators[bname]['fastd']].flatten
    margin = 10 * (data.max - data.min) / 100
    out = []
    out << <<~GNU
      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%Y-%m-%d\\n%H:%M"
      set ytics("20" 20, "80" 80)

      set bmargin 1
      set tmargin 0

      set label 'STOCHRSI' at graph 0.5, graph 0.51 center font ',46' front textcolor '#e6#{WHITE}'

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [0:100]

      set object 1 rect from #{timestamps.first},20 to #{timestamps.last},80 fc rgb '#ee#{PURPLE}' fs solid noborder
      set arrow 1 from #{timestamps.first},20 to #{timestamps.last},20 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2
      set arrow 2 from #{timestamps.first},80 to #{timestamps.last},80 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2

      plot '-' using 1:2 notitle with lines linecolor '##{BLUE}' lw 1.5, \\
           '-' using 1:3 notitle with lines linecolor '##{YELLOW}' lw 1.5
    GNU
    out << timestamps.zip(indicators[bname]['fastk'], indicators[bname]['fastd']).map { |candle| candle.join(' ') }.push('e') * 2
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
