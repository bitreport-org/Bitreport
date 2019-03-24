# frozen_string_literal: true

module Admin
  class PostsController < AdminController
    include Pagy::Backend

    def index
      @pagy, @posts = pagy(TwitterPost.includes(report: [:pair]).order(published_at: :desc),
                           items: 10)
    end
  end
end
