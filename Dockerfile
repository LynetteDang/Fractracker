# Retrieve Python version
FROM python:3.9-slim-bullseye

# Ensure Python output is viewable in real time and not buffered
ENV PYTHONUNBUFFERED=1

# Install wget to set up the PPA (Personal Package Archives), 
# xvfb to have a virtual screen, and unzip to install the
# Chromedriver, among other packages
RUN apt-get update -y && apt-get install -y wget xvfb unzip make gnupg curl apt-transport-https
RUN apt-get update

# Set up the Chrome PPA
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Update the package list and install chrome
RUN apt-get update -y
RUN apt-get install -y google-chrome-stable

# Set up Chromedriver environment variables
ENV CHROMEDRIVER_VERSION 99.0.4844.51
ENV CHROMEDRIVER_DIR /usr/bin

# Install Chromedriver
RUN mkdir -p $CHROMEDRIVER_DIR
RUN wget -q --continue -P $CHROMEDRIVER_DIR "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
RUN unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR

# Create new working directory within container for source code
WORKDIR /fractracker-complaints

# Copy requirements file and install packages
COPY ./requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy remaining source code
COPY . /fractracker-complaints

# Expose port for Flask app
EXPOSE 8080

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
ARG PROD_ENV
ARG PORT
CMD bash ./run_server.sh $PROD_ENV $PORT
