# frozen_string_literal: true

FactoryBot.define do
  factory :pair do
    transient do
      first_part { Faker::Currency.code }
      second_part { Faker::Currency.code }
    end
    symbol { "#{first_part}#{second_part}" }
    name { Faker::Currency.name }
    exchange { 'binance' }
    tags { %W[##{first_part} $#{first_part}] }

    trait(:with_reports) do
      after(:create) do |pair|
        create(:report, pair: pair)
      end
    end
  end
end
