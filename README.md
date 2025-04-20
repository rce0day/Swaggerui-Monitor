# API Endpoint Monitor

A lightweight Python tool that monitors Swagger/OpenAPI-enabled APIs for endpoint changes and sends notifications to Discord when changes are detected.

## Overview

This tool continuously monitors specified API endpoints by:
1. Fetching Swagger/OpenAPI specifications from the target APIs
2. Extracting endpoint information from the specifications
3. Detecting changes in the endpoints over time
4. Sending detailed change notifications to a Discord webhook

## Features

- **Automatic API Specification Parsing**: Extracts Swagger specifications from JavaScript initialization files
- **Detailed Change Detection**: Identifies newly added and removed API endpoints
- **Real-time Notifications**: Sends formatted diff reports to Discord
- **Multiple API Support**: Monitors any number of Swagger/OpenAPI-enabled APIs simultaneously
- **Configurable Monitoring**: Adjustable check intervals and notification settings

## Requirements

- Python 3.6+
- `requests` library

## Configuration

Edit the `monit.py` file to configure the following:

```python
urls = [
    "https://example.com/api/swagger-ui-init.js",
    # Add additional URLs to monitor
]

webhook_url = "YOUR_DISCORD_WEBHOOK_URL"  # Replace with your Discord webhook URL
check_interval = 300  # Time in seconds between checks (default: 5 minutes)
```

### Discord Webhook Setup

1. In your Discord server, go to Server Settings > Integrations > Webhooks
2. Create a new webhook and copy the webhook URL
3. Paste the URL into the `webhook_url` variable in the script

## Usage

Run the script to start monitoring:

```bash
python monit.py
```

The script will:
1. Initialize by fetching the current state of all monitored APIs
2. Check for changes at the specified interval
3. Send Discord notifications when endpoints are added or removed

Consider using a process manager like PM2 or a systemd service to keep the script running permanently.

## Notification Format

When changes are detected, a Discord message will be sent with a formatted diff:

```diff
Changes detected at https://example.com/api/swagger-ui-init.js!
NEW ENDPOINTS:
+ GET /api/v1/new-resource (query:param1)
+ POST /api/v1/users

REMOVED ENDPOINTS:
- DELETE /api/v1/deprecated-endpoint
```

## How It Works

1. The script extracts Swagger specifications from the target URLs
2. It parses the specifications to build a list of available endpoints with their HTTP methods and parameters
3. On each check, it compares the current endpoints with previously saved ones
4. If differences are detected, it generates a detailed diff and sends it via Discord webhook