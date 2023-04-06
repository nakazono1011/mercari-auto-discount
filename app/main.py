import argparse
from factory import CrawlerFactory

# import sentry_sdk

# sentry_sdk.init(
#     dsn="https://728c5487e6ae49f6a76f0943f18d13a7@o4504950406250496.ingest.sentry.io/4504950409986048",
#     traces_sample_rate=1.0,
# )

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
