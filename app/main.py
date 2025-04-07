import argparse
from factory import CrawlerFactory


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
