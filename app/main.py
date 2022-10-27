from crawler import MercariDiscountCrawler
import config

if __name__ == "__main__":
    crawler = MercariDiscountCrawler(config.DRIVER_PATH, config.PROFILE_PATH)
    crawler.crawl()
