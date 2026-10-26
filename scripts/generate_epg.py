#!/usr/bin/env python3
"""
Philippine TV EPG Generator (XMLTV) - 2026 Updated
Generates a rolling 14-day EPG with current date/time awareness.
Timezone: Asia/Manila (UTC+8)
Includes: TV5, Kapamilya, ALLTV2, A2Z, JeepneyTV, GMA, GTV,
          Cinema One Global, TFC Asia, Hallypop, DZMM Teleradyo, Cinemo PH
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
    {"id": "CinemaOneGlobal.ph", "display-name": "Cinema One Global", "icon": ""},
    {"id": "TFCAsia.ph", "display-name": "TFC Asia", "icon": ""},
    {"id": "Hallypop.ph", "display-name": "Hallypop", "icon": ""},
    {"id": "DZMMTeleradyo.ph", "display-name": "DZMM Teleradyo", "icon": ""},
    {"id": "Cinemo.ph", "display-name": "Cinemo PH", "icon": ""},
]

# 2026 Accurate Weekly Templates (hour, minute, title, duration_minutes)
SCHEDULES = {
    "TV5.ph": {
        "weekday": [
            (4, 30, "Mga Kwentong MX3", 60),
            (5, 30, "Frontline sa Umaga", 150),
            (8, 0, "Chibi Maruko Chan", 30),
            (8, 30, "Blockbusters sa Umaga", 120),
            (10, 30, "Frontline Express AM", 30),
            (11, 0, "Gandang Mornings with Ate Koring", 60),
            (12, 0, "Eat Bulaga!", 150),
            (14, 30, "Afternoon Drama", 45),
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
            (23, 30, "Oras ng Himala", 60),
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
            (18, 0, "Gandang Gabi Vice (Classic / Special)", 90),
            (19, 30, "Kapamilya Deal or No Deal", 60),
            (20, 30, "Maalaala Mo Kaya", 60),
            (21, 30, "Sigabo (Weekend Encore)", 60),
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
            (12, 0, "Gandang Gabi Vice Replay", 90),
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
            (7, 0, "Team YeY / Kids Block", 120),
            (9, 0, "Magandang Buhay", 60),
            (10, 0, "Kapamilya Blockbusters", 120),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Kapamilya Gold Drama", 90),
            (16, 0, "Afternoon Zinema", 90),
            (17, 30, "TV Patrol Express", 15),
            (17, 45, "Goin' Bulilit", 45),
            (18, 30, "TV Patrol", 90),
            (20, 0, "Sigabo", 45),
            (20, 45, "Lavender Fields / Primetime Bida", 45),
            (21, 30, "High Street / Primetime Drama", 45),
            (22, 15, "Asianovela / The Voice Kids Rerun", 30),
            (22, 45, "The World Tonight", 30),
            (23, 15, "Movie Central Presents", 165),
        ],
        "saturday": [
            (5, 30, "Kapamilya Daily Mass", 30),
            (6, 0, "Kids Block (Bubu, Dinoman, Team YeY)", 150),
            (8, 30, "KB Family Weekend", 210),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Kapamilya Action Sabado", 150),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Rainbow Rumble", 90),
            (19, 30, "Kapamilya Deal or No Deal", 60),
            (20, 30, "Maalaala Mo Kaya", 60),
            (21, 30, "Blockbusters sa Sabado", 150),
        ],
        "sunday": [
            (6, 0, "The Healing Eucharist", 60),
            (7, 0, "Team YeY Sunday / Educational", 180),
            (10, 0, "KB Family Weekend", 120),
            (12, 0, "ASAP XP", 120),
            (14, 0, "FPJ Da King Movies", 180),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Rated Korina", 60),
            (19, 0, "ASAP XP (Main Feed)", 105),
            (20, 45, "Kapamilya Deal or No Deal", 60),
            (21, 45, "Maalaala Mo Kaya", 60),
            (22, 45, "Super Kapamilya Blockbusters", 135),
        ],
    },
    "ALLTV2.ph": {
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
            (20, 0, "Sigabo (Simulcast)", 165),
            (22, 45, "The World Tonight", 30),
        ],
        "saturday": [
            (5, 30, "Kapamilya Daily Mass", 30),
            (6, 0, "Kids Block", 150),
            (8, 30, "KB Family Weekend", 210),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Action / Movies", 150),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "AllTV Weekend Specials", 330),
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
            (20, 0, "Sigabo (Simulcast)", 165),
            (22, 45, "Balitang A2Z", 30),
            (23, 15, "Bro. Eddie Classics", 45),
        ],
        "saturday": [
            (6, 0, "Shuffle", 60),
            (7, 0, "Jesus the Healer", 60),
            (8, 0, "Kids Block (Team YeY, Wansapanataym)", 120),
            (10, 0, "Zinema sa Umaga", 120),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Zine Aksyon", 150),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Primetime", 300),
        ],
        "sunday": [
            (6, 0, "Shuffle", 60),
            (7, 0, "JIL Sunday Worship", 120),
            (9, 0, "Team YeY Sunday", 60),
            (10, 0, "Zinema sa Umaga", 120),
            (12, 0, "ASAP XP", 120),
            (14, 0, "Afternoon Movies / Specials", 180),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Primetime + ASAP", 300),
        ],
    },
    "JeepneyTV.ph": {
        "weekday": [
            (0, 0, "Classic Teleserye Marathon", 330),
            (5, 30, "Mara Clara (Classic)", 60),
            (6, 30, "Pangako Sa 'Yo (Classic)", 60),
            (7, 30, "Kapamilya Daily Mass (Delayed)", 30),
            (8, 0, "Tabing Ilog", 60),
            (9, 0, "Magandang Buhay (Simulcast)", 60),
            (10, 0, "Annaliza", 60),
            (11, 0, "Be Careful With My Heart", 60),
            (12, 0, "Kadenang Ginto", 60),
            (13, 0, "The General's Daughter", 60),
            (14, 0, "Classic Run", 90),
            (15, 30, "Wildflower", 90),
            (17, 0, "Got to Believe", 30),
            (17, 30, "TV Patrol Express (Simulcast)", 15),
            (17, 45, "Princess and I", 255),
            (22, 0, "Banana Sundae / Goin' Bulilit Classics", 120),
        ],
        "saturday": [
            (0, 0, "Classic Marathon", 450),
            (7, 30, "Kapamilya Daily Mass (Delayed)", 30),
            (8, 0, "Super Inggo", 240),
            (12, 0, "It's Showtime Classic Encore", 180),
            (15, 0, "Action Sabado Classics", 150),
            (17, 30, "TV Patrol Weekend", 30),
            (18, 0, "Maalaala Mo Kaya Classics", 360),
        ],
        "sunday": [
            (0, 0, "Classic Marathon", 360),
            (6, 0, "Healing Eucharist (Delayed)", 60),
            (7, 0, "Sine Omnibus", 300),
            (12, 0, "ASAP Classic Archives", 300),
            (17, 0, "Rated K Classic", 180),
            (20, 0, "Gandang Gabi Vice Archives", 120),
            (22, 0, "MOR Originals / Late Night", 120),
        ],
    },
    "GMA.ph": {
        "weekday": [
            (5, 30, "Unang Hirit", 150),
            (8, 0, "Pokemon / Anime / Kids Block", 60),
            (9, 0, "Morning Variety", 120),
            (11, 0, "TiktoClock", 60),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Afternoon Drama", 50),
            (15, 20, "Abot-Kamay na Pangarap", 45),
            (16, 5, "Fast Talk with Boy Abunda", 25),
            (16, 30, "Pulang Araw", 40),
            (17, 10, "Encantadia Chronicles (Rerun)", 30),
            (17, 40, "Family Feud Philippines", 50),
            (18, 30, "24 Oras", 90),
            (20, 0, "Primetime Drama", 50),
            (20, 50, "Asawa ng Asawa Ko", 45),
            (21, 35, "Lolong: Bayani ng Bayan", 40),
            (22, 15, "Saksi", 45),
            (23, 0, "The Fake Life / Asian Drama", 60),
        ],
        "saturday": [
            (5, 30, "Kapwa Ko Mahal Ko / Agripreneur", 90),
            (7, 0, "Smart Kids / Anime Block", 120),
            (9, 0, "Magpakailanman Replay", 180),
            (12, 0, "It's Showtime", 150),
            (14, 30, "Sparkle U / Sabado Specials", 50),
            (15, 20, "GMA Blockbusters", 130),
            (17, 30, "24 Oras Weekend", 60),
            (18, 30, "Pinoy Crime Stories / Pepito Manaloto", 300),
        ],
        "sunday": [
            (5, 30, "In Touch / The Word Exposed", 90),
            (7, 0, "Kids Block", 120),
            (9, 0, "All-Out Sundays", 180),
            (12, 0, "GMA Blockbusters Sunday", 180),
            (15, 0, "Magpakailanman", 90),
            (16, 30, "Imbestigador", 60),
            (17, 30, "24 Oras Weekend", 60),
            (18, 30, "The Voice Kids", 30),
            (19, 0, "The Voice Kids (Main)", 90),
            (20, 30, "Amazing Earth / Sunday Specials", 150),
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
            (15, 30, "Afternoon Movie Break / Regal Studio Presents", 135),
            (17, 45, "Luv Is / Afternoon Series", 45),
            (18, 30, "24 Oras (Simulcast)", 90),
            (20, 0, "G! Flicks", 105),
            (21, 45, "Encantadia Chronicles: Sang'gre", 45),
            (22, 30, "Sanggang Dikit", 35),
            (23, 5, "State of the Nation", 25),
            (23, 30, "GTV Documentaries / Late Night", 30),
        ],
        "saturday": [
            (5, 30, "Dobol B TV Weekend", 210),
            (9, 0, "Pinas Sarap / Healing Galing", 90),
            (10, 30, "Saturday Cinema Hits", 90),
            (12, 0, "Noontime Movie Hits", 150),
            (14, 30, "Afternoon Movie Break", 180),
            (17, 30, "24 Oras Weekend", 60),
            (18, 30, "G! Flicks", 105),
            (20, 15, "Biyahe ni Drew / Pinas Sarap", 60),
            (21, 15, "GTV Weekend Specials", 165),
        ],
        "sunday": [
            (6, 0, "Animated Kids / Anime Block", 210),
            (9, 30, "Sunday Telesine", 150),
            (12, 0, "Sine Date Weekends", 180),
            (15, 0, "Afternoon Movie Break", 150),
            (17, 30, "24 Oras Weekend", 60),
            (18, 30, "Sunday G! Flicks", 270),
        ],
    },
    "CinemaOneGlobal.ph": {
        "weekday": [
            (0, 0, "Cinema One Blockbuster: Hello, Love, Goodbye", 120),
            (2, 0, "A Very Special Love", 120),
            (4, 0, "One More Chance", 120),
            (6, 0, "Starting Over Again", 120),
            (8, 0, "The Hows of Us", 120),
            (10, 0, "Hello, Love, Goodbye", 120),
            (12, 0, "My Ex and Whys", 120),
            (14, 0, "Four Sisters and a Wedding", 120),
            (16, 0, "Crazy Beautiful You", 120),
            (18, 0, "She's Dating the Gangster", 120),
            (20, 0, "Alone/Together", 120),
            (22, 0, "Unofficially Yours", 120),
        ],
        "saturday": [
            (0, 0, "Kinabukasan Mo", 120),
            (2, 0, "Anak", 120),
            (4, 0, "Milan", 120),
            (6, 0, "Muro-Ami", 120),
            (8, 0, "Dekada '70", 120),
            (10, 0, "Feng Shui", 120),
            (12, 0, "Sukob", 120),
            (14, 0, "Caregiver", 120),
            (16, 0, "In My Life", 120),
            (18, 0, "The Mistress", 120),
            (20, 0, "Seven Sundays", 120),
            (22, 0, "Barcelona: A Love Untold", 120),
        ],
        "sunday": [
            (0, 0, "The Revengers Squad", 120),
            (2, 0, "Fantastica", 120),
            (4, 0, "The Mall, The Merrier", 120),
            (6, 0, "Gandarrapiddo: The Revengers Squad", 120),
            (8, 0, "Beauty and the Bestie", 120),
            (10, 0, "The Amazing Praybeyt Benjamin", 120),
            (12, 0, "Sisterakas", 120),
            (14, 0, "Moron 5 and the Crying Lady", 120),
            (16, 0, "Bromance: My Brother's Romance", 120),
            (18, 0, "My Amnesia Girl", 120),
            (20, 0, "Starting Over Again", 120),
            (22, 0, "Must Be... Love", 120),
        ],
    },
    "TFCAsia.ph": {
        "weekday": [
            (0, 0, "Overnight Drama Marathon", 270),
            (4, 30, "Kapamilya Daily Mass", 30),
            (5, 0, "Gising Pilipinas", 60),
            (6, 0, "It's Showtime (Live / Delayed)", 150),
            (8, 30, "Radyo Patrol Balita", 30),
            (9, 0, "Magandang Buhay", 90),
            (10, 30, "TV Patrol Express", 15),
            (10, 45, "Morning Series Rerun", 75),
            (12, 0, "TV Patrol Global", 90),
            (13, 30, "Sigabo Replay", 45),
            (14, 15, "Lavender Fields Replay", 45),
            (15, 0, "High Street Replay", 45),
            (15, 45, "It's Showtime (Encore)", 150),
            (18, 15, "TFC News / Specials", 45),
            (19, 0, "Pamilya Sagrado", 45),
            (19, 45, "The General's Daughter", 45),
            (20, 30, "Asianovela Presents", 45),
            (21, 15, "TV Patrol Global Edition", 45),
            (22, 0, "Cinema One Movie Special", 120),
        ],
        "saturday": [
            (0, 0, "Overnight Specials", 300),
            (5, 0, "TFC Kids Zone / Mass", 90),
            (6, 30, "Weekend Morning Block", 150),
            (9, 0, "It's Showtime Saturday", 180),
            (12, 0, "TV Patrol Weekend", 60),
            (13, 0, "Weekend Afternoon Blockbusters", 240),
            (17, 0, "TV Patrol Global Edition", 45),
            (17, 45, "Rainbow Rumble / MMK", 90),
            (19, 15, "ASAP XP Global", 120),
            (21, 15, "TFC Weekend Blockbusters", 165),
        ],
        "sunday": [
            (0, 0, "Overnight Specials", 300),
            (5, 0, "The Healing Eucharist", 60),
            (6, 0, "TFC Kids / Educational", 180),
            (9, 0, "Sunday Morning Movies", 180),
            (12, 0, "ASAP XP Global", 120),
            (14, 0, "FPJ Da King Movies", 180),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Rated Korina", 60),
            (19, 0, "ASAP XP Encore", 105),
            (20, 45, "Maalaala Mo Kaya", 60),
            (21, 45, "Sunday Blockbusters", 135),
        ],
    },
    "Hallypop.ph": {
        "weekday": [
            (0, 0, "StarGazeMuzik / Overnight K-Pop Hits", 360),
            (6, 0, "StarGazeMuzik", 60),
            (7, 0, "Mr. Hashtag", 30),
            (7, 30, "Innerview", 30),
            (8, 0, "HallyStage", 120),
            (10, 0, "StarGazeMuzik", 60),
            (11, 0, "Hallypop Hits", 30),
            (11, 30, "Hallypop Lokal", 30),
            (12, 0, "Scream Flix (K-Horror / Thriller)", 120),
            (14, 0, "StarGazeMuzik", 60),
            (15, 0, "Mr. Hashtag / Innerview", 60),
            (16, 0, "HallyStage", 120),
            (18, 0, "Fanpick", 60),
            (19, 0, "Hallypop Hits", 30),
            (19, 30, "Hallypop Lokal", 30),
            (20, 0, "Scream Flix", 120),
            (22, 0, "StarGazeMuzik", 60),
            (23, 0, "Hallypop Fresh", 30),
            (23, 30, "Hallypop Hits", 30),
        ],
        "saturday": [
            (0, 0, "StarGazeMuzik / Overnight", 360),
            (6, 0, "StarGazeMuzik", 60),
            (7, 0, "Fanpick", 60),
            (8, 0, "HallyStage", 120),
            (10, 0, "StarGazeMuzik", 120),
            (12, 0, "Scream Flix", 120),
            (14, 0, "Jungo Pinoy Presents", 120),
            (16, 0, "StarGazeMuzik", 120),
            (18, 0, "Scream Flix", 120),
            (20, 0, "Jungo Pinoy Presents", 120),
            (22, 0, "HallyStage", 120),
        ],
        "sunday": [
            (0, 0, "StarGazeMuzik / Overnight", 360),
            (6, 0, "StarGazeMuzik", 60),
            (7, 0, "Fanpick", 60),
            (8, 0, "HallyStage", 120),
            (10, 0, "StarGazeMuzik", 120),
            (12, 0, "Scream Flix", 120),
            (14, 0, "Jungo Pinoy Presents", 120),
            (16, 0, "StarGazeMuzik", 120),
            (18, 0, "Scream Flix", 120),
            (20, 0, "Jungo Pinoy Presents", 120),
            (22, 0, "HallyStage", 120),
        ],
    },
    "DZMMTeleradyo.ph": {
        "weekday": [
            (0, 0, "Remember Your Music / Overnight", 240),
            (4, 0, "Radyo Patrol Balita Alas-Kwatro", 60),
            (5, 0, "Pasada Balita", 60),
            (6, 0, "Gising Pilipinas", 60),
            (7, 0, "Radyo Patrol Balita Alas-Syete", 30),
            (7, 30, "Tandem ng Bayan (Early)", 30),
            (8, 0, "Tandem ng Bayan", 60),
            (9, 0, "Balitapatan", 60),
            (10, 0, "Kabayan", 60),
            (11, 0, "Nagseserbisyo, Niña Corpuz", 60),
            (12, 0, "Headline Ngayon", 30),
            (12, 30, "MMK sa DZMM", 30),
            (13, 0, "Hello Attorney", 60),
            (14, 0, "Aksyon Ngayon", 60),
            (15, 0, "Ako 'To si Tyang Amy", 60),
            (16, 0, "Headline sa Hapon", 30),
            (16, 30, "ATM: Anong Take Mo!", 60),
            (17, 30, "Isyu Spotted", 60),
            (18, 30, "TV Patrol (Simulcast)", 90),
            (20, 0, "Spot Report", 60),
            (21, 0, "Alam Na Dis!", 60),
            (22, 0, "Love Konek", 120),
        ],
        "saturday": [
            (0, 0, "Remember Your Music / Overnight", 240),
            (4, 0, "Yan Tayo!", 120),
            (6, 0, "Ano'ng Ganap?", 60),
            (7, 0, "Radyo Patrol Balita Weekend", 30),
            (7, 30, "Balita AnteMano", 90),
            (9, 0, "Mutya ng Masa", 60),
            (10, 0, "Win Today", 60),
            (11, 0, "Wais Konsyumer", 60),
            (12, 0, "Ligtas Dapat", 120),
            (14, 0, "Weekend Talk / Public Service", 180),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Weekend Primetime Specials", 120),
            (20, 0, "Spot Report Weekend", 120),
            (22, 0, "Love Konek Late Night", 120),
        ],
        "sunday": [
            (0, 0, "Remember Your Music / Overnight", 300),
            (5, 0, "Sunday Mass / Early Block", 120),
            (7, 0, "Radyo Patrol Balita Weekend", 30),
            (7, 30, "Sunday Morning Talk", 150),
            (10, 0, "Weekend Documentaries", 120),
            (12, 0, "Sunday Afternoon Block", 180),
            (15, 0, "Public Affairs Specials", 120),
            (17, 0, "TV Patrol Weekend", 60),
            (18, 0, "Sunday Primetime Coverage", 180),
            (21, 0, "Weekend Late Night Music", 180),
        ],
    },
    "Cinemo.ph": {
        "weekday": [
            (0, 0, "Action Movie Classics: Panday", 120),
            (2, 0, "Asiong Salonga", 120),
            (4, 0, "Bukas Ka Na Lang Magsisisi", 120),
            (6, 0, "Action Specials", 120),
            (8, 0, "Action Comedy Hits", 120),
            (10, 0, "Classic Movie", 120),
            (12, 0, "Ang Panday Series Marathon", 120),
            (14, 0, "Ramon Revilla Sr. Action Classic", 120),
            (16, 0, "Bong Revilla Action Special", 120),
            (18, 0, "Rudy Fernandez Action Hits", 120),
            (20, 0, "Prime Time Action", 120),
            (22, 0, "Late Night Action Thriller", 120),
        ],
        "saturday": [
            (0, 0, "Midnight Action Block", 120),
            (2, 0, "Pinoy Action Marathon", 120),
            (4, 0, "Classic Comedy Action", 120),
            (6, 0, "All-Star Hits", 120),
            (8, 0, "Weekend Special", 120),
            (10, 0, "Astig Sabado Movie 1", 120),
            (12, 0, "Astig Sabado Movie 2", 120),
            (14, 0, "Astig Sabado Movie 3", 120),
            (16, 0, "Cinemo Blockbuster 1", 120),
            (18, 0, "Cinemo Blockbuster 2", 120),
            (20, 0, "Prime Time Special", 120),
            (22, 0, "Late Night Action Block", 120),
        ],
        "sunday": [
            (0, 0, "Midnight Action Block", 120),
            (2, 0, "Pinoy Action Marathon", 120),
            (4, 0, "Classic Comedy Action", 120),
            (6, 0, "All-Star Hits", 120),
            (8, 0, "Sunday Family Movie", 120),
            (10, 0, "Astig Sunday Movie 1", 120),
            (12, 0, "Astig Sunday Movie 2", 120),
            (14, 0, "Astig Sunday Movie 3", 120),
            (16, 0, "Cinemo Sunday Blockbuster 1", 120),
            (18, 0, "Cinemo Sunday Blockbuster 2", 120),
            (20, 0, "Prime Time Special", 120),
            (22, 0, "Late Night Action Block", 120),
        ],
    },
}

def fmt(dt: datetime) -> str:
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
    base = now.replace(hour=0, minute=0, second=0, microsecond=0)
    root = ET.Element("tv", attrib={
        "generator-info-name": "ph-tv-epg",
        "generator-info-url": "https://github.com/YOUR_USERNAME/ph-tv-epg",
        "date": now.strftime("%Y%m%d%H%M%S +0800"),
    })
    for ch in CHANNELS:
        c = ET.SubElement(root, "channel", id=ch["id"])
        dn = ET.SubElement(c, "display-name")
        dn.text = ch["display-name"]
        if ch.get("icon"):
            ET.SubElement(c, "icon", src=ch["icon"])
            
    # 14-day rolling guide
    for day_offset in range(14):
        day = base + timedelta(days=day_offset)
        weekday = day.weekday()
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
                if stop < now - timedelta(days=1):
                    continue
                add_programme(root, ch_id, start, stop, title)
                
    rough = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough)
    pretty = reparsed.toprettyxml(indent="  ", encoding="utf-8")
    
    with open(XML_PATH, "wb") as f:
        f.write(pretty)
    with open(XML_PATH, "rb") as f_in:
        with gzip.open(GZ_PATH, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
            
    print(f"Generated: {XML_PATH}")
    print(f"Generated: {GZ_PATH}")
    print(f"Base date: {base.date()} | Generated at: {now.isoformat()}")
    print(f"Channels: {len(CHANNELS)} | Days: 14")

if __name__ == "__main__":
    generate()
