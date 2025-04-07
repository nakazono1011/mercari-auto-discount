import re
import time
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from crawler.mercari import BaseCrawler
from logger import get_module_logger

logger = get_module_logger(__name__)


class SyncNeCrawler(BaseCrawler):
    START_URL = "https://jp.mercari.com/mypage/listings"

    def _scrape_target_urls(self):
        """
        連携対象のURLを生成する
        """

        # 商品リストの要素を取得
        listed_item_element = self.driver.find_element(
            By.CSS_SELECTOR, "[data-testid='listed-item-list']"
        )
        item_list = listed_item_element.find_elements(
            By.CSS_SELECTOR, "[data-testid='listed-item']"
        )

        # 要素内の値引き対象のURLを取得
        item_urls = []
        for el in item_list:
            item_url = el.find_element(By.TAG_NAME, "a").get_attribute("href")
            item_urls.append(item_url)

        return item_urls

    def _update_all(self, target_urls):
        """
        対象の商品について値下げを実行する処理
        """
        for target_url in target_urls:
            try:
                self.driver.get(target_url)
                time.sleep(random.randint(1, 2))

                edit_url = self.driver.find_element(
                    By.CSS_SELECTOR, "[data-testid='checkout-button']>a"
                ).get_attribute("href")

                self.driver.get(edit_url)
                time.sleep(random.randint(1, 2))

                item_name = self.driver.find_element(By.NAME, "name").get_attribute(
                    "value"
                )
                category_name = self.driver.find_element(
                    By.CSS_SELECTOR, "[data-testid='sell-category']"
                ).text.replace("\n", ">")

                brand_name = self.driver.find_element(
                    By.CSS_SELECTOR, "[data-testid='brand-link']>div>p"
                ).text

                condition = self.driver.find_element(
                    By.CSS_SELECTOR, "[name='itemCondition']"
                ).get_attribute("value")

                description = self.driver.find_element(
                    By.CSS_SELECTOR, "[name='description']"
                ).get_attribute("value")

                price = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'input[name="price"]',
                ).get_attribute("value")

                time.sleep(random.randint(1, 2))

            except Exception as e:
                logger.info(f"[商品名] {item_name} [例外エラー] {e}")
                continue

    def crawl(self):
        """
        メイン処理
        """

        logger.info(f"[イベント] 処理開始")
        self.driver = self._load_driver()
        self.driver.get(self.START_URL)

        # 出品リストをロード
        self._load_more()

        # 値下げ対象の出品リストを取得
        target_urls = self._scrape_target_urls()

        # 値下げ処理
        self._update_all(target_urls)
        logger.info(f"[更新件数] {len(target_urls)}件")

        self.driver.quit()
        logger.info(f"[イベント] 処理完了")
