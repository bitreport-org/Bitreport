# frozen_string_literal: true

module Admin
  class PostsController < AdminController
    def index
      @posts = TwitterPost.includes(report: [:pair]).all # paginate with pagy
    end
  end
end
