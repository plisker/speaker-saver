# SpeakerSaver

## Overview

**SpeakerSaver** is a Python-based solution designed to automatically manage and control your powered speakers connected via a smart plug. The primary goal is to ensure your speakers are turned off when not in use, specifically when no music has been played for a certain period or when the connected TV is off. This project also provides health monitoring, allowing you to check the status of the system.

This project is heavily customized for my own personal setup. However, it should be easy for anyone to fork this repository and modify the controllers for their own need.

## Features

- Automatically turns off speakers if no music is playing on Spotify or the TV is off.
- Integrates with Kasa smart plugs to control the power state of the speakers and connected audio mixer.
- Includes a health check endpoint to monitor the status of the running service.
- Logs system activities, with automatic log rotation to prevent log file overflow.
- Presents a UI for easily turning speakers on or off, as well as viewing current state of the system.

## Setup and Installation

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/speakersaver.git
cd speakersaver
```

### 2. Set Up the Python Environment

Create a virtual environment and install the required dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Setup Script

Run the setup script to configure the environment variables. This script will prompt you to input the necessary details, such as your Spotify `CLIENT_ID`, `CLIENT_SECRET`, and the IP addresses of your speakers and TV:

```bash
python setup_env.py
```

This script will generate a `.env` file with your configurations.

### 4. Authorize Spotify Access

The first time you run the `api.py` script, you'll need to authorize your Spotify app. Start the Quart server:

```bash
python -m src.api
```

Navigate to the `/authorize` endpoint in your browser to complete the Spotify authorization process. For example, if you're running the Quart server locally, visit `http://localhost:8888/authorize`.

## Running the Project

### 1. Running Locally

To start the app, including the monitoring script and the Quart server:

```bash
python -m src.api
```

### 2. Deploying to Raspberry Pi

#### Step 1: Transfer the Project to Raspberry Pi

Use `scp` to copy the entire project directory to your Raspberry Pi:

```bash
scp -r /path/to/speakersaver pi@<raspberry_pi_ip>:/home/pi/speakersaver
```

Alternatively, clone the git repository from inside your Raspberry Pi.

#### Step 2: Set Up the Environment on Raspberry Pi

SSH into your Raspberry Pi and navigate to the project directory:

```bash
ssh pi@<raspberry_pi_ip>
cd /home/pi/speakersaver
```

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
```

Run the setup script:

```bash
python3 setup_env.py
```

#### Step 3: Configure the Service to Run on Startup

##### Step 1: Create a `start_services.sh` script to run your project

1. Create script file:

```bash
sudo nano ~/start_services.sh
```

2. Add the following script:

```bash
#!/bin/bash

echo "Starting speaker saver service"
sleep 10

echo "Starting virtual environment"
cd /home/plisker/speaker-saver
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-rpi.txt
echo "Virtual environment is ready and dependencies are installed"

env > /home/plisker/speaker-saver/script_env.txt

# Run api and main scripts
python -m src.api &
API_PID=$!
echo "API server script started with PID: $API_PID"

wait $API_PID
```

##### Step 2: Create a `systemd` service to start your project automatically on boot

1. Create a service file:

```bash
sudo nano /etc/systemd/system/speaker-saver.service
```

2. Add the following configuration, making sure to change your paths as necessary:

```ini
[Unit]
Description=Speaker Saver Service
After=network.target

[Service]
Type=simple
ExecStart=/home/plisker/start_services.sh
WorkingDirectory=/home/plisker/speaker-saver
StandardOutput=inherit
StandardError=inherit
User=plisker

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl enable speaker-saver.service
sudo systemctl start speaker-saver.service
```

## Debugging

If, on the Raspberry Pi, you get an error about the `add_edge_detection`, you [may need](https://forums.raspberrypi.com/viewtopic.php?p=2230294&sid=ed8d0635e8e6760b1919468cb751a5e1#p2230294) to run this after activating the venv:

```bash
sudo apt remove python3-rpi.gpio
```

## Health Monitoring

SpeakerSaver logs its health status to `health.log` and makes this information available through an HTTP endpoint exposed by the Quart server. You can monitor the system’s health by visiting the `/health` endpoint provided by the Quart server and a simple log in the `/logs` endpoint.

You can control the speakers and view the state of the system at the root `/` endpoint.

## Port Forwarding

If you need to access the endpoints on your Raspberry Pi from your local computer, you can set up port forwarding. Add the following configuration to your `~/.ssh/config` file:

```ini
Host raspberrypi
    HostName <raspberrypi-host>
    User <raspberrypi-username>
    LocalForward 8888 127.0.0.1:8888
```

After running `ssh raspberrypi`, you will be able to access the endpoints on your computer by navigating to `http://localhost:8888`. For example, the `/health` endpoint will be [`http://localhost:8888/health`](http://localhost:8888/health).

Please note that the `HostName` may differ depending on your Raspberry Pi's configuration.
