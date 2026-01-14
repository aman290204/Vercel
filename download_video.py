"""
Simple Classplus Video Downloader
Downloads video from contentId URL using local API
"""

import requests
import urllib.parse
import subprocess
import os
import sys

def download_video(content_url, output_name="Polity_Part_1"):
    """Sign URL and download video"""
    
    # Local API endpoint
    api_base = "http://127.0.0.1:5000/ITsGOLU_OFFICIAL?url="
    
    print(f"[1/3] Getting signed URL for: {content_url[:60]}...")
    
    try:
        # Get signed URL from local API
        encoded_url = urllib.parse.quote(content_url, safe='')
        response = requests.get(api_base + encoded_url, timeout=120)
        data = response.json()
        
        if not data.get('success'):
            print(f"Error: {data.get('error', 'Unknown error')}")
            return None
            
        signed_url = data.get('url')
        print(f"[2/3] Got signed URL successfully!")
        print(f"Signed URL: {signed_url[:100]}...")
        
        # Download with yt-dlp
        output_file = f"{output_name}.mp4"
        print(f"\n[3/3] Downloading video to: {output_file}")
        
        cmd = [
            'yt-dlp',
            signed_url,
            '-o', output_file,
            '--no-check-certificates',
            '-f', 'best',
            '--external-downloader', 'aria2c',
            '--downloader-args', 'aria2c:-x 16 -j 16'
        ]
        
        result = subprocess.run(cmd)
        
        if os.path.exists(output_file):
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"\n✅ Download complete! File: {output_file} ({size_mb:.2f} MB)")
            return output_file
        else:
            # Check for other extensions
            for ext in ['.mkv', '.webm', '.mp4.webm']:
                alt_file = output_name + ext
                if os.path.exists(alt_file):
                    size_mb = os.path.getsize(alt_file) / (1024 * 1024)
                    print(f"\n✅ Download complete! File: {alt_file} ({size_mb:.2f} MB)")
                    return alt_file
            print("❌ Download failed - file not found")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Error: API request timed out")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


if __name__ == "__main__":
    # Your contentId URL
    VIDEO_URL = "https://contentId=U2FsdGVkX19uuu8KpEjnA76X1DL5PdPvk4ivXbc6E2ssd/jw9LBAusQ/H3O/1UL3.m3u8"
    OUTPUT_NAME = "Polity_Part_1"
    
    if len(sys.argv) > 1:
        VIDEO_URL = sys.argv[1]
    if len(sys.argv) > 2:
        OUTPUT_NAME = sys.argv[2]
    
    print("=" * 60)
    print("Classplus Video Downloader")
    print("=" * 60)
    print()
    
    result = download_video(VIDEO_URL, OUTPUT_NAME)
    
    if result:
        print(f"\n📁 Video saved to: {os.path.abspath(result)}")
    else:
        print("\n❌ Download failed!")
