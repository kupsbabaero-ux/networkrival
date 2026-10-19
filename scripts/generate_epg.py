#!/usr/bin/env python3
"""
Philippine TV EPG Generator (XMLTV)
Generates a rolling 7-day EPG with current date/time awareness.
Timezone: Asia/Manila (UTC+8)
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import gzip#!/usr/bin/env python3
"""
Philippine TV EPG Generator (XMLTV)
Generates a rolling 14-day EPG with current date/time awareness.
Timezone: Asia/Manila (UTC+8)
Densified schedules (~226+ programmes target per full run).
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import gzip
import shutil

TZ = ZoneInfo("Asia/Manila")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "epg")
XML_PATH = os.path.join(OUTPUT_DIR, "ph-tv-epg.xml")
GZ_PATH = os.path.join(OUTPUT_DIR, "ph-tv-epg.xml.gz")

CHANNELS = [
    {"id": "TV5.ph", "display-name": "TV5", "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/TV5_Logo_2021.svg/200px-TV5_Logo_2021.svg.png"},
    {"id": "Kapamilya.ph", "display-name": "Kapamilya Channel", "icon": ""},
    {"id": "ALLTV2.ph", "display-name": "ALLTV2", "icon": ""},
    {"id": "A2Z.ph", "display-name": "A2Z", "icon": ""},
    {"id": "JeepneyTV.ph", "display-name": "Jeepney TV", "icon": ""},
    {"id": "GMA.ph", "display-name": "GMA Network", "icon": ""},
    {"id": "GTV.ph", "display-name": "GTV", "icon": ""},
]

