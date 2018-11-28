$(document).on 'turbolinks:load', ->
  return unless $('body').hasClass('twitter_responses')
  $('.ui.dropdown').dropdown()
