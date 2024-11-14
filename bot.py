import os
import requests
from bs4 import BeautifulSoup
import telepot
from flask import Flask, request, jsonify
import re

# Initialize the bot with your token
bot_token = '7828618514:AAGbumaaNSLyqNn1NbtJbIJ7j0u8RS-a5kw'  # Your bot token
bot = telepot.Bot(bot_token)

# Create a Flask app
app = Flask(__name__)

# Define your Render app URL here
WEBHOOK_URL = f"https://gatewaychk.onrender.com/{bot_token}"  # Your Render app URL

# Helper functions
def format_url(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        return 'http://' + url
    return url

def check_site_status(url):
    try:
        response = requests.get(url, timeout=5)
        return response, None
    except requests.RequestException as e:
        return None, f"Error: {e}"

def check_cloudflare(response):
    return 'cloudflare' in response.headers.get('Server', '').lower()

def check_captcha(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    return bool(soup.find_all(string=re.compile(r'captcha', re.I)))

def check_payment_gateway(response):
    text = response.text.lower()
    gateways = {
        'stripe': 'Stripe',
        'braintree': 'Braintree',
        'paypal': 'PayPal',
        'mastercard': 'Mastercard',
        'visa': 'Visa'
    }
    detected_gateways = [name for keyword, name in gateways.items() if keyword in text]
    return ', '.join(detected_gateways) if detected_gateways else 'Unknown'

def create_site_report(site):
    formatted_site = format_url(site)
    response, status_message = check_site_status(formatted_site)
    
    if response:
        cloudflare = check_cloudflare(response)
        captcha = check_captcha(response)
        gateway = check_payment_gateway(response)
        
        cloudflare_status = 'Yes 😔' if cloudflare else 'No 🔥'
        captcha_status = 'Yes 😔' if captcha else 'No 🔥'
        overall_status = 'Good 🔥' if not cloudflare and not captcha else 'Not good 😔'
        
        return (f"Gateways Fetched Successfully ✅\n"
                f"━━━━━━━━━━━━━━\n"
                f"➔ Website ⋙ ({site})\n"
                f"➔ Gateways ⋙ ({gateway})\n"
                f"➔ Captcha ⋙ ({captcha_status})\n"
                f"➔ Cloudflare ⋙ ({cloudflare_status})\n"
                f"➔ Status ⋙ ({overall_status})\n"
                f"\nBot by - @itsyo3")
    else:
        return f"Site: {site}\nStatus: {status_message}"

# Define command handling
def handle_message(msg):
    chat_id = msg['chat']['id']
    text = msg['text']
    print(f"Received message: {text}")  # Log the received message

    if text.startswith('/start'):
        bot.sendMessage(chat_id, f"Hello {msg['from']['first_name']}, welcome to Eon Gateway Chk bot!")
    elif text.startswith('/cmds'):
        commands = (
            "/sc <site> - Check a single site\n"
            "/msc <site1> <site2> ... <site10> - Check up to 10 sites\n"
            "/cmds - List available commands"
        )
        bot.sendMessage(chat_id, f"Available Commands:\n{commands}")
    elif text.startswith('/sc'):
        site = text.split(' ')[1] if len(text.split()) > 1 else None
        if site:
            report = create_site_report(site)
            bot.sendMessage(chat_id, report)
        else:
            bot.sendMessage(chat_id, "Please provide a website URL. Example: /sc example.com")
    elif text.startswith('/msc'):
        sites = text.split(' ')[1:]
        if len(sites) > 10:
            bot.sendMessage(chat_id, "Please provide up to 10 sites only.")
        else:
            for site in sites:
                report = create_site_report(site)
                bot.sendMessage(chat_id, report)
    else:
        bot.sendMessage(chat_id, "Unknown command. Use /cmds to list available commands.")

# Define webhook route
@app.route(f"/{bot_token}", methods=["POST"])
def receive_update():
    update = request.get_json()
    print("Received update:", update)  # Log the incoming update
    if "message" in update:
        handle_message(update["message"])
    return jsonify({"status": "ok"})

# Set webhook when starting
@app.before_first_request
def set_webhook():
    bot.setWebhook(WEBHOOK_URL)
    print("Webhook set to:", WEBHOOK_URL)  # Log when webhook is set

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
