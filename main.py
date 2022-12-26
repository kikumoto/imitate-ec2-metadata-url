import os
import logging
import json
import re
from datetime import datetime
from urllib.parse import urljoin
import requests
from flask import Flask
from flask import request

app = Flask(__name__)

url_path = os.environ.get('AWS_CONTAINER_CREDENTIALS_RELATIVE_URI')
credentials_url = urljoin('http://169.254.170.2', url_path)

pattern = re.compile(':role/(.+)$')

@app.route("/")
def index():
    app.logger.info("Accessed - Imitate EC2 Metadata URL")
    return "Imitate EC2 Metadata URL"

@app.route('/latest/meta-data/iam/security-credentials')
def security_credentials():
    app.logger.info("security_credentials")

    m = pattern.search(get_credentials()['RoleArn'])
    if m:
        return m.group(1)
    return ''

@app.route('/latest/meta-data/iam/security-credentials/<role>')
def security_credentials_of(role):
    app.logger.info(f"security_credentials_of {role}")

    creds = get_credentials()
    today = datetime.now()

    ret = {
        'Code': 'Success',
        'LastUpdated': today.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'Type': 'AWS-HMAC',
        'AccessKeyId': creds['AccessKeyId'],
        'SecretAccessKey': creds['SecretAccessKey'],
        'Token': creds['Token'],
        'Expiration': creds['Expiration'],        
    }
    return json.dumps(ret)

def get_credentials():
    return requests.get(credentials_url, timeout=10).json()


if __name__ != '__main__':
    # if we are not running directly, we set the loggers
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)

