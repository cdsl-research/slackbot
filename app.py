from datetime import datetime
import os
import random
import re
import json

from slack_bolt import App

import google_calendar
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
            ]
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
            ]
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
                ]
            )


@app.message("hello")
def message_hello(message, say):
    say(f"Hey there <@{message['user']}>!")


def _payload_wrapper(_items):
    return [
        {
            "text": {
                "type": "plain_text",
                "text": f"{label}",
                "emoji": True
            },
            "value": value
        } for label, value in _items
    ]


def fmt_dt(_dt: datetime):
    return _dt.strftime(r"%m/%d %H:%M")


# 起点) [1] 書き込みに曜日や日付を含む文字列が含まれる
@app.message(re.compile(r"(?:.曜|明後|明|\d+)日"))
def schdule_register_message(body, respond):
    raw_message = body["event"]["text"]
    datetime_ranges = parser_datetime.parser_datetime(raw_message)
    schdule_candidates = []
    for dt_begin, dt_end in datetime_ranges:
        option_label = f"{fmt_dt(dt_begin)} - {fmt_dt(dt_end)}"
        option_value = json.dumps({
            "begin_datetime_unix": int(dt_begin.timestamp()),
            "end_datetime_unix": int(dt_end.timestamp()),
        })
        schdule_candidates.append((option_label, option_value))
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


# 起点) [1] メッセージからサブメニュー経由でのBot呼び出し
@ app.shortcut("schdule-register-shortcut")
def schdule_register_shortcut(body, ack, respond):
    assert body.get("response_url") is not None
    ack()
    try:
        raw_message = body["message"]["text"]
    except Exception:
        return
    datetime_ranges = parser_datetime.parser_datetime(raw_message)
    schdule_candidates = []
    for dt_begin, dt_end in datetime_ranges:
        option_label = f"{fmt_dt(dt_begin)} - {fmt_dt(dt_end)}"
        option_value = json.dumps({
            "begin_datetime_unix": int(dt_begin.timestamp()),
            "end_datetime_unix": int(dt_end.timestamp()),
        })
        schdule_candidates.append((option_label, option_value))
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


# [2] Botの提示したスケジュール候補が選択
@ app.action("schdule-title-select")
def schdule_title_action(body, ack, respond, action):
    assert body.get("response_url") is not None
    ack()

    try:
        selected_value = json.loads(action["selected_option"]["value"])
        # selected_label = action["selected_option"]["text"]["text"]
        user_id = body["user"]["id"]
    except Exception:
        respond(f"Error {body}")
        return

    # resolve user_id into user_name
    students = member_list.get_members()
    result = list(filter(lambda x: x["uid"] == user_id, students.values()))
    user_name = result[0]["real_name"]
    # user_email = result[0]["email"]

    # Pickup KANJI from username
    p = re.compile(r"[一-鿐]")
    kanji_name = "".join(p.findall(user_name))
    if len(kanji_name) > 0:
        user_name = kanji_name

    # Set schdule title
    schdule_title_candidates = (
        f"補講({user_name})",
        f"個別面談({user_name})",
        f"卒業課題MTG({user_name})",
        f"創成課題MTG({user_name})",
        f"論文チェック({user_name})",
        f"勉強会({user_name})"
    )
    _schdule_title_candidates = []
    for schdule_title in schdule_title_candidates:
        schdule_value = json.dumps({
            "title": schdule_title,
            # "author": user_email,
            "begin_datetime_unix": selected_value["begin_datetime_unix"],
            "end_datetime_unix": selected_value["end_datetime_unix"]
        })
        _schdule_title_candidates.append((schdule_title, schdule_value))
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
                    "options": _payload_wrapper(_schdule_title_candidates),
                    "action_id": "schdule-done"
                }
            }
        ]
    )


# [3] Botの予定タイトル名が選択
@ app.action("schdule-done")
def schdule_done_action(ack, body, respond, action):
    assert body.get("response_url") is not None
    ack()

    # Parse received values
    selected_value = json.loads(action["selected_option"]["value"])
    schdule_title = selected_value["title"]
    # schdule_user = selected_value["author"]
    _schdule_begin = selected_value["begin_datetime_unix"]
    _schdule_end = selected_value["end_datetime_unix"]
    schdule_begin = datetime.fromtimestamp(int(_schdule_begin))
    schdule_end = datetime.fromtimestamp(int(_schdule_end))

    # Add google calendar
    schdule_url = google_calendar.add(
        title=schdule_title,
        begin_date=schdule_begin,
        end_date=schdule_end,
        # user_email=schdule_user
    )

    respond(
        text="Schdule created",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Googleカレンダに次の予定を追加しました．"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f":pencil:*Title:*\n{schdule_title}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": (f":calendar:*Date:*\n{fmt_dt(schdule_begin)}"
                                 f" - {fmt_dt(schdule_end)}"),
                    },
                    {
                        "type": "mrkdwn",
                        "text": f":earth_asia:*Link:*\n<{schdule_url}|Google Calendar>"
                    }
                ]
            }
        ]
    )

    """
    {
        "type": "mrkdwn",
        "text": f":student:*Participans:*\n{schdule_user}"
    },
    """


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
