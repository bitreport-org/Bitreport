# frozen_string_literal: true

FactoryBot.define do
  factory :report do
    pair

    limit { 100 }
    timeframe { 6 }
    indicators { Faker::Hipster.words(3) }
    comment { Faker::Hipster.sentence }
    image { Rack::Test::UploadedFile.new(File.open(Rails.root.join('spec', 'files', 'report.png')), 'image/png') }
  end
end
