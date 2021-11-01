'''
 The MIT License(MIT)

 Copyright(c) 2016 Copyleaks LTD (https://copyleaks.com)

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
'''

import os
import base64
import random
import tempfile
from copyleaks.copyleaks import Copyleaks, Products
from copyleaks.exceptions.command_error import CommandError
from copyleaks.models.submit.document import FileDocument, UrlDocument, OcrFileDocument
from copyleaks.models.submit.properties.scan_properties import ScanProperties
from copyleaks.models.export import *

from github import Github
# Register on https://api.copyleaks.com and grab your secret key (from the dashboard page).
EMAIL_ADDRESS = 'XXXXXXXXXXXXXX'
KEY = 'XXXXXXXXXXXXXX'
PRODUCT = Products.EDUCATION  # BUSINESSES or EDUCATION, depending on your Copyleaks account type.
g = Github("XXXXXXXXXXXXXX")

# Get auth token for copyleaks
try:
    auth_token = Copyleaks.login(EMAIL_ADDRESS, KEY)
except CommandError as ce:
    response = ce.get_response()
    print(f"An error occurred (HTTP status code {response.status_code}):")
    print(response.content)
    exit(1)

print("Logged successfully!\nToken:")
print(auth_token)

# Github API get ropeository
repo = g.get_repo("XXXXXXXXXXX")
contents = repo.get_contents("")
urls = []

ignore = ["Procfile", "bootstrap.min.js", "bootstrap.min.css",
          "materialize.min.js", "materialize.min.css", "animations.css", 
          "png", "jpg", "manage.py","custom_storages.py", "wsgi.py",
          "settings.py", "0001_initial.py", "mp4", "avi", "m4v", "mp3", 
          "stripe.js", "pdf", "xd", "wav", "jquery.min.js", "jquery-3.5.0.js",
          "jasmine.js", "jasmine-html.js", "xterm.css", "xterm.js"]

# Build list of urls of raw source code files to be scanned
while contents:
    file_content = contents.pop(0)
    if file_content.type == "dir" and file_content.name != '.vscode':
        contents.extend(repo.get_contents(file_content.path))
    else:
        if file_content.name not in ignore:
            if file_content.name.split('.')[-1] in ['html', 'css', 'js', 'py']:
                urls.append(file_content.download_url)

# Iterate over urls list and send to copyleaks for checking.
for url in urls:
    print("Submitting a new file...")
    print(url)

    scan_id = random.randint(100, 100000)  # generate a random scan id
    url_submission = UrlDocument()
    url_submission.set_url(url)
    # Once the scan completed on Copyleaks servers, we will trigger a webhook that notify you.
    # Write your public endpoint server address. If you testing it locally, make sure that this endpoint
    # is publicly available.
    scan_properties = ScanProperties('XXXXXXXXXX')
    scan_properties.set_sandbox(False)  # Turn on sandbox mode. Turn off on production.
    scan_properties.set_sensitivity_level(5)
    url_submission.set_properties(scan_properties)
    Copyleaks.submit_url(PRODUCT, auth_token, scan_id, url_submission)  # sending the submission to scanning
    print("Send to scanning")
    print("You will notify, using your webhook, once the scan was completed.")
