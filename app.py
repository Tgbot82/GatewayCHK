from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# Function to send a message to Telegram
def send_to_telegram(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response

# Function to check payment gateways on a website
def check_payment_gateway(url):
    try:
        response = requests.get(url, timeout=5)
        text = response.text.lower()

        gateways = {
            'stripe': 'Stripe',
            'braintree': 'Braintree',
            'paypal': 'PayPal',
            'skrill': 'Skrill',
            'payoneer': 'Payoneer',
            'shopify': 'Shopify',
            'visa': 'Visa',
            'mastercard': 'Mastercard',
            'google pay': 'Google Pay',
            'apple pay': 'Apple Pay',
            'amazon pay': 'Amazon Pay'
        }

        detected_gateways = [name for keyword, name in gateways.items() if keyword in text]
        return ', '.join(detected_gateways) if detected_gateways else 'No gateways detected'

    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check_gateways')
def check_gateways():
    site = request.args.get('site')
    token = request.args.get('token')
    chat_id = request.args.get('chat_id')

    if site:
        site = site.strip()
        gateways = check_payment_gateway(site)

        # Construct message to send to Telegram
        message = f"Site: {site}\n"
        message += f"Detected Gateways: {gateways}"

        # Send the information to Telegram
        send_to_telegram(token, chat_id, message)

        return render_template('index.html', gateway=gateways, site_id=site, token=token)
    else:
        return render_template('index.html', gateway='No URL provided')

if __name__ == '__main__':
    app.run(debug=True)
