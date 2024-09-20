import pytest
import requests
import paramiko
import time
import os
import json

from check_video import check_video
from client_api.client_http import HttpClient

# External parameters
host = "localhost:5000"
wait_time = 3600.0
ssh_host = "virtual-device.local"
ssh_user = "operator"
local_folder = '/sample_video/'

# Parametrization config
video_format = ["mp4", "avi", "mov"]
video_height = ["480", "720", "1080", "2160"]
video_scan = ["p", "i"]

# Dummy data START
local_file_path_dummy = os.path.join(os.getcwd(), 'sample_video', '1726105909-1726109509.mp4')
# Dummy data END

# # Removing ssh fixture since we have no real device over ssh
# @pytest.fixture
# def ssh_client():
#     c = paramiko.SSHClient()
#     c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     c.connect(ssh_host, username=ssh_user)
#     yield c
#     c.close()


@pytest.fixture
def client_api():
    c = HttpClient(host)
    yield c

@pytest.fixture
def channel():
    if not hasattr(channel, "counter"):
        channel.counter = 0
    channel.counter += 1
    return channel.counter


@pytest.mark.parametrize("scan", video_scan)
@pytest.mark.parametrize("height", video_height)
@pytest.mark.parametrize("video_format", video_format)
def test_recording(video_format, height, scan, channel, client_api):

    # Preparing channel and JSON payload
    payload = { "format": video_format, "resolution": height + scan}

    # Set recording configuration
    response = client_api.post('config', channel, json=payload)
    assert response.get('status') == "config set"

    # Check if recording configuration was set properly
    response = client_api.get('config', channel)
    assert response == payload

    # Start recording
    response = client_api.post('start', channel)
    assert response.get('status') == "recording started"

    # Wait for a few seconds as asked
    time.sleep(wait_time/1000)

    # Stop recording and extract file link
    response = client_api.post('stop', channel)
    assert response.get('status') == "recording stopped"

    remote_file_path = response.get('file')
    _, local_file_name = os.path.split(remote_file_path)
    local_file_path = local_folder + local_file_name

    # # Retrieve the recorded file via SSH
    # sftp = ssh_client.open_sftp()
    # sftp.get(remote_file_path, local_file_path)

    # Overriding file location since we have no real device over ssh
    # Dummy data START
    local_file_path = local_file_path_dummy
    # Dummy data END

    # Getting comparative results of file and config
    check_video_result = check_video(local_file_path, payload, wait_time)

    # Asserting results
    for key in check_video_result.get('expected'):

        expected = check_video_result.get('expected')
        actual = check_video_result.get('actual')

        assert (expected.get(key) == actual.get(key)
        ), f'{key} mismatch: expected {expected.get(key)}, but got {actual.get(key)}'