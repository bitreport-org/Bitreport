# frozen_string_literal: true

module Api
  class EventsController < ApiController
    # POST /api/events
    def create
      PushDevice.find_each do |push|
        Webpush.payload_send(
          message: 'Something happened',
          endpoint: push.endpoint,
          p256dh: push.p256dh,
          auth: push.auth,
          vapid: {
            subject: 'mailto:support@bitreport.org',
            public_key: Settings.push.vapid.public_key,
            private_key: Settings.push.vapid.private_key
          }
        )
      end
    end
  end
end
