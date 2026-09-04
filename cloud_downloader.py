import os
import re
import sys
import json
import time
import shutil
import random
import logging
import argparse
import subprocess
from pathlib import Path
import yt_dlp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline_execution.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("MatrixPipeline")

BASE_DIR = Path("Trade_Dataset_281")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# کلاینت‌های مختلف برای فازهای تلاش مجدد
CLIENT_PROFILES = [
    ["android", "ios"],                     # دور اول: اپلیکیشن موبایل
    ["tv_embedded", "web_embedded"],        # دور دوم: تلویزیون هوشمند
    ["mweb", "default"]                     # دور سوم: وب سبک
]

COOKIE_FILE = "cookies.txt" if Path("cookies.txt").exists() else None

VIDEOS_DATA = {
    "PL1_Strategy": [
        "https://www.youtube.com/watch?v=5RtgblzXQ7E",
        "https://www.youtube.com/watch?v=LgrZnXys86c",
        "https://www.youtube.com/watch?v=rui0-OuNWmY",
        "https://www.youtube.com/watch?v=O5CAWmov9K8",
        "https://www.youtube.com/watch?v=aVAjCLO_LS0",
        "https://www.youtube.com/watch?v=FFo6G-gO288",
        "https://www.youtube.com/watch?v=fHr00Y01K5s",
        "https://www.youtube.com/watch?v=S5MSbl2ROqI",
        "https://www.youtube.com/watch?v=uJhxhKoEqdQ",
    ],
    "PL2_Bullrun": [
        "https://www.youtube.com/watch?v=ywaW_3pq8x8",
        "https://www.youtube.com/watch?v=T6EBy_LPQcY",
        "https://www.youtube.com/watch?v=kh-hoddH0Bk",
        "https://www.youtube.com/watch?v=SiguKsCDAq8",
        "https://www.youtube.com/watch?v=qfgplQVbcuY",
        "https://www.youtube.com/watch?v=sXS4v3Plo4c",
        "https://www.youtube.com/watch?v=d4MVrmX7bis",
        "https://www.youtube.com/watch?v=HoF6DRfH3Vg",
        "https://www.youtube.com/watch?v=z6F7vkPOdhE",
        "https://www.youtube.com/watch?v=BOHAF5PIT2g",
        "https://www.youtube.com/watch?v=-u3A8fEf0so",
        "https://www.youtube.com/watch?v=0K16TeRzIF4",
        "https://www.youtube.com/watch?v=LZ0XjxhCKp8",
        "https://www.youtube.com/watch?v=347XUVQ75C0",
        "https://www.youtube.com/watch?v=sW0Ke_uI_HM",
        "https://www.youtube.com/watch?v=O7vkTr4g6Hw",
        "https://www.youtube.com/watch?v=oBvd87A7Y20",
        "https://www.youtube.com/watch?v=8i8SAqeoHx4",
        "https://www.youtube.com/watch?v=gHreTOdbuB4",
        "https://www.youtube.com/watch?v=rHd6PMMrhrc",
        "https://www.youtube.com/watch?v=a5V0Y1IG2Lo",
        "https://www.youtube.com/watch?v=fTIg_mBjCWM",
        "https://www.youtube.com/watch?v=V7NEHl9jBI8",
        "https://www.youtube.com/watch?v=nQyySMFflYA",
        "https://www.youtube.com/watch?v=DJj8_j7JB-c",
        "https://www.youtube.com/watch?v=K81nsMTxuPo",
        "https://www.youtube.com/watch?v=VRCDjwV8jBs",
        "https://www.youtube.com/watch?v=m_Ex35tZ5Tg",
        "https://www.youtube.com/watch?v=HDoQHqF0qto",
        "https://www.youtube.com/watch?v=J5tlsjYj-MU",
        "https://www.youtube.com/watch?v=-y21ocqBtZA",
        "https://www.youtube.com/watch?v=u39fbxnJqQQ",
        "https://www.youtube.com/watch?v=y_FsgM7RVNI",
        "https://www.youtube.com/watch?v=fsJGVj_zLJo",
        "https://www.youtube.com/watch?v=LbbAZxPaW8A",
        "https://www.youtube.com/watch?v=ioD6xhmT2Es",
        "https://www.youtube.com/watch?v=y6bcCYZ2j6w",
        "https://www.youtube.com/watch?v=WnBWfix-GpU",
        "https://www.youtube.com/watch?v=7DBmLGSKCgM",
        "https://www.youtube.com/watch?v=m-Bsy0GCjE0",
    ],
    "PL3_Basic": [
        "https://www.youtube.com/watch?v=tX8URf_UZzw",
        "https://www.youtube.com/watch?v=L1Mwl_2zofY",
        "https://www.youtube.com/watch?v=bev5AR8XYkU",
        "https://www.youtube.com/watch?v=9BHBOxcpSBE",
        "https://www.youtube.com/watch?v=BcaKM9uSVu0",
        "https://www.youtube.com/watch?v=N3avE-Z6JjE",
        "https://www.youtube.com/watch?v=S05kdflNYl0",
        "https://www.youtube.com/watch?v=v_oVywG3dwM",
        "https://www.youtube.com/watch?v=KBSq2yQB8UA",
        "https://www.youtube.com/watch?v=uBBSLFYXSsw",
        "https://www.youtube.com/watch?v=zwXoMNPLJcc",
        "https://www.youtube.com/watch?v=YDcSKITbuyU",
        "https://www.youtube.com/watch?v=gk3TcSyer4s",
        "https://www.youtube.com/watch?v=6niurbOhhBs",
        "https://www.youtube.com/watch?v=SiguKsCDAq8",
        "https://www.youtube.com/watch?v=kF-o_9sk82k",
        "https://www.youtube.com/watch?v=fI-zGuuz_JM",
        "https://www.youtube.com/watch?v=JE62PEQfgWc",
        "https://www.youtube.com/watch?v=hvr5zJxcQ_o",
        "https://www.youtube.com/watch?v=9leQIhJXezw",
        "https://www.youtube.com/watch?v=gHreTOdbuB4",
        "https://www.youtube.com/watch?v=AlTJUk0N6qA",
        "https://www.youtube.com/watch?v=BPb8UxuN6Pc",
        "https://www.youtube.com/watch?v=EKlbAuH4aB8",
        "https://www.youtube.com/watch?v=94B9HdzOOjE",
        "https://www.youtube.com/watch?v=MEcW4Hm4cko",
        "https://www.youtube.com/watch?v=owzIvbVdE8w",
        "https://www.youtube.com/watch?v=GvReDYmaQeY",
        "https://www.youtube.com/watch?v=4h-nJMwCXDY",
        "https://www.youtube.com/watch?v=CRDnOwINpc8",
        "https://www.youtube.com/watch?v=XTnmHvCJLTA",
        "https://www.youtube.com/watch?v=0exTXE0MF9s",
        "https://www.youtube.com/watch?v=gFODVl7fsik",
        "https://www.youtube.com/watch?v=MUnWWmsk1e0",
        "https://www.youtube.com/watch?v=JXwWspvOVAQ",
        "https://www.youtube.com/watch?v=wYgoBDa9IlA",
        "https://www.youtube.com/watch?v=9BYWa6V0rnw",
        "https://www.youtube.com/watch?v=6QwwFC3MPHA",
        "https://www.youtube.com/watch?v=1yIre35Kp4Q",
        "https://www.youtube.com/watch?v=kh-hoddH0Bk",
        "https://www.youtube.com/watch?v=ku_iQIekPr4",
        "https://www.youtube.com/watch?v=Elt4CxFdgP4",
        "https://www.youtube.com/watch?v=GyHXekvfzZE",
        "https://www.youtube.com/watch?v=ayhS3LDtw0w",
        "https://www.youtube.com/watch?v=DZQhYtFC2_8",
        "https://www.youtube.com/watch?v=ET5RbiaYbpg",
        "https://www.youtube.com/watch?v=iAvt0oqAIkY",
        "https://www.youtube.com/watch?v=9zG2eedIvCs",
        "https://www.youtube.com/watch?v=OSe8aGk5ibY",
        "https://www.youtube.com/watch?v=sFZhVAY7N0Y",
        "https://www.youtube.com/watch?v=NJ0VcsrEuos",
        "https://www.youtube.com/watch?v=sFGu5TQ-qCo",
        "https://www.youtube.com/watch?v=MeLQfs4b8H0",
        "https://www.youtube.com/watch?v=rIOvU6PSd8E",
        "https://www.youtube.com/watch?v=Vmy7d25t6pw",
        "https://www.youtube.com/watch?v=Jn3BxCwO--c",
        "https://www.youtube.com/watch?v=9oBI5lPwltY",
        "https://www.youtube.com/watch?v=Rwm9f3pZd08",
        "https://www.youtube.com/watch?v=yE9mKgxJcwU",
        "https://www.youtube.com/watch?v=Uo5w_EzlTIk",
        "https://www.youtube.com/watch?v=2hjftGE8sB8",
        "https://www.youtube.com/watch?v=h_dYdA0bC_c",
        "https://www.youtube.com/watch?v=IhMPuDZuoxU",
        "https://www.youtube.com/watch?v=z6F7vkPOdhE",
        "https://www.youtube.com/watch?v=ArejlRH3r_A",
        "https://www.youtube.com/watch?v=irO2p9P6wLQ",
        "https://www.youtube.com/watch?v=5BmcE2X-9Vk",
        "https://www.youtube.com/watch?v=eNfuoAKVRn8",
        "https://www.youtube.com/watch?v=os9ZyARvCDE",
        "https://www.youtube.com/watch?v=t3aIDxJUSA8",
        "https://www.youtube.com/watch?v=BGeUAjcJHQQ",
        "https://www.youtube.com/watch?v=9VvIOGwwZ2U",
        "https://www.youtube.com/watch?v=O4LikOws9Pg",
        "https://www.youtube.com/watch?v=-Nk0MaMGOvI",
        "https://www.youtube.com/watch?v=el5wh7EhEfM",
        "https://www.youtube.com/watch?v=TctHRwfoXjg",
        "https://www.youtube.com/watch?v=yvczNRp68wA",
        "https://www.youtube.com/watch?v=SL61gvchUJ4",
        "https://www.youtube.com/watch?v=_6jIBHq-loI",
        "https://www.youtube.com/watch?v=neakIPUrT24",
        "https://www.youtube.com/watch?v=LkeGoHJzw2U",
        "https://www.youtube.com/watch?v=3OmWhOHjHFQ",
        "https://www.youtube.com/watch?v=NSDUiExPzQA",
        "https://www.youtube.com/watch?v=KWXYGpTvhMk",
        "https://www.youtube.com/watch?v=EjOVN3gaFkk",
        "https://www.youtube.com/watch?v=1JY0k3XAsTw",
        "https://www.youtube.com/watch?v=OXJEyvX3WX8",
        "https://www.youtube.com/watch?v=jCkHkNegvlw",
        "https://www.youtube.com/watch?v=ykzMw0hYoi4",
        "https://www.youtube.com/watch?v=6vL1li53_yk",
        "https://www.youtube.com/watch?v=zJQ77lRRcFY",
        "https://www.youtube.com/watch?v=K1gReIMIWmg",
        "https://www.youtube.com/watch?v=XZgEB_oz0No",
        "https://www.youtube.com/watch?v=i6JBcH6cSyA",
        "https://www.youtube.com/watch?v=TqkepgyTLZk",
        "https://www.youtube.com/watch?v=wzuHo69uF4Y",
        "https://www.youtube.com/watch?v=TwXZu4FGEwU",
        "https://www.youtube.com/watch?v=VJofewtla0g",
        "https://www.youtube.com/watch?v=CjpzTWZTt9I",
        "https://www.youtube.com/watch?v=foegve8-hko",
        "https://www.youtube.com/watch?v=iB7tDkS577w",
        "https://www.youtube.com/watch?v=nxnsDlk3yG0",
        "https://www.youtube.com/watch?v=ifZv3-eWKjg",
        "https://www.youtube.com/watch?v=T6EBy_LPQcY",
        "https://www.youtube.com/watch?v=y_FsgM7RVNI",
        "https://www.youtube.com/watch?v=fsJGVj_zLJo",
        "https://www.youtube.com/watch?v=_ubjbLPpbHo",
        "https://www.youtube.com/watch?v=sFms3NdlHqo",
        "https://www.youtube.com/watch?v=wldt19DPIoI",
        "https://www.youtube.com/watch?v=2BluCMI_fOo",
        "https://www.youtube.com/watch?v=eFMRpUUXGak",
        "https://www.youtube.com/watch?v=ywaW_3pq8x8",
        "https://www.youtube.com/watch?v=EV0pnULVVoo",
        "https://www.youtube.com/watch?v=QazmXGKXq5c",
        "https://www.youtube.com/watch?v=J4qdZWwrI8A",
        "https://www.youtube.com/watch?v=qd0xjIaQEuI",
        "https://www.youtube.com/watch?v=sz_Sy8C4hW0",
        "https://www.youtube.com/watch?v=y9CLWNkhi5w",
        "https://www.youtube.com/watch?v=pcfw8Fr6trI",
        "https://www.youtube.com/watch?v=xXmSljpp_hY",
    ],
    "PL4_Intermediate": [
        "https://www.youtube.com/watch?v=Ox5Mlas8n4g",
        "https://www.youtube.com/watch?v=btRFwk458CY",
        "https://www.youtube.com/watch?v=tD_1kj56Yf4",
        "https://www.youtube.com/watch?v=QXSqaS0o5rQ",
        "https://www.youtube.com/watch?v=Avl2PMZpE5E",
        "https://www.youtube.com/watch?v=wSNUrSVbGgk",
        "https://www.youtube.com/watch?v=6cDPDdbILJo",
        "https://www.youtube.com/watch?v=lx9FjULj4zI",
        "https://www.youtube.com/watch?v=BGy5-nSq1sU",
        "https://www.youtube.com/watch?v=8zTZOUwydfo",
        "https://www.youtube.com/watch?v=D74ckSnFdOA",
        "https://www.youtube.com/watch?v=sUn8l1IDxto",
        "https://www.youtube.com/watch?v=2uisqvCbdqQ",
        "https://www.youtube.com/watch?v=TYq76JRO_DU",
        "https://www.youtube.com/watch?v=ay46KhAOdRc",
        "https://www.youtube.com/watch?v=hGFgm2ryTKU",
        "https://www.youtube.com/watch?v=Xv2Del2i30Y",
        "https://www.youtube.com/watch?v=g9il3wBh3Eo",
        "https://www.youtube.com/watch?v=Fch4Wx6SAtk",
        "https://www.youtube.com/watch?v=nECdV9HBVHo",
        "https://www.youtube.com/watch?v=cn8lV0__Jtg",
        "https://www.youtube.com/watch?v=pETk-x9Qs7w",
        "https://www.youtube.com/watch?v=HVmymb-Cm7I",
        "https://www.youtube.com/watch?v=PDkk1L_S8pI",
        "https://www.youtube.com/watch?v=cJqZ9JJvC-8",
        "https://www.youtube.com/watch?v=S7g7qz8KitU",
        "https://www.youtube.com/watch?v=dnVa9zyz4QE",
        "https://www.youtube.com/watch?v=aW0iTAr2BH0",
        "https://www.youtube.com/watch?v=XSpB0gk1KbQ",
        "https://www.youtube.com/watch?v=2T79KMVd2IA",
        "https://www.youtube.com/watch?v=id1wZl9PLso",
        "https://www.youtube.com/watch?v=XKkYZ_vzRFs",
        "https://www.youtube.com/watch?v=ouPafQ70zWA",
        "https://www.youtube.com/watch?v=Ac0boGq6OCk",
        "https://www.youtube.com/watch?v=wUz9yks5TNU",
        "https://www.youtube.com/watch?v=7i933aANImI",
        "https://www.youtube.com/watch?v=B31EZsSRAak",
        "https://www.youtube.com/watch?v=Iqkhuo9bWXo",
        "https://www.youtube.com/watch?v=0MGAPsaT8x8",
        "https://www.youtube.com/watch?v=fGArARwlo08",
        "https://www.youtube.com/watch?v=0T6CJsTzmSk",
        "https://www.youtube.com/watch?v=5_TO9QGCDEo",
        "https://www.youtube.com/watch?v=Bx2fHbaLY14",
        "https://www.youtube.com/watch?v=_j3CBJatzv4",
        "https://www.youtube.com/watch?v=XDyWVBqmFPw",
        "https://www.youtube.com/watch?v=uhXnoPQycNM",
        "https://www.youtube.com/watch?v=1_mE0ELUqPk",
        "https://www.youtube.com/watch?v=GQh9HdCZvOM",
        "https://www.youtube.com/watch?v=fdGhyUFHJ5I",
        "https://www.youtube.com/watch?v=jFmeVYA76Dc",
        "https://www.youtube.com/watch?v=Qy8yHx7qD80",
        "https://www.youtube.com/watch?v=58Bv_3LSJmg",
        "https://www.youtube.com/watch?v=6r4GS89Stb0",
        "https://www.youtube.com/watch?v=jVBg_wp601U",
        "https://www.youtube.com/watch?v=EgsSbii_3cM",
        "https://www.youtube.com/watch?v=9LN9LiYhCyI",
        "https://www.youtube.com/watch?v=sYHqjzVpIPA",
        "https://www.youtube.com/watch?v=Ak-W_INGFwM",
        "https://www.youtube.com/watch?v=i0hxq2z7xp8",
        "https://www.youtube.com/watch?v=3pJaAzsNoT4",
        "https://www.youtube.com/watch?v=LUKndyla_jg",
        "https://www.youtube.com/watch?v=wX5CdZUCSNI",
        "https://www.youtube.com/watch?v=ghinfD6eOiA",
        "https://www.youtube.com/watch?v=HysicEWb5qw",
        "https://www.youtube.com/watch?v=3los1H5WKQI",
        "https://www.youtube.com/watch?v=oWQ9-LE72eE",
        "https://www.youtube.com/watch?v=ERoPVEL3Kf8",
        "https://www.youtube.com/watch?v=S6jEq884Xyk",
        "https://www.youtube.com/watch?v=X9Mc2asfibs",
        "https://www.youtube.com/watch?v=7wJPxo9AAgk",
        "https://www.youtube.com/watch?v=0v_aJVJF1qQ",
        "https://www.youtube.com/watch?v=_XwLovb2rWg",
        "https://www.youtube.com/watch?v=ZABjFGPQ-hA",
        "https://www.youtube.com/watch?v=az6gdTZL_oU",
        "https://www.youtube.com/watch?v=NYVBTbdIjfQ",
        "https://www.youtube.com/watch?v=x-K7LzbF-U0",
        "https://www.youtube.com/watch?v=Aj7mAzGHB3Y",
        "https://www.youtube.com/watch?v=WP9-kSm4DbM",
        "https://www.youtube.com/watch?v=UYIBDJkh5O0",
        "https://www.youtube.com/watch?v=8SqhmxQSfNY",
        "https://www.youtube.com/watch?v=Lhq_ef4HYNc",
        "https://www.youtube.com/watch?v=oPBMtzs7XYk",
        "https://www.youtube.com/watch?v=SpICWWNeWA4",
        "https://www.youtube.com/watch?v=TSaB__zRM1g",
        "https://www.youtube.com/watch?v=sLPJttDd5pA",
        "https://www.youtube.com/watch?v=4tyziOE0wmU",
        "https://www.youtube.com/watch?v=5uYTEZ3qzKA",
        "https://www.youtube.com/watch?v=j9ejHpBrslU",
        "https://www.youtube.com/watch?v=RtpCzkJoz2Y",
        "https://www.youtube.com/watch?v=sv3uBzVg68E",
        "https://www.youtube.com/watch?v=tqAwY0j9Ot4",
        "https://www.youtube.com/watch?v=YlKT4vzBY8k",
        "https://www.youtube.com/watch?v=DxZ0PmNzEZo",
        "https://www.youtube.com/watch?v=aWVC4rxKGo0",
        "https://www.youtube.com/watch?v=qfgplQVbcuY",
        "https://www.youtube.com/watch?v=nPxzbDpCpNA",
        "https://www.youtube.com/watch?v=55W7TQeqNf8",
        "https://www.youtube.com/watch?v=cFEIvYqjE64",
        "https://www.youtube.com/watch?v=eGn7vICr55k",
        "https://www.youtube.com/watch?v=tplgMnSD8qs",
        "https://www.youtube.com/watch?v=-u3A8fEf0so",
        "https://www.youtube.com/watch?v=nIDcQTgPG5M",
        "https://www.youtube.com/watch?v=zw90iCX4ZEM",
        "https://www.youtube.com/watch?v=3bnVEwTr8Cs",
        "https://www.youtube.com/watch?v=K81nsMTxuPo",
        "https://www.youtube.com/watch?v=T6EBy_LPQcY",
        "https://www.youtube.com/watch?v=MFNkP4IHzzg",
        "https://www.youtube.com/watch?v=ioD6xhmT2Es",
        "https://www.youtube.com/watch?v=GapzlVH_WQY",
        "https://www.youtube.com/watch?v=SJ9m5d4rX5A",
        "https://www.youtube.com/watch?v=zDw9Rq6LcfI",
    ],
}

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()[:70]

