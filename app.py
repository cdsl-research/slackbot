import os
import random
import re
import json

from slack_bolt import App

import member_list
import parser_datetime
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
    # print(tokenized_message)

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
                        "text": chose_result["text"]
                    },
                    "block_id": "image",
                    "image_url": chose_result["image"],
                    "alt_text": "Image " + chose_result["text"]
                }
            ],
        )
    elif tokenized_message_types == ["USERNAME", "GAKUSEKI", "STUDENT_ID"]:
        students = member_list.get_members()
        student_id = tokenized_message[2].value
        the_student = students.get(student_id)
        if the_student is None:
            say("Not found.")
        else:
            s_email = the_student["email"]
            s_real_name = the_student["real_name"]
            say(
                blocks=[
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f":e-mail:*Email:*\n{s_email}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f":pencil:*Real Name:*\n{s_real_name}",
                            }
                        ]
                    }
                ],
            )


@app.message("hello")
def message_hello(message, say):
    say(f"Hey there <@{message['user']}>!")


# 予定の追加候補を提示
@app.message(re.compile(r"(?:.曜|明後|明|\d+)日"))
def handle_add_calendar(body, say):
    raw_message = body["event"]["text"]
    datetime_ranges = parser_datetime.parser_datetime(raw_message)
    schdule_candidates = [f"{dt_begin} - {dt_end}" for dt_begin,
                          dt_end in datetime_ranges]

    def _payload_wrapper(titles):
        return [
            {
                "text": {
                    "type": "plain_text",
                    "text": f"{title}",
                    "emoji": True
                },
                "value": title
            } for title in titles
        ]
    say(
        text="Schdule candidates display",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "BotからGoogleカレンダーに予定を追加できます．"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "予定の日時を選んでください．"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "日時の候補",
                                "emoji": True
                    },
                    "options": _payload_wrapper(schdule_candidates),
                    "action_id": "schdule_button_click"
                }
            }
        ]
    )


"""
{
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": "Test block with users select"
    },
    "accessory": {
        "type": "users_select",
        "placeholder": {
            "type": "plain_text",
            "text": "Select a user",
            "emoji": True
        },
        "action_id": "users_select-action"
    }
},
"""

# Botの提示したスケジュール候補を選択


@app.action("schdule_button_click")
def action_schdule_button_click(body, ack, respond, action):
    assert body.get("response_url") is not None
    ack()
    selected_value = action.get("value")
    respond(f"<@{body['user']['id']}>次の予定を追加しました．\n{selected_value}")


# メッセージからサブメニュー経由でのBot呼び出し
@app.shortcut("schdule_register_button_click")
def action_schdule_rester_button_click(body, ack):
    assert body.get("response_url") is not None
    ack()


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
