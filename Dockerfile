FROM python:3.10-slim-buster

RUN pip3 install pipenv
RUN apt-get update && apt-get install -y default-jre wget gnupg curl && rm -rf /var/lib/apt/lists/*

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome
RUN apt-get -y update && apt-get install -y google-chrome-stable

# Installing Unzip
RUN apt-get install -yqq unzip

# Download the Chrome Driver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/112.0.5615.49/chromedriver_linux64.zip

RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Set display port as an environment variable
ENV DISPLAY=:99

ENV PROJECT_DIR /usr/src/voliboli

WORKDIR ${PROJECT_DIR}

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install

COPY . .

CMD ["pipenv", "run", "python", "main.py"]
