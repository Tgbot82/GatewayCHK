import requests
from bs4 import BeautifulSoup
import telepot
from telepot.loop import MessageLoop
import re
import time

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
        'shopify': 'Shopify',
        'paypal': 'PayPal',
        'skrill': 'Skrill',
        'payoneer': 'Payoneer',
        'mastercard': 'Mastercard',
        'visa': 'Visa',
        'apple pay': 'Apple Pay',
        'google pay': 'Google Pay'
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

def handle_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        text = msg['text']
        
        # Welcome message for /start
        if text.startswith('/start'):
            bot.sendMessage(chat_id, f"Hy {msg['from']['first_name']}, welcome to Eon Gateway Chk bot!")
        
        # Commands list
        elif text.startswith('/cmds'):
            commands = (
                "/sc <site> - Check a single site\n"
                "/msc <site1> <site2> ... <site10> - Check up to 10 sites\n"
                "/cmds - List available commands"
            )
            bot.sendMessage(chat_id, f"Available Commands:\n{commands}")
        
        # Single site check command
        elif text.startswith('/sc'):
            site = text.split(' ')[1] if len(text.split()) > 1 else None
            if site:
                report = create_site_report(site)
                bot.sendMessage(chat_id, report)
            else:
                bot.sendMessage(chat_id, "Please provide a website URL. Example: /sc example.com")
        
        # Multiple sites check command
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

# Bot setup with token
bot_token = '7828618514:AAGbumaaNSLyqNn1NbtJbIJ7j0u8RS-a5kw'
bot = telepot.Bot(bot_token)

# Start the MessageLoop
MessageLoop(bot, handle_message).run_as_thread()

# Keep the program running
print("Bot is running...")
while True:
    time.sleep(10)
