$(document).on 'turbolinks:load', ->
  return unless $('body').hasClass('pairs')
  $('.ui.dropdown').dropdown()
  $('.ui.checkbox').checkbox()
