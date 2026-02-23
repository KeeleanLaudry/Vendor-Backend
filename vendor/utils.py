import os
import requests

def send_whatsapp_otp(phone_number, otp):
    url = f"https://graph.facebook.com/v22.0/{os.getenv('WHATSAPP_PHONE_NUMBER_ID')}/messages"

    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number.replace("+", ""),
        "type": "template",
        "template": {
            "name": os.getenv("WHATSAPP_TEMPLATE"),  # otp_keelean
            "language": {"code": "en_US"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        { "type": "text", "text": otp }
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        { "type": "text", "text": "login123" }  # MUST be <15 chars
                    ]
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("\n📨 WHATSAPP API RESPONSE:", response.status_code, response.text)
    return response.json()
