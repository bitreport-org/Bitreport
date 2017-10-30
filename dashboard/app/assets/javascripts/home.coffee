$(document).on 'turbolinks:load', ->
  # Fix menu when passed
  $('.masthead').visibility
    once: false
    onBottomPassed: ->
      $('.fixed.menu').transition 'fade in'
    onBottomPassedReverse: ->
      $('.fixed.menu').transition 'fade out'
  # Create sidebar and attach to menu open
  $('.ui.sidebar').sidebar(mobileTransition: 'overlay').sidebar 'attach events', '.toc.item'
  # Attach donation modal to cta clicks
  $('.donation.modal').modal(blurring: false).modal 'attach events', '.cta', 'show'
  # Attach qr code popup
  $('.modal .qr').popup()
