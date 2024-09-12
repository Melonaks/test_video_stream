import mimetypes
import subprocess

def check_video(file_path, file_name, stream_json, expected_duration):
    print("Checking video format")

    # Extract MIME from recorded file
    video_raw_mime, _ = mimetypes.guess_type(file_path)

    # Extract duration from recorded file
    timestamp_start, timestamp_end = (file_name.split('.')[0]).split('-')
    duration = (int(timestamp_end) - int(timestamp_start))

    # Extract expected file format
    file_format_expected = stream_json['format']

    # Extract expected resolution
    expected_resolution = stream_json['resolution'][:-1]

    # Extract expected scan type
    expected_scan_type = stream_json['resolution'][-1]

    # Defining MIME alias
    match video_raw_mime:
        case 'video/quicktime':
            mime = "mov"
        case 'video/x-msvideo':
            mime = "avi"
        case 'video/mp4':
            mime = "mp4"
        case _:
            mime = "Unknown"

    if mime != file_format_expected:
        return False, f"Format mismatch: Actual MIME is {mime}, but expected file format is {file_format_expected}"

    # Getting video resolution and scan
    ffprobe_output_csv = (subprocess.check_output(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=height,field_order,duration',
         '-of', 'csv', file_path]).decode().strip())
    _, resolution, scan, real_duration = ffprobe_output_csv.split(',')

    # Checking scan type
    if expected_scan_type != scan[0]:
        return False, f"Scan type mismatch: Actual scan type is {scan[0]}, but expected is {expected_scan_type}"

    # Checking video resolution
    if int(expected_resolution) != int(resolution):
        return False, f"Resolution mismatch: Actual resolution is {resolution}, but expected is {expected_resolution}"

    # Checking duration
    if expected_duration != duration:
        return False, f"Duration mismatch: Actual duration is {duration}, but expected is {expected_duration}"

    return True, ""