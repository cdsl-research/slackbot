import json
import os
import urllib.request


def get_members(SLACK_TOKEN: str = os.environ.get("SLACK_BOT_TOKEN"), EXCLUDE_USERS={"slackbot"}):
    SLACK_WEBHOOK = (f"https://slack.com/api/users.list?token={SLACK_TOKEN}&pretty=1",)
    assert len(SLACK_TOKEN) > 10, "Invalid Slack Token"
    response = urllib.request.urlopen(SLACK_WEBHOOK)
    content = json.loads(response.read().decode("utf8"))

    members_dict = {}
    for member in content["members"]:
        # api doc) https://api.slack.com/methods/users.list
        if member["is_bot"] or member["deleted"] or member["name"] in EXCLUDE_USERS:
            continue
        # print(member)
        uid = str(member["id"])
        name = str(member["name"])  # add oauth permission 'users:read.email'
        email = str(member["profile"].get("email"))
        if email is None:
            continue
        student_id = str(email[0:8]).upper()
        real_name = str(member.get("real_name"))
        # print('{0:<10}\t{1:<10}\t{2:<10}'.format(uid, name, real_name))
        members_dict[student_id] = {"email": email, "name": name, "uid": uid, "real_name": real_name}

    return members_dict


def main():
    _members_dict = get_members()
    with open("member_list.json", mode="w") as f:
        json.dump(_members_dict, f, ensure_ascii=False, indent=4, sort_keys=False, separators=(",", ": "))


if __name__ == "__main__":
    main()
