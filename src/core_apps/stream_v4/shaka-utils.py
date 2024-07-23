import subprocess
import os
import uuid
import base64

def get_16_byte_key(base64_string):
    # Decode the Base64 string and take the first 16 bytes
    decoded = base64.b64decode(base64_string)
    return decoded[:16].hex()

def run_shaka_packager(input_file, output_dir, base_url):
    # Generate a unique key_id
    key_id = uuid.uuid4().hex

    # Get a 16-byte key from the Base64 string
    base64_key = "XVBovsmzhP9gRIZxWfFta3VVRPzVEWmJsazEJ46I"
    hex_key = get_16_byte_key(base64_key)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Construct the command
    #     command = [
    #         "shaka-packager",
    #         f"in={input_file},stream=video,output={os.path.join(output_dir, 'video_1080p.mp4')}",
    #         f"in={input_file},stream=audio,output={os.path.join(output_dir, 'audio.mp4')}",
    #         "--enable_raw_key_encryption",
    #         "--protection_scheme", "cenc",
    #         "--mpd_output", os.path.join(output_dir, "manifest.mpd"),
    #         "--generate_static_live_mpd",
    #         "--segment_duration", "4",
    #         "--base_urls", base_url,
    #         "--keys", f"label=:key_id={key_id}:key={hex_key}"
    #     ]

#     key_id = (
#         "XVBovsmzhP9gRIZxWEJ46I"  # Replace with your actual key ID
    

    #     command = [
    #         "shaka-packager",
    #         "in=input_1080p.mp4,stream=video,output=output_1080p.mp4",
    #         "in=input_audio.mp4,stream=audio,output=output_audio.mp4",
    #         "--mpd_output", "manifest.mpd",
    #         "--segment_duration", "4",
    #         "--fragment_duration", "2",
    #         "--generate_static_live_mpd",
    #         "--enable_playready_encryption",
    #         "--protection_scheme", "cenc",
    #         "--playready_server_url", "https://test.playready.microsoft.com/service/rightsmanager.asmx",
    #         "--program_identifier", "XVBovsmzhP9gRIZxWfFta3VVRPzVEWmJsazEJ46I",
    #         "--keys", f"label=:key_id={key_id}:key=XVBovsmzhP9gRIZxWfFta3VVRPzVEWmJsazEJ46I",
    #     ]

    command = [
        "shaka-packager",
        # "in=input_360p.mp4,stream=video,output=output_360p.mp4",
        # "in=input_480p.mp4,stream=video,output=output_480p.mp4",
        # "in=input_720p.mp4,stream=video,output=output_720p.mp4",
        f"in={input_file},stream=video,output=output_1080p.mp4",
        # "in=input_audio.mp4,stream=audio,output=output_audio.mp4",
        "--mpd_output", "manifest.mpd",
        "--segment_duration", "4",
        "--fragment_duration", "2",
        "--generate_static_live_mpd",
        "--enable_raw_key_encryption",
        "--protection_scheme", "cenc",
        "--keys", f"label=:key_id={hex_key}:key={hex_key}",
        "--protection_systems", "PlayReady,Widevine",
        "--playready_extra_header_data", f"<LA_URL>https://test.playready.microsoft.com/service/rightsmanager.asmx</LA_URL>",

        ]

    try:
        # Run the command
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Shaka Packager command executed successfully.")
        print("Output:", result.stdout)
        return True, key_id
    except subprocess.CalledProcessError as e:
        print("An error occurred while running Shaka Packager:")
        print("Error output:", e.stderr)
        return False, key_id
# Example usage

home_path = "/home/mehboob/poridhi-codes/cls-02-node-js-project/cutetube/src"

input_file = f"{home_path}/raw-videos/rain-bg-vid-sound.mp4"
output_dir = f"{home_path}/raw-videos/drm/new"
base_url = "https://cdn.algocode.site/"

success, key_id = run_shaka_packager(input_file, output_dir, base_url)


print()

if success:
    print(f"Processing completed successfully. Key ID: {key_id}")
else:
    print("Processing failed.")