def build_ydl_opts(client_list, proxy="socks5://127.0.0.1:40000"):
    return {
        "proxy": proxy,
        "socket_timeout": 30,
        "retries": 10,
        "fragment_retries": 10,
        "continuedl": True,
        "quiet": True,
        "no_warnings": True,
        "cookiefile": COOKIE_FILE,
        "extractor_args": {
            "youtube": {
                "player_client": client_list
            }
        }
    }

def process_video(url: str, category_dir: Path, round_num: int) -> bool:
    clients = CLIENT_PROFILES[min(round_num - 1, len(CLIENT_PROFILES) - 1)]
    base_opts = build_ydl_opts(clients)

    # تاخیر تطبیقی: هرچه دور بالاتر باشد، مکث بیشتر می‌شود تا حساسیت یوتیوب فروکش کند
    time.sleep(random.uniform(2.0, 3.5 + (round_num * 1.5)))

    try:
        with yt_dlp.YoutubeDL(base_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_id = info.get("id", "video")
            raw_title = info.get("title", video_id)
            duration = info.get("duration", 0)
    except Exception as e:
        logger.warning(f"[R{round_num}] Metadata error for {url}: {e}")
        return False

    safe_title = sanitize_filename(raw_title)
    video_dir = category_dir / f"{video_id}_{safe_title}"
    done_marker = video_dir / ".completed"

    if done_marker.exists():
        logger.info(f"  -> Already verified. Skipping {video_id}.")
        return True

    video_dir.mkdir(parents=True, exist_ok=True)

    try:
        # ۱. دانلود فایل صوتی و متادیتا
        opts_audio = dict(base_opts)
        opts_audio.update({
            "format": "ba[ext=m4a]/ba/b",
            "outtmpl": str(video_dir / "01_audio.%(ext)s"),
            "writeinfojson": True,
        })
        with yt_dlp.YoutubeDL(opts_audio) as ydl:
            ydl.download([url])

        for j in video_dir.glob("*.info.json"):
            j.replace(video_dir / "03_metadata.json")

        # ۲. دانلود موقت ۳۶۰p برای استخراج چارت
        temp_vid = video_dir / "temp_video.mp4"
        keyframes_dir = video_dir / "02_keyframes"
        keyframes_dir.mkdir(exist_ok=True)

        opts_video = dict(base_opts)
        opts_video.update({
            "format": "bv[height<=360][ext=mp4]/bv[height<=360]/worstvideo",
            "outtmpl": str(temp_vid),
        })
        with yt_dlp.YoutubeDL(opts_video) as ydl:
            ydl.download([url])

        # ۳. استخراج یک فریم در هر ۳۰ ثانیه چارت
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", str(temp_vid),
            "-vf", "fps=1/30",
            "-q:v", "2",
            str(keyframes_dir / "frame_%06ds.jpg"),
        ]
        subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        frames = sorted(keyframes_dir.glob("*.jpg"))
        for f_idx, f_path in enumerate(frames, start=1):
            sec = f_idx * 30
            f_path.rename(keyframes_dir / f"frame_{sec:06d}s.jpg")

        if temp_vid.exists():
            temp_vid.unlink()

        # علامت‌گذاری تایید سلامت کامل ویدیو
        done_marker.touch()

        audio_file = next(video_dir.glob("01_audio.*"), None)
        manifest_record = {
            "video_id": video_id,
            "title": raw_title,
            "category": category_dir.name,
            "duration": duration,
            "audio_file": str(audio_file.name) if audio_file else None,
            "keyframes_count": len(frames),
        }
        manifest_path = category_dir / "manifest_part.jsonl"
        with open(manifest_path, "a", encoding="utf-8") as mf:
            mf.write(json.dumps(manifest_record, ensure_ascii=False) + "\n")

        logger.info(f"  ✅ [SUCCESS] {video_id} ({len(frames)} frames extracted)")
        return True

    except Exception as e:
        logger.warning(f"  ⚠️ Error processing {video_id} in Round {round_num}: {e}")
        shutil.rmtree(video_dir, ignore_errors=True)
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", type=str, required=True, help="Category name to process")
    args = parser.parse_args()

    cat_name = args.category
    if cat_name not in VIDEOS_DATA:
        logger.error(f"Unknown category: {cat_name}")
        sys.exit(1)

    urls = VIDEOS_DATA[cat_name]
    cat_dir = BASE_DIR / cat_name
    cat_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"🚀 Starting Dedicated Runner for: {cat_name} ({len(urls)} videos)")

    remaining_urls = list(urls)
    round_num = 1
    max_rounds = 3

    # موتور پاکسازی و تلاش مجدد (Multi-Round Sweeper)
    while remaining_urls and round_num <= max_rounds:
        logger.info(f"\n🔄 === [ROUND {round_num}/{max_rounds}] Remaining Videos: {len(remaining_urls)} ===")
        still_failed = []

        for idx, u in enumerate(remaining_urls, start=1):
            logger.info(f"[{idx}/{len(remaining_urls)}] Round {round_num} -> {u}")
            success = process_video(u, cat_dir, round_num)
            if not success:
                still_failed.append(u)

        remaining_urls = still_failed
        if remaining_urls:
            wait_sec = round_num * 15
            logger.info(f"⏳ Waiting {wait_sec}s before starting Round {round_num + 1}...")
            time.sleep(wait_sec)
        round_num += 1

    # ایجاد خروجی ZIP دسته‌بندی
    logger.info(f"\n📦 Compressing final dataset archive for {cat_name}...")
    zip_name = f"{cat_name}_dataset"
    shutil.make_archive(zip_name, 'zip', BASE_DIR, cat_name)
    logger.info(f"✅ Created: {zip_name}.zip")

    if remaining_urls:
        logger.warning(f"⚠️ {len(remaining_urls)} videos were incomplete after {max_rounds} rounds.")
    else:
        logger.info(f"🎉 100% of videos in {cat_name} downloaded successfully!")

if __name__ == "__main__":
    main()
