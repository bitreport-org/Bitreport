require 'test_helper'

class TwitterImagesControllerTest < ActionDispatch::IntegrationTest
  setup do
    @twitter_image = twitter_images(:one)
  end

  test "should get index" do
    get twitter_images_url
    assert_response :success
  end

  test "should get new" do
    get new_twitter_image_url
    assert_response :success
  end

  test "should create twitter_image" do
    assert_difference('TwitterImage.count') do
      post twitter_images_url, params: { twitter_image: { image_data: @twitter_image.image_data, name: @twitter_image.name } }
    end

    assert_redirected_to twitter_image_url(TwitterImage.last)
  end

  test "should show twitter_image" do
    get twitter_image_url(@twitter_image)
    assert_response :success
  end

  test "should get edit" do
    get edit_twitter_image_url(@twitter_image)
    assert_response :success
  end

  test "should update twitter_image" do
    patch twitter_image_url(@twitter_image), params: { twitter_image: { image_data: @twitter_image.image_data, name: @twitter_image.name } }
    assert_redirected_to twitter_image_url(@twitter_image)
  end

  test "should destroy twitter_image" do
    assert_difference('TwitterImage.count', -1) do
      delete twitter_image_url(@twitter_image)
    end

    assert_redirected_to twitter_images_url
  end
end
