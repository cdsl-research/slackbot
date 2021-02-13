import os
import random
import json

from slack_bolt import App

import tokenizer

# Import the async app instead of the regular one
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

QR_BASE_URL = ("https://api.qrserver.com/v1/create-qr-code/"
               "?size=200%C3%97200&data=")


@app.event("app_mention")
def handle_mentions(body, say):
    raw_message = body["event"]["text"]
    tokenized_message = tokenizer.tokenizer(raw_message)
    tokenized_message_types = [x.type for x in tokenized_message]

    if tokenized_message_types == ["USERNAME", "QR", "URL"]:
        target_url = tokenized_message[2].value
        say(
            blocks=[
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": f"QR Code of {target_url}"
                    },
                    "block_id": f"image-{target_url}",
                    "image_url": QR_BASE_URL + target_url,
                    "alt_text": "QR Code"
                }
            ],
        )
    elif tokenized_message_types == ["USERNAME", "OMIKUJI"]:
        with open("omikuji_result.json") as f:
            omikuji_result = json.load(f)["omikuji"]
        chose_result = random.choice(omikuji_result)
        say(
            blocks=[
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": "Omikuji result " + chose_result["text"]
                    },
                    "block_id": "image",
                    "image_url": chose_result["image"],
                    "alt_text": "QR Code " + chose_result["text"]
                }
            ],
        )


@app.message("hello")
def message_hello(message, say):
    say(f"Hey there <@{message['user']}>!")


# group mension

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
