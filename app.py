from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import telepot
import re
import os

app = Flask(__name__)

# Configure upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt'}

# Function to check if the file is valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to read sites from a file
def read_sites(file_path):
    with open(file_path, 'r') as file:
        sites = file.readlines()
    return [site.strip() for site in sites]

# Function to format URLs
def format_url(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        return 'http://' + url
    return url

# Function to check site status
def check_site_status(url):
    try:
        response = requests.get(url, timeout=5)  # Reduced timeout to 5 seconds for faster checks
        if response.status_code == 200:
            return response, None
        else:
            return None, f"Error: Received status code {response.status_code}"
    except requests.RequestException as e:
        return None, f"Error: {e}"

# Function to check Cloudflare presence
def check_cloudflare(response):
    return 'cloudflare' in response.headers.get('Server', '').lower()

# Function to check for captcha presence
def check_captcha(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    return bool(soup.find_all(string=re.compile(r'captcha', re.I)))

# Function to check payment gateways
def check_payment_gateway(response):
    text = response.text.lower()
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
    return ', '.join(detected_gateways) if detected_gateways else 'Unknown'

# Function to send a message to Telegram bot
def send_to_telegram(bot_token, chat_id, message):
    bot = telepot.Bot(bot_token)
    try:
        bot.sendMessage(chat_id, message)
    except telepot.exception.TelegramError as e:
        print(f"Failed to send message: {e}")

# Home route (render the form)
@app.route('/')
def home():
    return render_template("index.html")

# Result route (to process the form and send response)
@app.route('/check', methods=['POST'])
def check():
    # Retrieve bot token and chat ID
    bot_token = request.form['bot_token']
    chat_id = request.form['chat_id']
    
    # Handle file upload
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file', 400
    
    if file and allowed_file(file.filename):
        # Save the file temporarily
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Read sites from the uploaded file
        sites = read_sites(filepath)

        # Process each site
        for site in sites:
            formatted_site = format_url(site)
            response, status_message = check_site_status(formatted_site)
            
            if response:
                cloudflare = check_cloudflare(response)
                captcha = check_captcha(response)
                gateway = check_payment_gateway(response)
                
                cloudflare_status = 'Yes 😔' if cloudflare else 'No 🔥'
                captcha_status = 'Yes 😔' if captcha else 'No 🔥'
                overall_status = 'Good 🔥' if not cloudflare and not captcha else 'Not good 😔'
                
                message = (f"Gateways Fetched Successfully ✅\n"
                           f"━━━━━━━━━━━━━━\n"
                           f"➔ Website ⋙ ({site})\n"
                           f"➔ Gateways ⋙ ({gateway})\n"
                           f"➔ Captcha ⋙ ({captcha_status})\n"
                           f"➔ Cloudflare ⋙ ({cloudflare_status})\n"
                           f"➔ Status ⋙ ({overall_status})\n"
                           f"\nBot by - @your_bot_username")
            else:
                message = f"Site: {site}\nStatus: {status_message}"
            
            # Send the result to the user's Telegram bot
            send_to_telegram(bot_token, chat_id, message)

        return render_template('index.html', message="Check completed! Results sent to your bot.")

    return 'File type not allowed', 400

if __name__ == '__main__':
    app.run(debug=True)
