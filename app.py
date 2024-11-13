import os
from flask import Flask, request, render_template, redirect, url_for
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Make sure the file upload folder exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    bot_token = request.form.get('bot_token')
    chat_id = request.form.get('chat_id')

    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']

    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        # Save file securely
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the file
        with open(file_path, 'r') as f:
            sites = f.readlines()
            sites = [site.strip() for site in sites]

        # Now you can use your logic to check sites and send to telegram
        message = "Processing Sites..."
        # Here you would add the logic to check sites and send messages via your bot
        
        # Example: Iterate through sites and send the message (same logic as before)
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
                           f"\nBot by - @itsyo3")

                send_to_telegram(bot_token, chat_id, message)
            else:
                message = f"Site: {site}\nStatus: {status_message}"

        return render_template('index.html', message="File processed and information sent to your bot!")

    else:
        return "Invalid file format. Only .txt files are allowed.", 400

if __name__ == '__main__':
    app.run(debug=True)
