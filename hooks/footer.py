"""푸터의 저작권 문구 안에 있는 {build_date}를 빌드한 날짜(한국 시간)로 바꾼다."""
from datetime import datetime
from zoneinfo import ZoneInfo


def on_config(config):
    if config.copyright and "{build_date}" in config.copyright:
        today = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")
        config.copyright = config.copyright.replace("{build_date}", today)
    return config
