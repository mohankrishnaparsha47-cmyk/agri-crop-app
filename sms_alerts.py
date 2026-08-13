"""
SMS Irrigation Alerts module (optional feature).

Uses Twilio to send SMS alerts to farmers when irrigation is due, even if
they don't open the app. Requires a free Twilio trial account.

SETUP TO GO LIVE:
1. Sign up free at https://www.twilio.com/try-twilio (free trial credit given)
2. Get your Account SID, Auth Token, and a Twilio phone number from the console
3. Set these as environment variables before running the app:
     export TWILIO_ACCOUNT_SID="your_sid"
     export TWILIO_AUTH_TOKEN="your_token"
     export TWILIO_PHONE_NUMBER="+1xxxxxxxxxx"
4. Install the SDK: pip install twilio
5. Farmer's phone number (stored at registration) will then receive real SMS.

Without these env variables configured, send_irrigation_sms() safely no-ops
and just logs what WOULD have been sent - so the rest of the app keeps
working normally in demo/offline mode.
"""

import os


def send_irrigation_sms(phone_number, crop_name, growth_stage, water_mm):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_PHONE_NUMBER")

    message_body = (
        f"Smart Farmer Assistant Alert: Your {crop_name} crop needs irrigation "
        f"now ({growth_stage} stage, ~{water_mm}mm water). Please irrigate soon."
    )

    if not (account_sid and auth_token and from_number):
        print(f"[SMS DEMO MODE] Would send to {phone_number}: {message_body}")
        return {"sent": False, "demo": True, "message": message_body}

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        # Twilio requires E.164 format; assume Indian numbers if no country code
        to_number = phone_number if phone_number.startswith("+") else f"+91{phone_number}"
        client.messages.create(body=message_body, from_=from_number, to=to_number)
        return {"sent": True, "demo": False, "message": message_body}
    except Exception as e:
        print(f"[SMS ERROR] {e}")
        return {"sent": False, "demo": False, "error": str(e)}
