# frozen_string_literal: true

require 'rails_helper'

RSpec.describe Tweets::Responder do
  subject(:service) { described_class.new(params) }

  let(:params) { { tweet_id: 1, symbols: symbols, screen_name: screen_name } }
  let(:symbols) { [symbol] }
  let(:screen_name) { nil }
  let!(:twitter_stub) { stub_twitter_update }

  context 'with valid symbols' do
    context 'when pair exists' do
      let(:pair) { create(:pair) }
      let(:symbol) { pair.symbol[0..3] }

      before do
        reports_creator_stub = instance_double(Reports::Creator, call: create(:report, pair: pair))
        allow(Reports::Creator).to receive(:new).and_return(reports_creator_stub)
      end

      it 'creates new TwitterPost' do
        expect { service.call }.to change(TwitterPost, :count).from(0).to(1)
      end

      it 'creates a post on Twitter' do
        service.call
        expect(twitter_stub).to have_been_requested
      end

      context 'when screen_name is set to self' do
        let(:screen_name) { 'Bitreport_org' }

        it 'does not post anything on Twitter' do
          service.call
          expect(twitter_stub).not_to have_been_requested
        end
      end
    end

    context 'when pair does not exist' do
      let(:symbol) { 'YOLO' }

      context 'when pair can be created' do
        before do
          stub_core_fill
          reports_creator_stub = instance_double(Reports::Creator, call: create(:report))
          allow(Reports::Creator).to receive(:new).and_return(reports_creator_stub)
        end

        it 'creates new TwitterPost' do
          expect { service.call }.to change(TwitterPost, :count).from(0).to(1)
        end

        it 'creates new Pair' do
          expect { service.call }.to change(Pair, :count).by(1)
        end

        it 'creates a post on Twitter' do
          service.call
          expect(twitter_stub).to have_been_requested
        end

        context 'when screen_name is set to self' do
          let(:screen_name) { 'Bitreport_org' }

          it 'does not post anything on Twitter' do
            service.call
            expect(twitter_stub).not_to have_been_requested
          end
        end
      end

      context 'when core has no result for the pair' do
        before do
          stub_core_fill_failure
        end

        it 'does not create a TwitterPost' do
          expect { service.call }.not_to change(TwitterPost, :count)
        end

        # TODO: This will loop, won't it?
        it 'creates a post on Twitter' do
          service.call
          expect(twitter_stub).to have_been_requested
        end
      end
    end
  end

  context 'with invalid symbols' do
    context 'when tweet does not include any cashtags' do
      let(:symbols) { [] }

      it 'does not generate a report' do
        expect(Reports::Creator).not_to receive(:new)
        service.call
      end

      it 'does not post anything on Twitter' do
        service.call
        expect(twitter_stub).not_to have_been_requested
      end
    end
  end
end
