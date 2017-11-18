fetchImage = ->
  oldUrl = $('img#preview').attr('src')
  newUrl = '/admin/twitter_image_preview?' + $('form#new_admin_twitter_image').serialize()
  if oldUrl != newUrl
    $('img#preview').attr('src', newUrl)

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
