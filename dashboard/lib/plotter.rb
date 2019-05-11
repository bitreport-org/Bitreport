# frozen_string_literal: true

class Plotter
  attr_reader :timestamps, :indicators, :step, :margin, :filename

  WHITE = 'e6e6e6'
  BLACK = '363631'
  YELLOW = 'f6d60e'
  BLUE = '5bc0eb'
  GREEN = 'b0db43'
  RED = 'db504a'
  PURPLE = 'f455c7'

  BANDS = {
    'BB' => { colors: %W[#f2#{BLUE} #66#{BLUE}], name: 'Bollinger Bands', middle: true },
    'KC' => { colors: %W[#f8#{YELLOW} #70#{YELLOW}], name: 'Keltner Channel', middle: true },
    'parabola' => { colors: %W[#f8#{RED} #70#{RED}], name: 'Parabola', middle: false },
    'channel' => { colors: %W[#f8#{YELLOW} #70#{YELLOW}], name: 'Channel', middle: false },
    'wedge' => { colors: %W[#f8#{YELLOW} #70#{YELLOW}], name: 'Wedge', middle: false }
  }.freeze

  AVERAGES = {
    'SMA' => { colors: %W[#c0#{YELLOW} #70#{YELLOW} #00#{YELLOW}], attributes: %w[slow medium fast], name: 'SMA' },
    'EMA' => { colors: %W[#c0#{BLUE} #70#{BLUE} #00#{BLUE}], attributes: %w[slow medium fast], name: 'EMA' },
    'ALLIGATOR' => { colors: %W[#70#{BLUE} #70#{GREEN} #70#{RED}], attributes: %w[jaw lips teeth], name: 'Alligator' }
  }.freeze

  DOUBLES = {
    'double_top' => { color: "#70#{RED}", symbol: '▼', offset: '0,1', name: 'Double Top' },
    'double_bottom' => { color: "#70#{GREEN}", symbol: '▲', offset: '0,-1', name: 'Double Bottom' }
  }.freeze

  def initialize(timestamps:, indicators: {})
    @timestamps = timestamps
    @indicators = indicators
    @step = timestamps[1].to_i - timestamps[0].to_i
    @margin = (10 * (highs.max.to_f - lows.min.to_f) / 100)
    @filename = 'plot-' + SecureRandom.uuid + '.png'
    @plots = []
    @data = []
  end

  def plot
    out = []
    out << terminal
    out << upper_preamble
    out << draw_levels
    out << draw_doubles
    prepare_volume
    prepare_bands_bg
    prepare_ichimoku_bg
    prepare_candles
    prepare_bands_fg
    prepare_ichimoku_fg
    prepare_sar
    prepare_averages
    prepare_tds
    out << commands
    out << send((indicators.keys & %w[EWO MACD RSI STOCH STOCHRSI OBV MOM ADX AROON]).first.downcase.to_sym)
    io = IO.popen('gnuplot -persist', 'w+')
    io << out.join("\n")
    io.close_write
    io.read
  end

  private

  def terminal
    out = ["set terminal pngcairo truecolor font 'PT Sans,15' size 1570,890 background rgb '##{BLACK}'"]
    out << 'unset output'
    out
  end

  def price_length
    m = [lows.min - margin, highs.max + margin]
    (Math.log10((m.max - m.min) / 10).round.abs + 3).clamp(6, 12)
  end

  def upper_preamble
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
    return unless indicators['levels']['levels']

    out = []
    indicators['levels']['levels'].each do |level|
      value = level['value']
      next unless (lows.min..highs.max).cover?(value)

      out << <<~TXT
        set arrow from #{level['first_occurrence']},#{value} to #{timestamps.last},#{value} nohead lc rgb "#c0#{YELLOW}" lw 1.5 dt 1
      TXT
    end
    out
  end

  def prepare_volume
    @plots << "using 1:4:(#{0.95 * step}):($3 < $2 ? -1 : 1) axes x1y2 notitle with boxes palette fs transparent solid 0.1 noborder"
    @data << timestamps.zip(opens, closes, volumes).map { |candle| candle.join(' ') }.push('e')
  end

  def prepare_bands_bg
    BANDS.each do |name, info|
      indicator = indicators[name]
      next unless indicator

      @plots << "using 1:2:3 notitle with filledcurves linecolor '#{info[:colors][0]}'" <<
        "using 1:2 notitle with lines linecolor '#{info[:colors][1]}' lw 1.5" <<
        "using 1:3 notitle with lines linecolor '#{info[:colors][1]}' lw 1.5"
      @data << timestamps.zip(indicator['upper_band'],
                              indicator['lower_band']).map { |candle| candle.join(' ') }.push('e') * 3
    end
  end

  def prepare_ichimoku_bg
    return unless indicators['ICM']

    @plots << "using 1:2:3 notitle with filledcurves above linecolor '#dd#{GREEN}'" <<
      "using 1:2:3 notitle with filledcurves below linecolor '#dd#{RED}'" <<
      "using 1:2 notitle with lines linecolor '#88#{GREEN}' lw 1.5" <<
      "using 1:3 notitle with lines linecolor '#88#{RED}' lw 1.5"
    @data << timestamps.zip(indicators['ICM']['leading_span_a'],
                            indicators['ICM']['leading_span_b']).map { |candle| candle.join(' ') }.push('e') * 4
  end

  def prepare_candles
    @plots << 'using 1:2:3:4:5:($5 < $2 ? -1 : 1) notitle with candlesticks palette lw 1.5'
    @data << timestamps.zip(opens, lows, highs, closes).map { |candle| candle.join(' ') }.push('e')
  end

  def prepare_bands_fg
    BANDS.each do |name, info|
      indicator = indicators[name]
      next unless indicator && info[:middle]

      @plots << "using 1:2 title '#{info[:name]}' with lines linecolor '#{info[:colors][1]}' lw 1.5"
      @data << timestamps.zip(indicator['middle_band']).map { |candle| candle.join(' ') }.push('e')
    end
  end

  def prepare_ichimoku_fg
    return unless indicators['ICM']

    @plots << "using 1:2 title 'Ichimoku Base Line' with lines linecolor '#60#{RED}' lw 1.5"
    @data << timestamps.zip(indicators['ICM']['base_line']).map { |candle| candle.join(' ') }.push('e')
  end

  def prepare_sar
    return unless indicators['SAR']

    @plots << "using 1:2 title 'SAR' with points lt 6 ps 0.3 lc '##{BLUE}'"
    @data << timestamps.zip(indicators['SAR']['sar']).map { |candle| candle.join(' ') }.push('e')
  end

  def prepare_averages
    AVERAGES.each do |name, info|
      indicator = indicators[name]
      next unless indicator

      @plots << "using 1:2 title '#{info[:name]} #{info[:attributes][0]}' with lines lw 1.5 lc '#{info[:colors][0]}'" <<
        "using 1:3 title '#{info[:name]} #{info[:attributes][1]}' with lines lw 1.5 lc '#{info[:colors][1]}'" <<
        "using 1:4 title '#{info[:name]} #{info[:attributes][2]}' with lines lw 1.5 lc '#{info[:colors][2]}'"
      @data << timestamps.zip(indicator[info[:attributes][0]],
                              indicator[info[:attributes][1]],
                              indicator[info[:attributes][2]]).map { |candle| candle.join(' ') }.push('e') * 3
    end
  end

  def prepare_tds
    return unless indicators['TDS']
    # 💩💩💩
    tdsvals = { 'pbuy' => -1, 'buy' => 0, 'sell' => 0, 'psell' => 1 }
    vals = indicators['TDS']['tds'].map { |v| tdsvals[v] }
    prices = indicators['TDS']['tds'].each_with_index.map do |v, i|
      v.include?('buy') ? lows[i] - @margin / 2 : highs[i] + @margin / 2
    end
    @plots << 'using 1:2:3 title "TD Sequential" with points pt 6 palette' <<
      'using 1:2:3 notitle with points pt 7 palette'
    @data << timestamps.zip(prices, vals).map { |candle| candle.join(' ') }.push('e')
    counts = [1]
    (1..indicators['TDS']['tds'].count).each do |i|
      counts << (indicators['TDS']['tds'][i] == indicators['TDS']['tds'][i - 1] || (indicators['TDS']['tds'][i] == 'buy' && indicators['TDS']['tds'][i - 1] == 'pbuy') || (indicators['TDS']['tds'][i] == 'pbuy' && indicators['TDS']['tds'] == 'buy') || (indicators['TDS']['tds'][i] == 'sell' && indicators['TDS']['tds'][i - 1] == 'psell') || (indicators['TDS']['tds'][i] == 'psell' && indicators['TDS']['tds'][i - 1] == 'sell') ? counts.last + 1 : 1)
    end
    @data << timestamps.zip(prices, vals, counts).select { |el| el[1] && el[3] >= 9 }.map { |candle| candle[0..2].join(' ') }.push('e')
  end

  def draw_doubles
    out = []
    DOUBLES.each do |name, info|
      indicator = indicators[name]
      next unless indicator && indicator['A']

      out << <<~TXT
        set label at #{indicator['A'][0]}, #{indicator['A'][1]} "#{info[:symbol]}" center font ',20' front textcolor '#{info[:color]}' offset #{info[:offset]}
        set label at #{indicator['C'][0]}, #{indicator['C'][1]} "#{info[:symbol]}" center font ',20' front textcolor '#{info[:color]}' offset #{info[:offset]}
      TXT
    end
    out
  end

  def commands
    "plot '-' " + @plots.join(",\\\n'-' ") + "\n" + @data.join("\n")
  end

  def lower_preamble(label, margin: 0, yrange: '*:*', ytics: [0])
    <<~GNU
      unset label

      set size 1.0,0.25
      set origin 0.0,0.05

      set format x "%Y-%m-%d\\n%H:%M"
      set ytics(#{ytics.map { |tic| %("#{tic}" #{tic}) }.join(', ')})

      set bmargin 1
      set tmargin 0

      set label '#{label}' at graph 0.5, graph 0.51 center font ',46' front textcolor '#e6#{WHITE}'

      set offsets 0,0,#{margin},#{margin}
      set xrange [#{timestamps.first}:#{timestamps.last}]
      set yrange [#{yrange}]

      unset arrow
    GNU
  end

  def ewo
    margin = (indicators['EWO']['ewo'].max - indicators['EWO']['ewo'].min) / 10
    out = []
    out << lower_preamble('EWO', margin: margin)
    out << "plot '-' using 1:2:($2 < 0 ? -1 : 1) notitle with impulses palette lw 1.5"
    out << timestamps.zip(indicators['EWO']['ewo']).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def macd
    data = [indicators['MACD']['histogram'], indicators['MACD']['signal'], indicators['MACD']['macd']].flatten
    margin = (data.max - data.min) / 10
    out = []
    out << lower_preamble('MACD', margin: margin)
    out << <<~GNU
      plot '-' using 1:2 notitle with impulses lc '##{PURPLE}' lw 1.5, \\
           '-' using 1:3 notitle with lines lc '##{YELLOW}' lw 1.5, \\
           '-' using 1:4 notitle with lines lc '##{BLUE}' lw 1.5
    GNU
    out << timestamps.zip(indicators['MACD']['histogram'],
                          indicators['MACD']['signal'],
                          indicators['MACD']['macd']).map { |candle| candle.join(' ') }.push('e') * 3
    out
  end

  def rsi
    out = []
    out << lower_preamble('RSI', margin: 10, yrange: '*<25:75<*', ytics: [0, 30, 70, 100])
    out << <<~GNU
      set object 1 rect from #{timestamps.first},30 to #{timestamps.last},70 fc rgb '#ee#{PURPLE}' fs solid noborder
      set arrow 1 from #{timestamps.first},30 to #{timestamps.last},30 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2
      set arrow 2 from #{timestamps.first},70 to #{timestamps.last},70 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2

      plot '-' using 1:2 notitle with lines lc '##{PURPLE}' lw 1.5
    GNU
    out << timestamps.zip(indicators['RSI']['rsi']).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def mom
    margin = 10 * (indicators['MOM']['mom'].max - indicators['MOM']['mom'].min) / 100
    out = []
    out << lower_preamble('MOM', margin: margin)
    out << "plot '-' using 1:2 notitle with lines lc '##{GREEN}' lw 1.5"
    out << timestamps.zip(indicators['MOM']['mom']).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def obv
    margin = (indicators['OBV']['obv'].max - indicators['OBV']['obv'].min) / 10
    out = []
    out << lower_preamble('OBV', margin: margin, ytics: [])
    out << "plot '-' using 1:2 notitle with lines lc '##{BLUE}' lw 1.5"
    out << timestamps.zip(indicators['OBV']['obv']).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def stoch
    out = []
    out << lower_preamble('STOCH', margin: 10, yrange: '*<15:85<*', ytics: [0, 20, 80, 100])
    out << <<~GNU
      set object 1 rect from #{timestamps.first},20 to #{timestamps.last},80 fc rgb '#ee#{PURPLE}' fs solid noborder
      set arrow 1 from #{timestamps.first},20 to #{timestamps.last},20 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2
      set arrow 2 from #{timestamps.first},80 to #{timestamps.last},80 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2

      plot '-' using 1:2 notitle with lines linecolor '##{BLUE}' lw 1.5, \\
           '-' using 1:3 notitle with lines linecolor '##{YELLOW}' lw 1.5
    GNU
    out << timestamps.zip(indicators['STOCH']['k'],
                          indicators['STOCH']['d']).map { |candle| candle.join(' ') }.push('e') * 2
    out
  end

  def stochrsi
    out = []
    out << lower_preamble('STOCH RSI', margin: 10, yrange: '*<15:85<*', ytics: [0, 20, 80, 100])
    out << <<~GNU
      set object 1 rect from #{timestamps.first},20 to #{timestamps.last},80 fc rgb '#ee#{PURPLE}' fs solid noborder
      set arrow 1 from #{timestamps.first},20 to #{timestamps.last},20 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2
      set arrow 2 from #{timestamps.first},80 to #{timestamps.last},80 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2

      plot '-' using 1:2 notitle with lines linecolor '##{BLUE}' lw 1.5, \\
           '-' using 1:3 notitle with lines linecolor '##{YELLOW}' lw 1.5
    GNU
    out << timestamps.zip(indicators['STOCHRSI']['k'],
                          indicators['STOCHRSI']['d']).map { |candle| candle.join(' ') }.push('e') * 2
    out
  end

  def adx
    margin = 10 * (indicators['ADX']['adx'].max - indicators['ADX']['adx'].min) / 100
    out = []
    out << lower_preamble('ADX', margin: margin, ytics: [0, 25, 50, 75, 100])
    out << <<~GNU
      set arrow 1 from #{timestamps.first},25 to #{timestamps.last},25 nohead lc rgb '#66#{PURPLE}' lw 1.5 dt 2

      plot '-' using 1:2 notitle with lines lc '##{GREEN}' lw 1.5
    GNU
    out << timestamps.zip(indicators['ADX']['adx']).map { |candle| candle.join(' ') }.push('e')
    out
  end

  def aroon
    out = []
    out << lower_preamble('AROON', margin: 10, yrange: '0:100', ytics: [0, 100])
    out << <<~GNU
      plot '-' using 1:2 notitle with lines lc '##{YELLOW}' lw 1.5, \\
           '-' using 1:3 notitle with lines lc '##{BLUE}' lw 1.5
    GNU
    out << timestamps.zip(indicators['AROON']['up'],
                          indicators['AROON']['down']).map { |candle| candle.join(' ') }.push('e') * 2
    out
  end

  def opens
    indicators['price']['open']
  end

  def closes
    indicators['price']['close']
  end

  def highs
    indicators['price']['high']
  end

  def lows
    indicators['price']['low']
  end

  def volumes
    indicators['volume']['volume']
  end
end