# Approximate weekly templates (hour, minute, title, duration_minutes)
# Day keys: 0=Mon ... 6=Sun
SCHEDULES = {
    "TV5.ph": {
        "weekday": [  # Mon-Fri
            (4, 30, "Mga Kwentong MX3", 60),
            (5, 30, "Frontline sa Umaga", 150),
            (8, 0, "Chibi Maruko Chan", 30),
            (8, 30, "Blockbusters sa Umaga", 120),
            (10, 30, "Frontline Express AM", 30),
            (11, 0, "Gandang Mornings with Ate Koring", 60),
            (12, 0, "Eat Bulaga!", 150),
            (14, 30, "Mommy Guard / Afternoon Series", 45),
            (15, 15, "Frontline Express PM", 45),
            (16, 0, "Suntok sa Buwan", 45),
            (16, 45, "Knight Rider", 45),
            (17, 30, "Jasmine", 30),
            (18, 0, "Frontline Pilipinas: Una sa Lahat", 30),
            (18, 30, "Frontline Pilipinas", 90),
            (20, 0, "Sigabo", 45),
            (20, 45, "Someone, Someday", 45),
            (21, 30, "The Loyalty Game: Level Up", 45),
            (22, 15, "Frontline Tonight", 30),
            (22, 45, "Cassandra: Warrior Angel", 45),
            (23, 30, "Vibe Nights / Oras ng Himala", 60),
        ],
        "saturday": [
            (7, 0, "Prinsipe Cedie", 30),
            (7, 30, "The Adventures of Tom Sawyer", 60),
            (8, 30, "Little Princess Sarah", 60),
            (9, 30, "Blockbusters sa Umaga", 115),
            (11, 25, "Eat Bulaga!", 180),
            (14, 25, "Frontline Express", 45),
            (15, 10, "Cine Cinco Hit na Hit", 110),
            (17, 0, "Frontline Pilipinas Weekend", 60),
            (18, 0, "Vibe+", 90),
            (19, 30, "Kapamilya Deal or No Deal", 60),
            (20, 30, "Maalaala Mo Kaya", 60),
            (21, 30, "Matteo G Primetime", 60),
            (22, 30, "America's Got Talent", 60),
            (23, 30, "In Touch with Dr. Charles Stanley", 30),
        ],
        "sunday": [
            (5, 30, "In Touch with Dr. Charles Stanley", 30),
            (6, 0, "Sunday Mass", 60),
            (7, 0, "Oras ng Katotohanan", 60),
            (8, 0, "Prinsipe Cedie", 60),
            (9, 0, "The Adventures of Tom Sawyer", 60),
            (10, 0, "Blockbusters sa Umaga", 120),
            (12, 0, "Vibe+ Playback", 90),
            (13, 30, "Cine Cinco Astig Sunday", 120),
            (15, 30, "Julius Babao Unplugged", 30),
            (16, 0, "Rated Korina", 60),
            (17, 0, "Frontline Pilipinas Weekend", 60),
            (18, 0, "Kapatid Mo, Idol Raffy Tulfo", 60),
            (19, 0, "ASAP XP", 105),
            (20, 45, "Kapamilya Deal or No Deal", 60),
            (21, 45, "Maalaala Mo Kaya", 60),
            (22, 45, "Kapatid Sunday Specials", 75),
        ],
    },
    "Kapamilya.ph": {
        "weekday": [
            (5, 30, "Kapamilya Daily Mass", 30),
            (6, 0, "Knowledge Channel School Anywhere", 60),
            (7, 0, "Kids / Rerun Block", 120),
            (9, 0, "Magandang Buhay", 60),
            (10, 0, "Kapamilya Blockbusters", 120),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Kapamilya Gold Drama", 90),
            (16, 0, "Kapamilya Gold Hits / Afternoon Zinema", 90),
            (17, 30, "TV Patrol Express", 15),
            (17, 45, "Minute to Win It / Goin' Bulilit", 45),
            (18, 30, "TV Patrol", 90),
            (20, 0, "Primetime Bida Drama 1", 45),
            (20, 45, "Primetime Bida Drama 2", 45),
            (21, 30, "Primetime Bida Drama 3", 45),
            (22, 15, "Primetime Bida Drama 4 / Asian Drama", 30),
            (22, 45, "The World Tonight", 30),
            (23, 15, "Movie Central Presents", 165),
        ],
        "saturday": [
            (5, 30, "Kapamilya Daily Mass", 30),
            (6, 0, "Kids Block (Bubu, Dinoman, Team YeY)", 150),
            (8, 30, "KB Family Weekend", 210),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Kapamilya Action Sabado / Movies", 150),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Variety / Game Show", 90),
            (19, 30, "Kapamilya Deal or No Deal", 60),
            (20, 30, "Maalaala Mo Kaya", 60),
            (21, 30, "Weekend Special / Blockbusters", 150),
        ],
        "sunday": [
            (6, 0, "The Healing Eucharist", 60),
            (7, 0, "Educational / Kids Block", 180),
            (10, 0, "KB Family Weekend / Movies", 120),
            (12, 0, "ASAP XP", 120),
            (14, 0, "Afternoon Specials / Movies", 180),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Primetime", 60),
            (19, 0, "ASAP XP (encore / main)", 105),
            (20, 45, "Kapamilya Deal or No Deal", 60),
            (21, 45, "Maalaala Mo Kaya", 60),
            (22, 45, "Super Kapamilya Blockbusters", 135),
        ],
    },
    "ALLTV2.ph": {
        # Shares most of Kapamilya feed
        "weekday": [
            (5, 30, "Kapamilya Daily Mass", 30),
            (6, 0, "Knowledge Channel / Kids", 180),
            (9, 0, "Magandang Buhay", 60),
            (10, 0, "Kapamilya Blockbusters", 120),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Kapamilya Gold", 180),
            (17, 30, "TV Patrol Express", 15),
            (17, 45, "Minute to Win It", 45),
            (18, 30, "TV Patrol", 90),
            (20, 0, "Primetime Bida", 165),
            (22, 45, "The World Tonight", 30),
        ],
        "saturday": [
            (5, 30, "Kapamilya Daily Mass", 30),
            (6, 0, "Kids Block", 150),
            (8, 30, "KB Family Weekend", 210),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Action / Movies", 150),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Shows", 330),
        ],
        "sunday": [
            (6, 0, "The Healing Eucharist", 60),
            (7, 0, "Kids / Educational", 180),
            (10, 0, "Movies / Family", 120),
            (12, 0, "ASAP XP", 120),
            (14, 0, "Afternoon Block", 180),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Primetime + ASAP XP", 300),
        ],
    },
    "A2Z.ph": {
        "weekday": [
            (5, 0, "Shuffle: Honoring God Through Music", 60),
            (6, 0, "Bro. Eddie Villanueva Classics", 60),
            (7, 0, "A2Z School Everywhere", 60),
            (8, 0, "The Flying House / Superbook", 60),
            (9, 0, "Magandang Buhay", 60),
            (10, 0, "Zinema sa Umaga", 120),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Afternoon Reruns / Zinema", 180),
            (17, 30, "TV Patrol Express", 15),
            (17, 45, "Primetime Preview", 45),
            (18, 30, "TV Patrol", 90),
            (20, 0, "Kapamilya Primetime (simulcast)", 165),
            (22, 45, "Balitang A2Z", 30),
            (23, 15, "Bro. Eddie Classics (replay)", 45),
        ],
        "saturday": [
            (6, 0, "Shuffle", 60),
            (7, 0, "Jesus the Healer", 60),
            (8, 0, "Kids Block (Bubu, Team YeY, Wansapanataym)", 120),
            (10, 0, "Zinema sa Umaga", 120),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Zine Aksyon / Afternoon", 150),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Primetime", 300),
        ],
        "sunday": [
            (6, 0, "Shuffle", 60),
            (7, 0, "JIL Sunday Worship", 120),
            (9, 0, "Kids / Team YeY Sunday", 60),
            (10, 0, "Zinema sa Umaga", 120),
            (12, 0, "ASAP XP", 120),
            (14, 0, "Afternoon Movies / Specials", 180),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Primetime + ASAP", 300),
        ],
    },
    "JeepneyTV.ph": {
        "weekday": [
            (0, 0, "Classic Teleserye Marathon (overnight)", 330),
            (5, 30, "Classic Drama", 60),
            (6, 30, "Classic Drama", 60),
            (7, 30, "Kapamilya Daily Mass (delayed)", 30),
            (8, 0, "Classic Series", 60),
            (9, 0, "Magandang Buhay (simulcast)", 60),
            (10, 0, "Classic Series / Annaliza etc.", 60),
            (11, 0, "Classic Series", 60),
            (12, 0, "Classic Series", 60),
            (13, 0, "Classic Series", 60),
            (14, 0, "Classic Series / PHR", 90),
            (15, 30, "Classic Series", 90),
            (17, 0, "Classic Series", 30),
            (17, 30, "TV Patrol Express (simulcast)", 15),
            (17, 45, "Classic Series", 255),
            (22, 0, "Classic Series / Late Night", 120),
        ],
        "saturday": [
            (0, 0, "Classic Marathon", 450),
            (7, 30, "Kapamilya Daily Mass (delayed)", 30),
            (8, 0, "Classic Weekend Block", 240),
            (12, 0, "Classic / Showtime encore", 180),
            (15, 0, "Classic Action / Drama", 150),
            (17, 30, "TV Patrol Express / Weekend", 30),
            (18, 0, "Classic Primetime Reruns", 360),
        ],
        "sunday": [
            (0, 0, "Classic Marathon", 360),
            (6, 0, "Healing Eucharist (delayed)", 60),
            (7, 0, "Classic Sunday Block", 300),
            (12, 0, "Classic / ASAP delayed later", 300),
            (17, 0, "Classic Evening", 180),
            (20, 0, "ASAP XP (delayed telecast)", 120),
            (22, 0, "Classic Late Night", 120),
        ],
    },
    "GMA.ph": {
        "weekday": [
            (5, 30, "Unang Hirit", 150),
            (8, 0, "Anime / Kids Block", 60),
            (9, 0, "Morning Talk / Variety", 120),
            (11, 0, "TiktoClock", 60),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Born to Shine", 50),
            (15, 20, "Delivery Boi / Afternoon Drama", 45),
            (16, 5, "Fast Talk with Boy Abunda", 25),
            (16, 30, "Maria Clara at Ibarra", 40),
            (17, 10, "Encantadia (rerun)", 30),
            (17, 40, "Family Feud Philippines", 50),
            (18, 30, "24 Oras", 90),
            (20, 0, "GMA Prime Drama 1", 50),
            (20, 50, "Taskforce Firewall", 45),
            (21, 35, "GMA Prime Drama 3", 40),
            (22, 15, "Saksi", 45),
            (23, 0, "Late Night / Asian Drama", 60),
        ],
        "saturday": [
            (5, 30, "Kapwa Ko Mahal Ko / Agri", 90),
            (7, 0, "Kids / Anime Block", 120),
            (9, 0, "Morning Variety / Movies", 180),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Born to Shine", 50),
            (15, 20, "Afternoon Block", 130),
            (17, 30, "24 Oras Weekend", 60),
            (18, 30, "Saturday Primetime / Variety", 300),
        ],
        "sunday": [
            (5, 30, "Religious / Early", 90),
            (7, 0, "Kids Block", 120),
            (9, 0, "All Out Sundays / Variety", 180),
            (12, 0, "Sunday Afternoon Specials", 180),
            (15, 0, "Magpakailanman / Docs", 90),
            (16, 30, "Public Affairs", 60),
            (17, 30, "24 Oras Weekend", 60),
            (18, 30, "Sunday Primetime", 30),
            (19, 0, "The Voice Kids", 90),
            (20, 30, "Sunday Specials / Movies", 150),
        ],
    },
    "GTV.ph": {
        "weekday": [
            (5, 30, "Dobol B TV / Buena Manong Balita", 210),
            (9, 0, "Cinema G!", 120),
            (11, 0, "Balitanghali", 60),
            (12, 0, "Noontime Movie Hits", 150),
            (14, 30, "Asian Drama 1", 30),
            (15, 0, "Asian Drama 2", 30),
            (15, 30, "Afternoon Movie Break / Regal", 135),
            (17, 45, "Luv Is / Afternoon Series", 45),
            (18, 30, "24 Oras (simulcast)", 90),
            (20, 0, "G! Flicks", 105),
            (21, 45, "Encantadia Chronicles: Sang'gre", 45),
            (22, 30, "Sanggang Dikit FR", 35),
            (23, 5, "State of the Nation", 25),
            (23, 30, "Beauty Empire / Late Night", 30),
        ],
        "saturday": [
            (5, 30, "Dobol B TV (weekend)", 210),
            (9, 0, "ExperTalk / Healing Galing", 90),
            (10, 30, "Saturday Cinema Hits", 90),
            (12, 0, "Noontime Movie Hits / Showtime", 150),
            (14, 30, "Afternoon Movie Break", 180),
            (17, 30, "24 Oras Weekend", 60),
            (18, 30, "G! Flicks", 105),
            (20, 15, "Pinas Sarap / Public Affairs", 60),
            (21, 15, "Weekend Specials", 165),
        ],
        "sunday": [
            (6, 0, "Kids / Anime Block", 210),
            (9, 30, "Sunday Movies / Specials", 150),
            (12, 0, "Sine Date Weekends / Movies", 180),
            (15, 0, "Afternoon Movie Break", 150),
            (17, 30, "24 Oras Weekend", 60),
            (18, 30, "Sunday G! Flicks / Specials", 270),
        ],
    },
}


