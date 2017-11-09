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
  $('.donation.modal').modal(inverted: true).modal 'attach events', '.cta', 'show'
  # Attach qr code popup
  $('.modal .qr').popup()
  # Scroll site after clicking features button
  $('button.features, a.features').on 'click', ->
    $('html, body').animate { scrollTop: $('.features.segment').offset().top }, 500
    $('.ui.sidebar').sidebar('hide')
  $('a.contact').on 'click', ->
    $('html, body').animate { scrollTop: $('.footer.segment').offset().top }, 500
    $('.ui.sidebar').sidebar('hide')
  $('.cta').on 'click', ->
    $('.ui.sidebar').sidebar('hide')
    $.post 'wallet/use'
  uri = "bitcoin:" + $('#address').data('address')
  qrcodelib.toCanvas document.getElementById('address'), uri, (e) ->
    return
