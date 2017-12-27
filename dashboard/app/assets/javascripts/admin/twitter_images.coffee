wrapText = (context, text, x, y, maxWidth, lineHeight) ->
  words = text.split(' ')
  line = ''
  n = 0
  while n < words.length
    testLine = line + words[n] + ' '
    metrics = context.measureText(testLine)
    testWidth = metrics.width
    if testWidth > maxWidth and n > 0
      context.fillText line, x, y
      line = words[n] + ' '
      y += lineHeight
    else
      line = testLine
    n++
  context.fillText line, x, y
  return

fetchImage = ->
  oldUrl = $('img#preview').attr('src')
  newUrl = '/admin/twitter_image_preview?' + $('form#new_admin_twitter_image').serialize()
  if oldUrl != newUrl
    chart = new Image()
    chart.onload = ->
      unless @firstTimeInit == true
        $.getJSON '/admin/twitter_image_data?' + $('form#new_admin_twitter_image').serialize(), (data) ->
          console.log(data['levels'])
          for pattern, pattern_data of data['patterns']
            for direction, timestamps of pattern_data
              for timestamp in timestamps
                $('table#patterns').append('<tr><td class="collapsing"><div class="ui fitted slider checkbox"><input type="checkbox"> <label></label></div></td><td>'+pattern+'</td><td>'+direction+'</td><td>'+$.format.date(timestamp*1000, "yyyy-MM-dd hh:mm")+'</td></tr>')
          for type, values of data['levels']
            for value in values
              $('table#levels').append('<tr><td class="collapsing"><div class="ui fitted slider checkbox"><input type="checkbox"> <label></label></div></td><td>'+type+'</td><td>'+value+'</td></tr>')
        $('table .ui.checkbox').checkbox()
        @firstTimeInit = true
      canvas = document.getElementById('preview')
      ctx = canvas.getContext('2d')
      background = document.getElementById('background')
      ctx.drawImage(background, 0, 0)
      ctx.drawImage(chart, 0, 110)
      ctx.font = 'bold 56px PT Sans'
      ctx.fillStyle = '#EEEEEE'
      ctx.textAlign = 'center'
      symbol = $('#admin_twitter_image_symbol').val()
      timeframe = $('#admin_twitter_image_timeframe').val()
      ctx.fillText("#{symbol} #{timeframe}", 820, 80)
#      ctx.fillStyle = '#db504a'
#      ctx.textAlign = 'left'
#      ctx.fillText('16464.0', 790, 80)
      ctx.font = 'bold 32px PT Sans'
      ctx.fillStyle = '#363631'
      ctx.textAlign = 'center'
      date = $.format.date($.now(), 'yyyy-MM-dd HH:mm UTC')
      ctx.fillText(date, 1810, 200)
      ctx.font = '17px PT Sans'
      ctx.fillText('Provided information is not an investing advice', 1810, 1007)
      ctx.textAlign = 'left'
      offset = 220
      patterns = []
      for pattern in $('table#patterns input[type=checkbox]:checked').parents('tr')
        values = []
        $(pattern).children('td:gt(0)').each ->
          values.push(@innerText)
        patterns.push(values)
      if patterns.length > 0
        offset += 40
        ctx.font = 'bold 22px PT Sans'
        ctx.fillText('Patterns', 1610, offset)
        offset += 40
        ctx.font = '22px PT Sans'
        for pattern in patterns
          ctx.fillText(pattern[0], 1610, offset)
          ctx.fillText(pattern[2], 1760, offset)
          ctx.fillText(pattern[1], 1970, offset)
          offset += 40
      levels = []
      for level in $('table#levels input[type=checkbox]:checked').parents('tr')
        values = []
        $(level).children('td:gt(0)').each ->
          values.push(@innerText)
        levels.push(values)
      if levels.length > 0
        offset += 40
        ctx.font = 'bold 22px PT Sans'
        ctx.fillText('Levels', 1610, offset)
        offset += 40
        ctx.font = '22px PT Sans'
        for level in levels
          ctx.fillText(level[0], 1610, offset)
          ctx.fillText(level[1], 1760, offset)
          offset += 40
      if $('#admin_twitter_image_comment').val() != ''
        offset += 40
        ctx.font = 'bold 22px PT Sans'
        ctx.fillText('Comment', 1610, offset)
        offset += 40
        ctx.font = '22px PT Sans'
        wrapText(ctx, $('#admin_twitter_image_comment').val(), 1610, offset, 410, 36)
    chart.src = newUrl

countdown = ->
  @time += 1
  $('#reloader').progress('increment')
  if @time == 10
    fetchImage()
  else
    @timeout = setTimeout(countdown, 200)

tryFetchImage = ->
  clearTimeout(@timeout)
  $('#reloader').progress('reset')
  @time = 0
  @timeout = setTimeout(countdown, 200)

$(document).on 'turbolinks:load', ->
  return unless $('body').hasClass('twitter_images')
  $('.ui.dropdown').dropdown()
  $('.ui.checkbox').checkbox()
  $('#reloader').progress
    total: 10
    value: 10
  $('img#preview').error ->
    $('img#preview').attr('src', '')
  $('form#new_admin_twitter_image :input').on 'change input', ->
    tryFetchImage()
  fetchImage()
  canvas = document.getElementById('preview')
  ctx = canvas.getContext('2d')
  background = document.getElementById('background')
  ctx.drawImage(background, 0, 0)
  downloadLink = $('#save-image')
  downloadLink.on 'click', (e) ->
    downloadLink.attr('href', canvas.toDataURL())
    symbol = $('#admin_twitter_image_symbol').val()
    date = $.format.date($.now(), 'yyyy-MM-dd HH:mm')
    downloadLink.attr('download', "Twitter #{symbol} #{date}.png")
