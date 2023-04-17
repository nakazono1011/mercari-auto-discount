import logging
import argparse
from factory import CrawlerFactory

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

def before_send(event, hint):
    # 'exception' キーが存在する場合、Exception をキャプチャしているイベントです。
    # これを捨てることで、logger.error を使ってのみエラーを検知するようになります。
    if 'exception' in event:
        return None
    return event

sentry_logging = LoggingIntegration(
    level=logging.ERROR,        # エラーレベルのみキャプチャ
    event_level=logging.ERROR   # エラーレベルのイベントを Sentry に送信
)

sentry_sdk.init(
    dsn="https://728c5487e6ae49f6a76f0943f18d13a7@o4504950406250496.ingest.sentry.io/4504950409986048",
    traces_sample_rate=1.0,
    integrations=[sentry_logging],
    before_send=before_send,
)

# python main.py -m {mode}
# 1 discount
# 2 weekly_comment_create
# 3 weekly_comment_delete

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", "-m", type=str)
    args = parser.parse_args()

    crawler = CrawlerFactory().create(args.mode)
    crawler.crawl()
