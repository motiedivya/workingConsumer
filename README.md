
# NSQ with FastAPI and Supervisor

This guide covers the setup of NSQ, a FastAPI application to publish messages, and a consumer to process these messages, all managed by Supervisor. The consumer will print messages to the console and acknowledge them.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup NSQ Services](#setup-nsq-services)
3. [Create and Configure FastAPI Application](#create-and-configure-fastapi-application)
4. [Create and Configure NSQ Consumer](#create-and-configure-nsq-consumer)
5. [Manage Consumer with Supervisor](#manage-consumer-with-supervisor)
6. [Testing the Setup](#testing-the-setup)
7. [Verification and Troubleshooting](#verification-and-troubleshooting)

## Prerequisites

- Python 3.x
- pip (Python package installer)
- Supervisor
- NSQ binaries (`nsqlookupd`, `nsqd`, `nsqadmin`)

## Setup NSQ Services

1. **Download and Install NSQ:**

   Follow the instructions from the [NSQ official website](https://nsq.io/deployment/installing.html) to download and install the NSQ binaries.

2. **Start NSQ Services:**

   Open three terminal windows and start the following services:

   **nsqlookupd:**

   ```bash
   nsqlookupd
   ```

   **nsqd:**

   ```bash
   nsqd --lookupd-tcp-address=127.0.0.1:4200
   ```

   **nsqadmin:**

   ```bash
   nsqadmin --lookupd-http-address=127.0.0.1:4201
   ```

   Ensure the services are running on the correct ports.

## Create and Configure FastAPI Application

1. **Install Required Packages:**

   ```bash
   pip install fastapi uvicorn requests
   ```

2. **Create `app.py`:**

   ```python
   from fastapi import FastAPI, HTTPException
   from pydantic import BaseModel
   import requests
   import json

   app = FastAPI()

   NSQD_HTTP_ADDRESS = 'http://127.0.0.1:4211'  # Adjust this to your nsqd HTTP port

   class Message(BaseModel):
       topic: str
       message: dict

   def publish_message(topic: str, message: str):
       url = f"{NSQD_HTTP_ADDRESS}/pub?topic={topic}"
       response = requests.post(url, data=message)
       if response.status_code != 200:
           raise Exception(f"Failed to publish message: {response.text}")

   @app.post("/publish/")
   async def publish_to_queue(msg: Message):
       try:
           publish_message(msg.topic, json.dumps(msg.message))
           return {"status": "Message published"}
       except Exception as e:
           raise HTTPException(status_code=500, detail=str(e))

   @app.get("/print_route/")
   async def print_route():
       try:
           message = {
               "topic": "print_topic",
               "message": {"text": "Hello, World!"}
           }
           publish_message(message["topic"], json.dumps(message["message"]))
           return {"status": "Message published to print_topic and will be processed"}
       except Exception as e:
           raise HTTPException(status_code=500, detail=str(e))

   if __name__ == '__main__':
       import uvicorn
       uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
   ```

3. **Run the FastAPI Application:**

   ```bash
   python3 app.py
   ```

## Create and Configure NSQ Consumer

1. **Install Required Packages:**

   ```bash
   pip install nsq tornado
   ```

2. **Create `consumer.py`:**

   ```python
   import nsq
   import tornado.ioloop

   def print_handler(message):
       data = message.body.decode('utf-8')
       print(f"Processing message: {data}")
       message.finish()

   def run():
       reader = nsq.Reader(
           message_handler=print_handler,
           lookupd_http_addresses=['http://127.0.0.1:4201'],  # Adjust this to your nsqlookupd HTTP port
           topic='print_topic',
           channel='print_channel',
           max_in_flight=9
       )
       nsq.run()

   if __name__ == '__main__':
       run()
   ```

## Manage Consumer with Supervisor

1. **Create Supervisor Configuration:**

   **/etc/supervisor/conf.d/consumer.conf:**

   ```ini
   [program:nsq_consumer]
   command=/usr/bin/python3 /home/neural/consumer.py
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/nsq_consumer.err.log
   stdout_logfile=/var/log/nsq_consumer.out.log
   ```

2. **Reload Supervisor:**

   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start nsq_consumer
   ```

## Testing the Setup

1. **Start FastAPI Server:**

   ```bash
   python3 app.py
   ```

2. **Publish Messages Using `curl`:**

   ```bash
   curl -X POST "http://127.0.0.1:8000/publish/" -H "Content-Type: application/json" -d '{"topic": "print_topic", "message": {"key": "value"}}'
   ```

3. **Access the Print Route:**

   ```bash
   curl http://127.0.0.1:8000/print_route/
   ```

## Verification and Troubleshooting

1. **Check Consumer Logs:**

   ```bash
   tail -f /var/log/nsq_consumer.out.log
   ```

   Ensure you see logs indicating messages are being processed.

2. **Verify Supervisor Status:**

   ```bash
   sudo supervisorctl status nsq_consumer
   ```

   Ensure the consumer is running without errors.

3. **Check NSQ Admin:**

   Open `http://127.0.0.1:4213` in your web browser to monitor NSQ topics, channels, and nodes.

By following this guide, you should have a fully functional NSQ setup with FastAPI publishing messages and a consumer processing them, all managed by Supervisor. If you encounter any issues, refer to the logs and the NSQ admin interface for troubleshooting.