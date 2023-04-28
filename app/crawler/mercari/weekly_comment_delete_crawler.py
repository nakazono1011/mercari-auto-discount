import time
import random

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from crawler.mercari import BaseCrawler
from logger import get_module_logger

logger = get_module_logger(__name__)


class WeeklyCommentDeleteCrawler(BaseCrawler):
    START_URL = "https://jp.mercari.com/mypage/listings"
    # 最低いいね数
    MIN_LIKE_COUNT = 2
    # 削除対象の判定文字列
    DELETE_TARGET_CHARCTER = "★"

    def _delete_comment_all(self, target_urls):
        for target_url in target_urls:
            try:
                self.driver.get(target_url)

                time.sleep(random.randint(1, 4))

                item_name = self.driver.find_element(
                    By.CSS_SELECTOR, 'div[data-testid="name"]'
                ).text

                try:
                    wait = WebDriverWait(self.driver, 1)
                    element = wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//button[contains(text(), 'コメントをもっと見る')]")
                        )
                    )

                    element.click()
                except:
                    pass

                comment_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, "[data-testid='comment-list']"
                )

                for comment_element in comment_elements:
                    if (
                        self.DELETE_TARGET_CHARCTER
                        in comment_element.find_element(
                            By.CSS_SELECTOR, "[class*='contentContainer']"
                        ).text
                    ):

                        comment_element.find_element(
                            By.CSS_SELECTOR, "mer-icon-button"
                        ).click()

                        self.driver.find_elements(
                            By.CSS_SELECTOR, "mer-dialog .merButton"
                        )[-1].click()

                        time.sleep(3)

                logger.info(f"[商品名] {item_name} [イベント] 週末セールコメント削除完了")

            except Exception as e:
                logger.error(f"[商品名] {item_name} [例外エラー] {e}")
                continue

    def _scrape_target_urls(self):
        """
        コメント対象のURLを生成する
        """

        # 商品リストの要素を取得
        listed_item_element = self.driver.find_element(
            By.CSS_SELECTOR, "[data-testid='listed-item-list']"
        )
        item_list = listed_item_element.find_elements(By.CSS_SELECTOR, "[data-testid='merListItem-container']")

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

        time.sleep(5)

        # 出品リストをロード
        self._load_more()

        # 週末コメント削除対象のURLを取得
        target_urls = self._scrape_target_urls()

        # コメント削除処理
        self._delete_comment_all(target_urls)
        logger.info(f"[削除件数] {len(target_urls)}件")

        self.driver.quit()
        logger.info(f"[イベント] 処理完了")
