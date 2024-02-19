# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install Firefox
RUN apt-get update && apt-get install -y firefox-esr

# Install geckodriver
RUN apt-get install -y wget unzip && \
    GECKODRIVER_VERSION=$(wget https://api.github.com/repos/mozilla/geckodriver/releases/latest -O - | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/') && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -xvzf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    chmod +x geckodriver && \
    mv geckodriver /usr/local/bin/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 38570 available to the world outside this container
EXPOSE 38570

# Run LufaWeeklyDeliveryTimeMain.py when the container launches
CMD ["python", "LufaWeeklyDeliveryTimeMain.py"]