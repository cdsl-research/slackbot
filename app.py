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


# 起点) [1] 書き込みに曜日や日付を含む文字列が含まれる
@app.message(re.compile(r"(?:.曜|明後|明|\d+)日"))
def schdule_register_message(body, say):
    raw_message = body["event"]["text"]
    datetime_ranges = parser_datetime.parser_datetime(raw_message)
    schdule_candidates = [f"{dt_begin} - {dt_end}" for dt_begin,
                          dt_end in datetime_ranges]
    say(
        text="Schdule candidates select",
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
                    "action_id": "schdule-title-select"
                }
            }
        ]
    )


# 起点) [1] メッセージからサブメニュー経由でのBot呼び出し
@app.shortcut("schdule-register-shortcut")
def schdule_register_shortcut(body, ack, respond):
    assert body.get("response_url") is not None
    ack()
    try:
        raw_message = body["message"]["text"]
    except Exception:
        return
    datetime_ranges = parser_datetime.parser_datetime(raw_message)
    schdule_candidates = [f"{dt_begin} - {dt_end}" for dt_begin,
                          dt_end in datetime_ranges]
    respond(
        text="Schdule candidates select",
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
                    "action_id": "schdule-title-select"
                }
            }
        ]
    )


"""
{
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": "会議の参加者"
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


# [2] Botの提示したスケジュール候補が選択
@app.action("schdule-title-select")
def schdule_title_action(body, ack, respond, action):
    assert body.get("response_url") is not None
    ack()
    try:
        # selected_value = action["selected_option"]["value"]
        # selected_label = action["selected_option"]["text"]["text"]
        user_id = body["user"]["id"]
    except Exception:
        respond(f"Error {body}")
        return
    # resolve user_id into user_name
    students = member_list.get_members()
    result = list(filter(lambda x: x["uid"] == user_id, students.values()))
    # Pickup 漢字
    user_name = result[0]["real_name"]
    import regex
    p = regex.compile(r'[\p{Script=Han}]')
    _user_name = "".join(p.findall(user_name))
    schdule_title_candidates = (
        f"補講({_user_name})",
        f"個別面談({_user_name})",
        f"卒業課題MTG({_user_name})",
        f"創成課題MTG({_user_name})",
        f"論文チェック({_user_name})",
        f"勉強会({_user_name})"
    )
    respond(
        text="Schdule title select",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "予定のタイトルを選んでください．"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "タイトル名",
                                "emoji": True
                    },
                    "options": _payload_wrapper(schdule_title_candidates),
                    "action_id": "schdule-done"
                }
            }
        ]
    )


# [3] Botの予定タイトル名が選択
@app.action("schdule-done")
def schdule_done_action(ack, body, respond, action):
    assert body.get("response_url") is not None
    ack()
    # selected_value = action["selected_option"]["value"]
    selected_label = action["selected_option"]["text"]["text"]
    respond(f"{selected_label}が選ばれました.")


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