def fmt(dt: datetime) -> str:
    """XMLTV timestamp: YYYYMMDDHHMMSS +0000 (we use +0800 for Manila)"""
    return dt.strftime("%Y%m%d%H%M%S +0800")


def add_programme(root, channel_id, start, stop, title, desc=""):
    prog = ET.SubElement(root, "programme", start=fmt(start), stop=fmt(stop), channel=channel_id)
    t = ET.SubElement(prog, "title", lang="en")
    t.text = title
    if desc:
        d = ET.SubElement(prog, "desc", lang="en")
        d.text = desc
    return prog


def generate():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now(TZ)
    # Start from today 00:00
    base = now.replace(hour=0, minute=0, second=0, microsecond=0)

    root = ET.Element("tv", attrib={
        "generator-info-name": "ph-tv-epg",
        "generator-info-url": "https://github.com/YOUR_USERNAME/ph-tv-epg",
        "date": now.strftime("%Y%m%d%H%M%S +0800"),
    })

    # Channels
    for ch in CHANNELS:
        c = ET.SubElement(root, "channel", id=ch["id"])
        dn = ET.SubElement(c, "display-name")
        dn.text = ch["display-name"]
        if ch.get("icon"):
            ET.SubElement(c, "icon", src=ch["icon"])

    # 14-day rolling guide (denser coverage)
    for day_offset in range(14):
        day = base + timedelta(days=day_offset)
        weekday = day.weekday()  # 0=Mon ... 6=Sun

        for ch_id, templates in SCHEDULES.items():
            if weekday < 5:
                slots = templates["weekday"]
            elif weekday == 5:
                slots = templates["saturday"]
            else:
                slots = templates["sunday"]

            for hour, minute, title, duration in slots:
                start = day.replace(hour=hour, minute=minute, second=0, microsecond=0)
                stop = start + timedelta(minutes=duration)
                # Skip if programme already ended more than 1 day ago (keep future + recent)
                if stop < now - timedelta(days=1):
                    continue
                add_programme(root, ch_id, start, stop, title)

    # Pretty print
    rough = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough)
    pretty = reparsed.toprettyxml(indent="  ", encoding="utf-8")

    with open(XML_PATH, "wb") as f:
        f.write(pretty)

    # Also write gzipped
    with open(XML_PATH, "rb") as f_in:
        with gzip.open(GZ_PATH, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    print(f"Generated: {XML_PATH}")
    print(f"Generated: {GZ_PATH}")
    print(f"Base date: {base.date()} | Generated at: {now.isoformat()}")


if __name__ == "__main__":
    generate()

import shutil

TZ = ZoneInfo("Asia/Manila")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "epg")
XML_PATH = os.path.join(OUTPUT_DIR, "ph-tv-epg.xml")
GZ_PATH = os.path.join(OUTPUT_DIR, "ph-tv-epg.xml.gz")

