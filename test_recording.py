import pytest
import requests
import paramiko
import time
import os

from check_video import check_video


# External parameters
host = "localhost:5000"
wait_time = 3600
ssh_host = "virtual-device.local"
ssh_user = "operator"
local_folder = '/sample_video/'

# Dummy data START
dummy_file_location = os.path.join(os.getcwd(), 'sample_video', '1726105909-1726109509.mp4')
# Dummy data END

# # Removing ssh fixture since we have no real device over ssh
# @pytest.fixture(scope="module")
# def ssh_client():
#     c = paramiko.SSHClient()
#     c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     c.connect(ssh_host, username=ssh_user)
#     yield c
#     c.close()


@pytest.mark.parametrize("stream", [
    {"format": "mp4", "resolution": "1080p"},
    {"format": "mp4", "resolution": "720p"},
    {"format": "mov", "resolution": "1080p"},
    {"format": "mp4", "resolution": "1080i"}
])
def test_recording(stream, request):
    channel_id = int(request.node.callspec.id[6:])                          # TODO: this part is fragile
    base_url = f"http://{host}/channel/{channel_id + 1}/recording"

    # Set recording configuration
    response = requests.post(f"{base_url}/config", json=stream)
    assert response.status_code == 200
    assert response.json()["status"] == "config set"

    # Check if recording configuration was set properly
    response = requests.get(f"{base_url}/config")
    assert response.status_code == 200
    assert response.json() == stream

    # Start recording
    response = requests.post(f"{base_url}/start")
    assert response.status_code == 200
    assert response.json()["status"] == "recording started"

    # Wait for a few seconds as asked
    time.sleep(wait_time/1000)

    # Stop recording and extract file link
    response = requests.post(f"{base_url}/stop")                            # TODO: add check if recording is not
    assert response.status_code == 200                                      # ready yet and make sure recording will
    assert response.json()["status"] == "recording stopped"                 # be stopped on error
    remote_file_path = response.json()["file"]
    _, local_file_name = os.path.split(remote_file_path)
    local_file_path = local_folder + local_file_name


    # Dummy data: overriding file location since we have no real device over ssh
    local_file_path = dummy_file_location

    # # Retrieve the recorded file via SSH
    # sftp = ssh_client.open_sftp()
    # sftp.get(remote_file_path, local_file_path)

    # Validate the recorded file and Handling the results
    is_valid, message = check_video(local_file_path, local_file_name, stream, wait_time)
    assert is_valid, message