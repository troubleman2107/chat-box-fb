from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests

app = FastAPI()

VERIFY_TOKEN = "blackcat"
PAGE_ACCESS_TOKEN = "EAAkoFi3B1W8BO7PnHMvVesE4IAKh1liG69mFIb9iD6rO6tBG2LOoyL4T6IG1V1xxMhgxrka3JgZARrrud8eqq9GZAJEW6broC3c96wapZAbH7jFkJQY6amdY3EOS9izfWvQ1SPHKICHgac3ZCH5rEAk840kKguquFwkhZA0HKOyuURyOaKZCFmqK83ZAI1qhf3b"


class Message(BaseModel):
    sender_id: str
    message: str


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    if body.get("object") == "page":
        for entry in body.get("entry"):
            for messaging_event in entry.get("messaging"):
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"]["text"]
                    message = Message(sender_id=sender_id, message=message_text)
                    process_message(message)
    return "ok"


def process_message(message: Message):
    sender_id = message.sender_id
    message_text = message.message
    # Here you can implement your logic to process the received message
    # For now, let's just echo back the received message
    send_message(sender_id, message_text)


def send_message(recipient_id, message_text):
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    }
    response = requests.post(
        "https://graph.facebook.com/v12.0/me/messages",
        params=params,
        headers=headers,
        json=data
    )
    if response.status_code != 200:
        print("Failed to send message:", response.text)


@app.get("/")
async def verify_webhook(mode: str, verify_token: str):
    print(verify_token)
    if mode == "subscribe" and verify_token == VERIFY_TOKEN:
        return int(requests.query_params.get("hub.challenge"))
    else:
        raise HTTPException(status_code=403, detail="Verification token mismatch")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
