from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# Your functions for checking the site status here
# (like check_site_status, check_cloudflare, etc.)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        sites = request.form["sites"].splitlines()
        results = []
        
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
                
                results.append({
                    "site": site,
                    "gateway": gateway,
                    "captcha_status": captcha_status,
                    "cloudflare_status": cloudflare_status,
                    "overall_status": overall_status
                })
            else:
                results.append({
                    "site": site,
                    "status": status_message
                })
        return render_template("index.html", results=results)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