CHANNELS = [
    {"id": "TV5.ph", "display-name": "TV5", "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/TV5_Logo_2021.svg/200px-TV5_Logo_2021.svg.png"},
    {"id": "Kapamilya.ph", "display-name": "Kapamilya Channel", "icon": ""},
    {"id": "ALLTV2.ph", "display-name": "ALLTV2", "icon": ""},
    {"id": "A2Z.ph", "display-name": "A2Z", "icon": ""},
    {"id": "JeepneyTV.ph", "display-name": "Jeepney TV", "icon": ""},
    {"id": "GMA.ph", "display-name": "GMA Network", "icon": ""},
    {"id": "GTV.ph", "display-name": "GTV", "icon": ""},
]

# Approximate weekly templates (hour, minute, title, duration_minutes)
# Day keys: 0=Mon ... 6=Sun
SCHEDULES = {
    "TV5.ph": {
        "weekday": [  # Mon-Fri
            (4, 30, "Mga Kwentong MX3", 60),
            (5, 30, "Frontline sa Umaga", 150),
            (8, 0, "Chibi Maruko Chan", 30),
            (8, 30, "Blockbusters sa Umaga", 120),
            (10, 30, "Frontline Express AM", 30),
            (11, 0, "Gandang Mornings with Ate Koring", 60),
            (12, 0, "Eat Bulaga!", 150),
            (14, 30, "Mommy Guard / Afternoon Series", 45),
            (15, 15, "Frontline Express PM", 45),
            (16, 0, "Suntok sa Buwan", 45),
            (16, 45, "Knight Rider", 45),
            (17, 30, "Jasmine", 30),
            (18, 0, "Frontline Pilipinas: Una sa Lahat", 30),
            (18, 30, "Frontline Pilipinas", 90),
            (20, 0, "Sigabo", 45),
            (20, 45, "Someone, Someday", 45),
            (21, 30, "The Loyalty Game: Level Up", 45),
            (22, 15, "Frontline Tonight", 30),
            (22, 45, "Cassandra: Warrior Angel", 45),
            (23, 30, "Vibe Nights / Oras ng Himala", 60),
        ],
        "saturday": [
            (7, 0, "Prinsipe Cedie", 30),
            (7, 30, "The Adventures of Tom Sawyer", 60),
            (8, 30, "Little Princess Sarah", 60),
            (9, 30, "Blockbusters sa Umaga", 115),
            (11, 25, "Eat Bulaga!", 180),
            (14, 25, "Frontline Express", 45),
            (15, 10, "Cine Cinco Hit na Hit", 110),
            (17, 0, "Frontline Pilipinas Weekend", 60),
            (18, 0, "Vibe+", 90),
            (19, 30, "Kapamilya Deal or No Deal", 60),
            (20, 30, "Maalaala Mo Kaya", 60),
            (21, 30, "Matteo G Primetime", 60),
            (22, 30, "America's Got Talent", 60),
            (23, 30, "In Touch with Dr. Charles Stanley", 30),
        ],
        "sunday": [
            (5, 30, "In Touch with Dr. Charles Stanley", 30),
            (6, 0, "Sunday Mass", 60),
            (7, 0, "Oras ng Katotohanan", 60),
            (8, 0, "Prinsipe Cedie", 60),
            (9, 0, "The Adventures of Tom Sawyer", 60),
            (10, 0, "Blockbusters sa Umaga", 120),
            (12, 0, "Vibe+ Playback", 90),
            (13, 30, "Cine Cinco Astig Sunday", 120),
            (15, 30, "Julius Babao Unplugged", 30),
            (16, 0, "Rated Korina", 60),
            (17, 0, "Frontline Pilipinas Weekend", 60),
            (18, 0, "Kapatid Mo, Idol Raffy Tulfo", 60),
            (19, 0, "ASAP XP", 105),
            (20, 45, "Kapamilya Deal or No Deal", 60),
            (21, 45, "Maalaala Mo Kaya", 60),
            (22, 45, "Kapatid Sunday Specials", 75),
        ],
    },
    "Kapamilya.ph": {
        "weekday": [
            (5, 30, "Kapamilya Daily Mass", 30),
            (6, 0, "Knowledge Channel School Anywhere", 60),
            (7, 0, "Kids / Rerun Block", 120),
            (9, 0, "Magandang Buhay", 60),
            (10, 0, "Kapamilya Blockbusters", 120),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Kapamilya Gold Drama", 90),
            (16, 0, "Kapamilya Gold Hits / Afternoon Zinema", 90),
            (17, 30, "TV Patrol Express", 15),
            (17, 45, "Minute to Win It / Goin' Bulilit", 45),
            (18, 30, "TV Patrol", 90),
            (20, 0, "Primetime Bida Drama 1", 45),
            (20, 45, "Primetime Bida Drama 2", 45),
            (21, 30, "Primetime Bida Drama 3", 45),
            (22, 15, "Primetime Bida Drama 4 / Asian Drama", 30),
            (22, 45, "The World Tonight", 30),
            (23, 15, "Movie Central Presents", 165),
        ],
        "saturday": [
            (5, 30, "Kapamilya Daily Mass", 30),
            (6, 0, "Kids Block (Bubu, Dinoman, Team YeY)", 150),
            (8, 30, "KB Family Weekend", 210),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Kapamilya Action Sabado / Movies", 150),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Variety / Game Show", 90),
            (19, 30, "Kapamilya Deal or No Deal", 60),
            (20, 30, "Maalaala Mo Kaya", 60),
            (21, 30, "Weekend Special / Blockbusters", 150),
        ],
        "sunday": [
            (6, 0, "The Healing Eucharist", 60),
            (7, 0, "Educational / Kids Block", 180),
            (10, 0, "KB Family Weekend / Movies", 120),
            (12, 0, "ASAP XP", 120),
            (14, 0, "Afternoon Specials / Movies", 180),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Primetime", 60),
            (19, 0, "ASAP XP (encore / main)", 105),
            (20, 45, "Kapamilya Deal or No Deal", 60),
            (21, 45, "Maalaala Mo Kaya", 60),
            (22, 45, "Super Kapamilya Blockbusters", 135),
        ],
    },
    "ALLTV2.ph": {
        # Shares most of Kapamilya feed
        "weekday": [
            (5, 30, "Kapamilya Daily Mass", 30),
            (6, 0, "Knowledge Channel / Kids", 180),
            (9, 0, "Magandang Buhay", 60),
            (10, 0, "Kapamilya Blockbusters", 120),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Kapamilya Gold", 180),
            (17, 30, "TV Patrol Express", 15),
            (17, 45, "Minute to Win It", 45),
            (18, 30, "TV Patrol", 90),
            (20, 0, "Primetime Bida", 165),
            (22, 45, "The World Tonight", 30),
        ],
        "saturday": [
            (5, 30, "Kapamilya Daily Mass", 30),
            (6, 0, "Kids Block", 150),
            (8, 30, "KB Family Weekend", 210),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Action / Movies", 150),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Shows", 330),
        ],
        "sunday": [
            (6, 0, "The Healing Eucharist", 60),
            (7, 0, "Kids / Educational", 180),
            (10, 0, "Movies / Family", 120),
            (12, 0, "ASAP XP", 120),
            (14, 0, "Afternoon Block", 180),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Primetime + ASAP XP", 300),
        ],
    },
    "A2Z.ph": {
        "weekday": [
            (5, 0, "Shuffle: Honoring God Through Music", 60),
            (6, 0, "Bro. Eddie Villanueva Classics", 60),
            (7, 0, "A2Z School Everywhere", 60),
            (8, 0, "The Flying House / Superbook", 60),
            (9, 0, "Magandang Buhay", 60),
            (10, 0, "Zinema sa Umaga", 120),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Afternoon Reruns / Zinema", 180),
            (17, 30, "TV Patrol Express", 15),
            (17, 45, "Primetime Preview", 45),
            (18, 30, "TV Patrol", 90),
            (20, 0, "Kapamilya Primetime (simulcast)", 165),
            (22, 45, "Balitang A2Z", 30),
            (23, 15, "Bro. Eddie Classics (replay)", 45),
        ],
        "saturday": [
            (6, 0, "Shuffle", 60),
            (7, 0, "Jesus the Healer", 60),
            (8, 0, "Kids Block (Bubu, Team YeY, Wansapanataym)", 120),
            (10, 0, "Zinema sa Umaga", 120),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Zine Aksyon / Afternoon", 150),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Primetime", 300),
        ],
        "sunday": [
            (6, 0, "Shuffle", 60),
            (7, 0, "JIL Sunday Worship", 120),
            (9, 0, "Kids / Team YeY Sunday", 60),
            (10, 0, "Zinema sa Umaga", 120),
            (12, 0, "ASAP XP", 120),
            (14, 0, "Afternoon Movies / Specials", 180),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Primetime + ASAP", 300),
        ],
    },
    "JeepneyTV.ph": {
        "weekday": [
            (0, 0, "Classic Teleserye Marathon (overnight)", 330),
            (5, 30, "Classic Drama", 60),
            (6, 30, "Classic Drama", 60),
            (7, 30, "Kapamilya Daily Mass (delayed)", 30),
            (8, 0, "Classic Series", 60),
            (9, 0, "Magandang Buhay (simulcast)", 60),
            (10, 0, "Classic Series / Annaliza etc.", 60),
            (11, 0, "Classic Series", 60),
            (12, 0, "Classic Series", 60),
            (13, 0, "Classic Series", 60),
            (14, 0, "Classic Series / PHR", 90),
            (15, 30, "Classic Series", 90),
            (17, 0, "Classic Series", 30),
            (17, 30, "TV Patrol Express (simulcast)", 15),
            (17, 45, "Classic Series", 255),
            (22, 0, "Classic Series / Late Night", 120),
        ],
        "saturday": [
            (0, 0, "Classic Marathon", 450),
            (7, 30, "Kapamilya Daily Mass (delayed)", 30),
            (8, 0, "Classic Weekend Block", 240),
            (12, 0, "Classic / Showtime encore", 180),
            (15, 0, "Classic Action / Drama", 150),
            (17, 30, "TV Patrol Express / Weekend", 30),
            (18, 0, "Classic Primetime Reruns", 360),
        ],
        "sunday": [
            (0, 0, "Classic Marathon", 360),
            (6, 0, "Healing Eucharist (delayed)", 60),
            (7, 0, "Classic Sunday Block", 300),
            (12, 0, "Classic / ASAP delayed later", 300),
            (17, 0, "Classic Evening", 180),
            (20, 0, "ASAP XP (delayed telecast)", 120),
            (22, 0, "Classic Late Night", 120),
        ],
    },
    "GMA.ph": {
        "weekday": [
            (5, 30, "Unang Hirit", 150),
            (8, 0, "Anime / Kids Block", 60),
            (9, 0, "Morning Talk / Variety", 120),
            (11, 0, "TiktoClock", 60),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Born to Shine", 50),
            (15, 20, "Delivery Boi / Afternoon Drama", 45),
            (16, 5, "Fast Talk with Boy Abunda", 25),
            (16, 30, "Maria Clara at Ibarra", 40),
            (17, 10, "Encantadia (rerun)", 30),
            (17, 40, "Family Feud Philippines", 50),
            (18, 30, "24 Oras", 90),
            (20, 0, "GMA Prime Drama 1", 50),
            (20, 50, "Taskforce Firewall", 45),
            (21, 35, "GMA Prime Drama 3", 40),
            (22, 15, "Saksi", 45),
            (23, 0, "Late Night / Asian Drama", 60),
        ],
        "saturday": [
            (5, 30, "Kapwa Ko Mahal Ko / Agri", 90),
            (7, 0, "Kids / Anime Block", 120),
            (9, 0, "Morning Variety / Movies", 180),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Born to Shine", 50),
            (15, 20, "Afternoon Block", 130),
            (17, 30, "24 Oras Weekend", 60),
            (18, 30, "Saturday Primetime / Variety", 300),
        ],
        "sunday": [
            (5, 30, "Religious / Early", 90),
            (7, 0, "Kids Block", 120),
            (9, 0, "All Out Sundays / Variety", 180),
            (12, 0, "Sunday Afternoon Specials", 180),
            (15, 0, "Magpakailanman / Docs", 90),
            (16, 30, "Public Affairs", 60),
            (17, 30, "24 Oras Weekend", 60),
            (18, 30, "Sunday Primetime", 30),
            (19, 0, "The Voice Kids", 90),
            (20, 30, "Sunday Specials / Movies", 150),
        ],
    },
    "GTV.ph": {
        "weekday": [
            (5, 30, "Dobol B TV / Buena Manong Balita", 210),
            (9, 0, "Cinema G!", 120),
            (11, 0, "Balitanghali", 60),
            (12, 0, "Noontime Movie Hits", 150),
            (14, 30, "Asian Drama 1", 30),
            (15, 0, "Asian Drama 2", 30),
            (15, 30, "Afternoon Movie Break / Regal", 135),
            (17, 45, "Luv Is / Afternoon Series", 45),
            (18, 30, "24 Oras (simulcast)", 90),
            (20, 0, "G! Flicks", 105),
            (21, 45, "Encantadia Chronicles: Sang'gre", 45),
            (22, 30, "Sanggang Dikit FR", 35),
            (23, 5, "State of the Nation", 25),
            (23, 30, "Beauty Empire / Late Night", 30),
        ],
        "saturday": [
            (5, 30, "Dobol B TV (weekend)", 210),
            (9, 0, "ExperTalk / Healing Galing", 90),
            (10, 30, "Saturday Cinema Hits", 90),
            (12, 0, "Noontime Movie Hits / Showtime", 150),
            (14, 30, "Afternoon Movie Break", 180),
            (17, 30, "24 Oras Weekend", 60),
            (18, 30, "G! Flicks", 105),
            (20, 15, "Pinas Sarap / Public Affairs", 60),
            (21, 15, "Weekend Specials", 165),
        ],
        "sunday": [
            (6, 0, "Kids / Anime Block", 210),
            (9, 30, "Sunday Movies / Specials", 150),
            (12, 0, "Sine Date Weekends / Movies", 180),
            (15, 0, "Afternoon Movie Break", 150),
            (17, 30, "24 Oras Weekend", 60),
            (18, 30, "Sunday G! Flicks / Specials", 270),
        ],
    },
}


