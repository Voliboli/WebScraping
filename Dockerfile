FROM python:3.10-slim-buster

RUN pip3 install pipenv
RUN apt-get update && apt-get install -y default-jre wget gnupg curl

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome
#RUN apt-get -y update && apt-get install -y google-chrome-stable

# Download Package
ENV CHROME_VERSION 114.0.5735.90-1
ENV TEMP_DEB $(mktemp)
RUN wget -O $TEMP_DEB "https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb"
RUN apt-get install fonts-liberation libgbm1 libu2f-udev libvulkan1 xdg-utils -y
RUN dpkg -i $TEMP_DEB
RUN rm -f $TEMP_DEB
#RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb
#RUN apt-get install -y ./google-chrome-stable_${CHROME_VERSION}_amd64.deb 

# Installing Unzip
RUN apt-get install -yqq unzip

# Download the Chrome Driver
ENV CHROMEDRIVER_VERSION 114.0.5735.90
ENV CHROMEDRIVER_DIR /chromedriver
RUN mkdir $CHROMEDRIVER_DIR
RUN wget -q --continue -P $CHROMEDRIVER_DIR "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
RUN unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR
# Put Chromedriver into the PATH
ENV PATH $CHROMEDRIVER_DIR:$PATH

# Set display port as an environment variable
ENV DISPLAY=:99

ENV PROJECT_DIR /usr/src/voliboli

WORKDIR ${PROJECT_DIR}

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install

COPY . .

CMD ["pipenv", "run", "python", "main.py"]
