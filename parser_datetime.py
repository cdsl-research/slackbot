import re
from datetime import datetime as dt


def parser_datetime(text: str):
    table = str.maketrans('：０１２３４５６７８９～　（）', ':0123456789- ()')
    fmt_txt = text.translate(table).replace(" ", "")

    # 時間をさがす(JP)
    # raw_times = re.findall(
    #    r'(?:2[0-3]|(?:0?|1)\d)時(?:[0-5]\d)?分', fmt_txt)

    # 時間をさがす(US)
    raw_times = re.findall(
        r'(?:2[0-3]|(?:0?|1)\d):[0-5]\d\-(?:2[0-3]|[0-1]?\d):[0-5]\d', fmt_txt)
    time_pairs = []
    for rt in raw_times:
        t_begin, t_end = rt.split("-")
        time_pairs.append((t_begin, t_end))

    # 日付をさがす
    month_day = re.findall(r"(?:(?P<month>\d+)月)?(?P<day>\d+)日",
                           fmt_txt)
    date_paris = []
    for md in month_day:
        if not md[0]:  # 月がない
            _month = int(dt.now().month)
        else:
            _month = int(md[0])
        if not md[1]:  # 日がない
            _day = int(dt.now().day)
        else:
            _day = int(md[1])
        # 現在の日より小さい && 月が未セット
        if dt.now().day > _day and not md[0]:
            _month = (_month + 1) // 13 + (_month + 1) % 13
        date_paris.append((_month, _day))

    # (?:.曜|明後|明|\d+)日
    # (?:[月火水木金土日]曜日?)
    return {
        "time": time_pairs,
        "date": date_paris,
    }


def test():
    test_patterns = (
        {
            "in": ("A2の皆様へ\n金曜日のテーマ決めにあたり、1度IoT組の方針をみんなで共有したいので"
                   "水曜日の15時頃から研究室で話し合いをしたいと考えています。30分程度です\n"
                   "申し訳ないのですが極力出席をお願いしたいので、”出れない方”は"
                   "工科太郎まで連絡いただけると助かります。よろしくお願いします。"),
        },
        {
            "in": ("<@U01LJNE6FC7> 24日は東京での用事が確定しているので出席できません．\n"
                   "次の日の木曜日にスライドさせていただけませんでしょうか？")
        },
        {
            "in": ("<@U01LJNE6FC7> 3月15日は研究室で発表予定なので，"
                   "将来，外部発表する予定の学生は，参加するとよいでしょう．")
        },
        {
            "in": ("<@U01LJNE6FC7> <@U01LJNE6FC7> <@U01LJNE6FC7> "
                   "24日10:30-11:30で確認します．\n"
                   "<@U01LJNE6FC7> カレンダに入れてください")
        },
        {
            "in": ("<@U01LJNE6FC7> <@U01LJNE6FC7>\n"
                   "19日（金）8:50-9:30AMにて，CCEM Pre-Workshopでの"
                   "プレゼンテーションの内容をそれぞれ説明してもらえますか．\n"
                   "<@U01LJNE6FC7> Googleカレンダにスケジュールを入れてください．")
        },
        {
            "in": ("<@U01LJNE6FC7> 17日 （水）8:50-9:30で"
                   "Googleカレンダにミーティングをスケジュールしてください．\n"
                   "また，時間に遅れないように，早めにきてください．")
        },
        {
            "in": ("<@U01LJNE6FC7> <@U01LJNE6FC7> <@U01LJNE6FC7> 17日（水）"
                   "08:50-10:00で論文投稿ミーティングを"
                   "研究室でするので，集まってください．"
                   "<@U01LJNE6FC7> Googleカレンダに入れてもらえますか．")
        },
        {
            "in": ("<@U01LJNE6FC7> それでは，15日は，太郎さんが"
                   "12:00-12:30でGoogleカレンダに入れて，"
                   "Google Meetにて，次郎さん，花子さん，優香さんと"
                   "ミーティングをスケジュールしてください．"
                   "3人は，8:50-9:30AMで先にする予定です．")
        },
        {
            "in": ("<@U01LJNE6FC7> 2月10日は10:00-10:30AMで、"
                   "テクニカルレポートの内容を確認します．\n"
                   "<@U01LJNE6FC7> Googleカレンダに入れてもらえますか．")
        },
        {
            "in": ("<@U01LJNE6FC7> 9日（火曜日）16:00-16:30に，"
                   "論文をみるのでそれまでに原稿を更新してください．"
                   "また，Googleカレンダに入れておいてください．")
        },
        {
            "in": ("2月11日から3月22日")
        }
    )
    for tp in test_patterns:
        result = parser_datetime(tp["in"])
        # assert result == tp["out"]
        # print(tp["in"])
        print(result)
        print()


if __name__ == "__main__":
    test()
    # parser_datetime()
