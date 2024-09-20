import ffmpeg

def check_video(file_path, stream_json, duration_expected: float):

    # Extract format from file
    _, file_format = file_path.split('.')

    # Extract expected file format
    file_format_expected = stream_json.get('format')

    # Extract expected height
    height_expected = int(stream_json.get('resolution')[:-1])

    # Extract expected scan type
    scan_expected = stream_json.get('resolution')[-1]

    # Getting video duration, height and scan from file
    ffprobe_output = ffmpeg.probe(
                 file_path,
                 cmd='ffprobe',
                 v='error',
                 )
    video_stream = next((stream for stream in ffprobe_output['streams'] if stream['codec_type'] == 'video'), None)

    duration = float(video_stream['duration'])
    height = int(video_stream['height'])
    scan_raw = video_stream['field_order']
    match scan_raw:
        case 'progressive':
            scan = 'p'
        case 'tt' | 'bb' | 'tb' | 'bt':
            scan = 'i'
        case _:
            scan = scan_raw

    return {
        "expected": {
            "format": file_format_expected,
            "scan": scan_expected,
            "height": height_expected,
            "duration": duration_expected
        },
        "actual": {
            "format": file_format,
            "scan": scan,
            "height": height,
            "duration": duration
        }

    }