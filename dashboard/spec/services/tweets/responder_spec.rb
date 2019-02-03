# frozen_string_literal: true

require 'rails_helper'

RSpec.describe Tweets::Responder do
  subject(:service) { described_class.new(params) }

  let(:params) { { tweet_id: 1, tweet_text: tweet_text } }
  let(:tweet_text) { "@Bitreport_org #{symbol}" }

  context 'with valid tweet_text' do
    context 'when pair exists' do
      let(:pair) { create(:pair) }
      let(:symbol) { "$#{pair.symbol[0..3]}" }

      before do
        stub_fill
        stub_twitter_update
        reports_creator_stub = instance_double(Reports::Creator, call: create(:report, pair: pair))
        allow(Reports::Creator).to receive(:new).and_return(reports_creator_stub)
      end

      it 'creates new TwitterPost' do
        expect { service.call }.to change(TwitterPost, :count).from(0).to(1)
      end
    end
  end
end
