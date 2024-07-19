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
        # Define the message
        message = {
            "topic": "print_topic",
            "message": {"text": "Hello, World!"}
        }
        # Publish the message to the NSQ topic
        publish_message(message["topic"], json.dumps(message["message"]))
        return {"status": "Message published to print_topic and will be processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
