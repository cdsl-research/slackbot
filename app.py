import os
import re

from slack_bolt import App

import tokenizer

# Import the async app instead of the regular one
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

QR_BASE_URL = "https://chart.apis.google.com/chart?chs=200x200&cht=qr&chl="


@app.event("app_mention")
def handle_mentions(body, say):
    raw_message = body["event"]["text"]
    tokenized_message = tokenizer(raw_message)
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
                    "block_id": "image1",
                    "image_url": QR_BASE_URL + target_url,
                    "alt_text": "QR Code"
                }
            ],
        )


@ app.message("hello")
def message_hello(message, say):
    say(f"Hey there <@{message['user']}>!")


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
