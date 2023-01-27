import time
import random

from selenium.webdriver.common.by import By

import config
from crawler.mercari import BaseCrawler
from logger import get_module_logger

logger = get_module_logger(__name__)


class WeeklyCommentCreateCrawler(BaseCrawler):
    START_URL = "https://jp.mercari.com/mypage/listings"
    # 最低いいね数
    MIN_LIKE_COUNT = 2

    def _comment_all(self, target_urls):
        for target_url in target_urls:
            try:
                self.driver.get(target_url)

                time.sleep(random.randint(1, 4))

                item_name = self.driver.find_element(
                    By.CSS_SELECTOR, 'div[data-testid="name"]'
                ).text

                self.driver.find_element(By.CSS_SELECTOR, ".input-node").send_keys(
                    config.WEEKLY_SALE_COMMENT
                )

                self.driver.find_element(
                    By.CSS_SELECTOR,
                    "mer-button[data-location='item_details:comment:post_button']",
                ).click()
                logger.info(f"[商品名] {item_name} [イベント] 週末セールコメント登録完了")

            except Exception as e:
                logger.error(f"[商品名] {item_name} [例外エラー] {e}")
                continue

    def _scrape_target_urls(self):
        """
        コメント対象のURLを生成する
        """

        # 商品リストの要素を取得
        listed_item_element = self.driver.find_element(
            By.XPATH, '//*[@id="currentListing"]/mer-list'
        )
        item_list = listed_item_element.find_elements(By.TAG_NAME, "mer-list-item")

        # 要素内のコメント対象のURLを取得
        item_urls = []
        for el in item_list:
            item_root = el.find_element(By.TAG_NAME, "mer-item-object").shadow_root
            like_count = int(item_root.find_element(By.CLASS_NAME, "icon-text").text)
            if like_count < self.MIN_LIKE_COUNT:
                continue

            item_url = el.find_element(By.TAG_NAME, "a").get_attribute("href")
            item_urls.append(item_url)

        return item_urls

    def crawl(self):
        """
        メイン処理
        """
        logger.info(f"[イベント] 処理開始")
        self.driver = self._load_driver()
        self.driver.get(self.START_URL)

        # 出品リストをロード
        self._load_more()

        # 週末コメント対象のURLを取得
        target_urls = self._scrape_target_urls()

        # コメント登録処理
        self._comment_all(target_urls)
        logger.info(f"[更新件数] {len(target_urls)}件")

        self.driver.quit()
        logger.info(f"[イベント] 処理完了")