def fmt(dt: datetime) -> str:
    """XMLTV timestamp: YYYYMMDDHHMMSS +0000 (we use +0800 for Manila)"""
    return dt.strftime("%Y%m%d%H%M%S +0800")


def add_programme(root, channel_id, start, stop, title, desc=""):
    prog = ET.SubElement(root, "programme", start=fmt(start), stop=fmt(stop), channel=channel_id)
    t = ET.SubElement(prog, "title", lang="en")
    t.text = title
    if desc:
        d = ET.SubElement(prog, "desc", lang="en")
        d.text = desc
    return prog


def generate():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now(TZ)
    # Start from today 00:00
    base = now.replace(hour=0, minute=0, second=0, microsecond=0)

    root = ET.Element("tv", attrib={
        "generator-info-name": "ph-tv-epg",
        "generator-info-url": "https://github.com/YOUR_USERNAME/ph-tv-epg",
        "date": now.strftime("%Y%m%d%H%M%S +0800"),
    })

    # Channels
    for ch in CHANNELS:
        c = ET.SubElement(root, "channel", id=ch["id"])
        dn = ET.SubElement(c, "display-name")
        dn.text = ch["display-name"]
        if ch.get("icon"):
            ET.SubElement(c, "icon", src=ch["icon"])

    # 7-day rolling guide
    for day_offset in range(7):
        day = base + timedelta(days=day_offset)
        weekday = day.weekday()  # 0=Mon ... 6=Sun

        for ch_id, templates in SCHEDULES.items():
            if weekday < 5:
                slots = templates["weekday"]
            elif weekday == 5:
                slots = templates["saturday"]
            else:
                slots = templates["sunday"]

            for hour, minute, title, duration in slots:
                start = day.replace(hour=hour, minute=minute, second=0, microsecond=0)
                stop = start + timedelta(minutes=duration)
                # Skip if programme already ended more than 1 day ago (keep future + recent)
                if stop < now - timedelta(days=1):
                    continue
                add_programme(root, ch_id, start, stop, title)

    # Pretty print
    rough = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough)
    pretty = reparsed.toprettyxml(indent="  ", encoding="utf-8")

    with open(XML_PATH, "wb") as f:
        f.write(pretty)

    # Also write gzipped
    with open(XML_PATH, "rb") as f_in:
        with gzip.open(GZ_PATH, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    print(f"Generated: {XML_PATH}")
    print(f"Generated: {GZ_PATH}")
    print(f"Base date: {base.date()} | Generated at: {now.isoformat()}")


if __name__ == "__main__":
    generate()
