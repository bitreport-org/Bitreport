setDownloadUrl = (url) ->
  downloadLink = $('#save-image')
  downloadLink.attr('href', url)
  date = $.format.date($.now(), 'yyyy-MM-dd HH:mm')
  downloadLink.attr('download', "Twitter #{window.symbol} #{date}.png")

fetchImage = ->
  if $('body').hasClass('new')
    fetchNewImage()
  else
     fetchExistingImage()

fetchNewImage = ->
  oldUrl = $('img#preview').attr('src')
  newUrl = '/admin/twitter_image_preview?' + $('form').serialize()
  document.getElementById('preview').src = newUrl
  setDownloadUrl(newUrl)

fetchExistingImage = ->
  oldUrl = $('img#preview').attr('src')
  levels = []
  for level in $('table#levels input[type=checkbox]:checked').parents('tr')
    values = []
    $(level).children('td:gt(0)').each ->
      values.push(@innerText)
    levels.push(values)
  newUrl = '/admin/twitter_image_preview/' + window.image_id + '?' + $('form').serialize()
  document.getElementById('preview').src = newUrl
  setDownloadUrl(newUrl)

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
  $('form :input').on 'change input', ->
    tryFetchImage()
  fetchImage()
