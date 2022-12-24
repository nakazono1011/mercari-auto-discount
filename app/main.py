import argparse
from factory import CrawlerFactory

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", "-m", type=str)
    args = parser.parse_args()

    crawler = CrawlerFactory().create(args.mode)
    crawler.crawl()
