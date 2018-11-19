# frozen_string_literal: true

class PushDevicesController < ApplicationController
  skip_before_action :verify_authenticity_token, only: %i[create destroy]

  def show
    render 'show'
  end

  def create
    PushDevice.create(push_device_params)
  end

  def destroy
    pd = PushDevice.find_by(endpoint: params[:subscription][:endpoint])
    pd&.destroy
  end

  private

  def push_device_params
    params.require(:subscription).permit(:endpoint, keys: %i[p256dh auth])
  end
end
