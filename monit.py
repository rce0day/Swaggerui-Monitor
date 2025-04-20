import requests
import time
import hashlib
import re
import json

urls = [
    "https://frontend-api.pump.fun/api/swagger-ui-init.js", # the js file returns the swagger spec in a json format, just replace the root url.
    "https://advanced-api.pump.fun/api/swagger-ui-init.js",
    "https://pump-fun-backend.fly.dev/api/swagger-ui-init.js",
]

webhook_url = "webhook"  # replace with your discord webhook
check_interval = 300  # time in seconds between checks

def send_discord_notification(message):
    try:
        data = {"content": message}
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord notification: {e}")

def get_page_content(url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch content from {url}: {e}")
        return None

def get_swagger_spec(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, timeout=30, headers=headers)
        if response.status_code != 200:
            return None
            
        content = response.text
        
        try:
            options_match = re.search(r'let\s+options\s*=\s*({[^;]*})', content, re.DOTALL)
            if options_match:
                options_text = options_match.group(1)
                options_text = re.sub(r'(\w+):', r'"\1":', options_text)
                options_text = re.sub(r',\s*}', '}', options_text)
                
                options = json.loads(options_text)
                if 'swaggerDoc' in options:
                    return options['swaggerDoc']
            return None
            
        except Exception:
            return None
            
    except requests.exceptions.RequestException:
        return None

def extract_endpoints(swagger_spec):
    if not swagger_spec or 'paths' not in swagger_spec:
        return set()
    
    endpoints = set()
    paths = swagger_spec.get('paths', {})
    
    for path, methods in paths.items():
        for method, details in methods.items():
            params = []
            if 'parameters' in details:
                for param in details['parameters']:
                    param_type = param.get('in', 'unknown')
                    param_name = param.get('name', 'unknown')
                    params.append(f"{param_type}:{param_name}")
            
            param_str = f" ({', '.join(params)})" if params else ""
            endpoint = f"{method.upper()} {path}{param_str}"
            endpoints.add(endpoint)
    
    return endpoints

def get_diff(old_endpoints, new_endpoints):
    old_set = set(old_endpoints)
    new_set = set(new_endpoints)
    
    added = new_set - old_set
    removed = old_set - new_set
    
    diff_lines = []
    
    if added:
        diff_lines.append("NEW ENDPOINTS:")
        for endpoint in sorted(added):
            diff_lines.append(f"+ {endpoint}")
    
    if removed:
        if added:
            diff_lines.append("")
        diff_lines.append("REMOVED ENDPOINTS:")
        for endpoint in sorted(removed):
            diff_lines.append(f"- {endpoint}")
    
    if diff_lines:
        return '\n'.join(diff_lines)
    return None

def monitor():
    try:
        last_endpoints = {}
        last_hashes = {}
        for url in urls:
            swagger_spec = get_swagger_spec(url)
            if swagger_spec:
                endpoints = extract_endpoints(swagger_spec)
                last_endpoints[url] = endpoints
                last_hashes[url] = hashlib.md5(str(endpoints).encode()).hexdigest()

        while True:
            time.sleep(check_interval)
            for url in urls:
                current_swagger_spec = get_swagger_spec(url)
                if current_swagger_spec:
                    current_endpoints = extract_endpoints(current_swagger_spec)
                    current_hash = hashlib.md5(str(current_endpoints).encode()).hexdigest()

                    if url in last_hashes and current_hash != last_hashes[url]:
                        changes = get_diff(last_endpoints[url], current_endpoints)
                        if changes:
                            message = f"Changes detected at {url}!\n```diff\n{changes}\n```"
                            send_discord_notification(message)
                        
                        last_endpoints[url] = current_endpoints
                        last_hashes[url] = current_hash

    except Exception as e:
        send_discord_notification(f"Monitoring script encountered an error: {e}")

if __name__ == "__main__":
    monitor()

