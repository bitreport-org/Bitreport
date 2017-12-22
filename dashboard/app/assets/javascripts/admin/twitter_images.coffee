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
      canvas = document.getElementById('preview')
      ctx = canvas.getContext('2d')
      background = document.getElementById('background')
      ctx.drawImage(background, 0, 0)
      ctx.drawImage(chart, 0, 110)
      ctx.font = 'bold 50px PT Sans'
      ctx.fillStyle = '#EEEEEE'
      ctx.textAlign = 'right'
      ctx.fillText('BTCUSD 1h', 780, 80)
      ctx.fillStyle = '#db504a'
      ctx.textAlign = 'left'
      ctx.fillText('16464.0', 790, 80)
      ctx.font = 'bold 32px PT Sans'
      ctx.fillStyle = '#363631'
      ctx.textAlign = 'center'
      ctx.fillText('2017-12-14 19:14 UTC', 1810, 200)
      ctx.font = '17px PT Sans'
      ctx.fillText('Provided information is not an investing advice', 1810, 1007)
      ctx.font = 'bold 22px PT Sans'
      ctx.textAlign = 'left'
      ctx.fillText('Patterns', 1610, 260)
      ctx.fillText('Levels', 1610, 460)
      ctx.fillText('Comment', 1610, 610)
      ctx.font = '22px PT Sans'
      ctx.fillText('Bałwanek', 1610, 300)
      ctx.fillText('Kula śniegu', 1610, 340)
      ctx.fillText('Sanki', 1610, 380)
      ctx.fillText('2017-12-13 18:00', 1760, 300)
      ctx.fillText('2017-12-14 01:14', 1760, 340)
      ctx.fillText('2017-12-14 01:17', 1760, 380)
      ctx.fillText('↗', 1970, 300)
      ctx.fillText('↗', 1970, 340)
      ctx.fillText('↘', 1970, 380)
      ctx.fillText('Support', 1610, 500)
      ctx.fillText('Resistance', 1610, 540)
      ctx.fillText('15400.0', 1760, 500)
      ctx.fillText('17218.0', 1760, 540)
      wrapText(ctx, 'Wczoraj padał śnieg, więc cena Bitkojna mocno wzrosła. Cena innych kojnów też wzrosła. Jutro przychodzi odwilż, więc można się spodziewać, ze cena i tak urośnie. Ale jak będzie to się dopiero okaże...', 1610, 650, 410, 36)
    chart.src = newUrl

countdown = ->
  @time += 1
  $('#reloader').progress('increment')
  if @time == 10
    fetchImage()
  else
    @timeout = setTimeout(countdown, 250)

tryFetchImage = ->
  clearTimeout(@timeout)
  $('#reloader').progress('reset')
  @time = 0
  @timeout = setTimeout(countdown, 250)

$(document).on 'turbolinks:load', ->
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
