import unittest
from unittest.mock import Mock, patch

from selenium.webdriver.common.by import By

from crawler.mercari.discount_crawler import (
    DiscountCrawler,
    item_url_to_edit_url,
)


class ItemUrlToEditUrlTest(unittest.TestCase):
    def test_converts_item_url_to_sell_edit_url(self):
        self.assertEqual(
            item_url_to_edit_url("https://jp.mercari.com/item/m96706433110"),
            "https://jp.mercari.com/sell/edit/m96706433110",
        )

    def test_returns_none_when_item_id_is_missing(self):
        self.assertIsNone(item_url_to_edit_url("https://jp.mercari.com/mypage/listings"))


class QuitDriverTest(unittest.TestCase):
    def test_quit_driver_does_nothing_when_driver_is_none(self):
        crawler = DiscountCrawler()
        crawler.driver = None
        crawler._quit_driver()
        self.assertIsNone(crawler.driver)

    def test_quit_driver_closes_and_clears_driver(self):
        crawler = DiscountCrawler()
        driver = Mock()
        crawler.driver = driver
        crawler._quit_driver()
        driver.quit.assert_called_once()
        self.assertIsNone(crawler.driver)

    def test_quit_driver_clears_driver_even_if_quit_raises(self):
        crawler = DiscountCrawler()
        driver = Mock()
        driver.quit.side_effect = Exception("no such window")
        crawler.driver = driver
        crawler._quit_driver()
        self.assertIsNone(crawler.driver)


class UpdateAllDriverReuseTest(unittest.TestCase):
    @patch("crawler.mercari.discount_crawler.time.sleep", return_value=None)
    def test_restarts_driver_when_window_is_closed(self, _sleep):
        crawler = DiscountCrawler()
        driver = Mock()
        driver.find_element.side_effect = Exception(
            "no such window: target window already closed"
        )
        crawler.driver = driver
        crawler._quit_driver = Mock(wraps=crawler._quit_driver)

        crawler._update_all(["https://jp.mercari.com/item/m1"])

        crawler._quit_driver.assert_called_once()
        self.assertIsNone(crawler.driver)

    @patch("crawler.mercari.discount_crawler.time.sleep", return_value=None)
    def test_does_not_quit_driver_after_item_error(self, _sleep):
        crawler = DiscountCrawler()
        driver = Mock()
        driver.find_element.side_effect = Exception("no such element")
        crawler.driver = driver

        crawler._update_all(["https://jp.mercari.com/item/m1"])

        driver.quit.assert_not_called()
        self.assertIs(crawler.driver, driver)

    @patch("crawler.mercari.discount_crawler.time.sleep", return_value=None)
    def test_does_not_quit_driver_after_successful_item(self, _sleep):
        crawler = DiscountCrawler()
        driver = Mock()
        name_el = Mock()
        name_el.get_attribute.return_value = "靴"
        price_el = Mock()
        price_el.get_attribute.return_value = "2000"
        edit_button = Mock()

        def find_element(by, value):
            if by == By.NAME and value == "name":
                return name_el
            if by == By.CSS_SELECTOR and "price" in value:
                return price_el
            if by == By.CSS_SELECTOR and "edit-button" in value:
                return edit_button
            raise AssertionError((by, value))

        driver.find_element.side_effect = find_element
        crawler.driver = driver
        crawler._confirm_image_creation_if_needed = Mock()
        crawler._safe_click = Mock()

        crawler._update_all(["https://jp.mercari.com/item/m1"])

        driver.get.assert_called_once_with("https://jp.mercari.com/sell/edit/m1")
        driver.quit.assert_not_called()
        self.assertIs(crawler.driver, driver)
        price_el.send_keys.assert_called()
