from flask import Flask, request, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import re
import telepot

app = Flask(__name__)

# Define a function to check the payment gateway
def check_payment_gateway(response_text):
    text = response_text.lower()
    gateways = {
        'stripe': 'Stripe',
        'braintree': 'Braintree',
        'shopify': 'Shopify',
        'paypal': 'PayPal',
        'skrill': 'Skrill',
        'payoneer': 'Payoneer',
        'nab': 'NAB',
        'omise': 'Omise',
        'epay': 'ePay',
        'mastercard': 'Mastercard',
        'visa': 'Visa',
        'discover': 'Discover',
        'american express': 'American Express',
        'adyen': 'Adyen',
        'square': 'Square',
        'authorize.net': 'Authorize.Net',
        '2checkout': '2Checkout',
        'worldpay': 'Worldpay',
        'alipay': 'Alipay',
        'wechat pay': 'WeChat Pay',
        'unionpay': 'UnionPay',
        'apple pay': 'Apple Pay',
        'google pay': 'Google Pay',
        'amazon pay': 'Amazon Pay'
    }
    detected_gateways = [name for keyword, name in gateways.items() if keyword in text]
    return detected_gateways if detected_gateways else ['Unknown']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_sites', methods=['POST'])
def check_sites():
    urls = request.form['urls'].splitlines()
    bot_token = request.form['bot_token']
    chat_id = request.form['chat_id']
    results = []
    gateway_counts = {}

    for url in urls:
        formatted_url = 'http://' + url if not url.startswith(('http://', 'https://')) else url
        try:
            response = requests.get(formatted_url, timeout=5)
            gateways = check_payment_gateway(response.text)

            # Count gateways
            for gateway in gateways:
                gateway_counts[gateway] = gateway_counts.get(gateway, 0) + 1

            results.append({
                'site': url,
                'gateways': ', '.join(gateways),
                'status': 'Accessible'
            })

            # Optional: Send to Telegram
            bot = telepot.Bot(bot_token)
            message = f"Site: {url}\nGateways: {', '.join(gateways)}"
            bot.sendMessage(chat_id, message)

        except requests.RequestException:
            results.append({
                'site': url,
                'gateways': 'N/A',
                'status': 'Error accessing site'
            })

    return jsonify({'results': results, 'gateway_counts': gateway_counts})

if __name__ == '__main__':
    app.run(debug=True)
