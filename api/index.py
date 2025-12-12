from flask import Flask, request, Response, stream_with_context, jsonify
import requests
from urllib.parse import quote

app = Flask(__name__)

# The backend service found in the codebase
KOYEB_API_URL = "https://head-micheline-botupdatevip-f1804c58.koyeb.app/get_keys"

@app.route('/extract_keys', methods=['GET'])
@app.route('/get_keys', methods=['GET'])
def extract_keys():
    """
    Proxies the key extraction request to the Koyeb API.
    Mimics the 'ItsGolu CP API' interface.
    """
    url = request.args.get('url')
    user_id = request.args.get('user_id', 'unknown')

    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    # DEBUG: Log input
    print(f"Proxying for URL: {url}")

    try:
        # Construct the target URL carefully. 
        # The backend likely triggers on the literal '@botupdatevip4u' suffix.
        # We encode the video URL to avoid query parameter confusion, assuming backend handles encoded value.
        # encoded_url = quote(url, safe=':/') # Encode but keep protocol chars? Or full encode?
        # Let's try passing it RAW first as the original python code did, but ensure requests doesn't mangle it.
        
        # Original code: f"...?url={url}@botupdatevip4u..."
        # If requests encodes the '@', it breaks.
        
        target_url = f"{KOYEB_API_URL}?url={url}@botupdatevip4u&user_id={user_id}"
        
        # Add headers required by the backend (it likely acts as a Classplus client)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://web.classplusapp.com/",
            "x-cdn-tag": "empty",
            # Add Origin just in case
            "Origin": "https://web.classplusapp.com"
        }

        response = requests.get(target_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            # Return FULL DETAILS for debugging
            return jsonify({
                "error": "Backend API Error", 
                "status": response.status_code, 
                "headers_sent": dict(response.request.headers),
                "url_requested": response.request.url,
                "details": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({"error": "Internal Proxy Error", "details": str(e)}), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    General proxy for direct file downloads (m3u8, mp4, etc.)
    Attempts to bypass 403 Forbidden by adding Classplus headers.
    """
    video_url = request.args.get('url')
    if not video_url:
        return "Missing 'url' parameter. Use /extract_keys?url=... for Classplus keys.", 400

    headers = {
        'User-Agent': 'Mobile', 
        'Referer': 'https://web.classplusapp.com/',
        'x-cdn-tag': 'empty' # Added based on codebase findings
    }

    try:
        req = requests.get(video_url, headers=headers, stream=True)
        
        if req.status_code != 200:
             return f"Error fetching video: {req.status_code}", req.status_code

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in req.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(stream_with_context(req.iter_content(chunk_size=1024)),
                        status=req.status_code,
                        headers=headers,
                        content_type=req.headers.get('content-type'))

    except Exception as e:
        return f"Internal Server Error: {str(e)}", 500

if __name__ == '__main__':
    app.run()
