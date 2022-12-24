from abc import ABCMeta, abstractclassmethod

from selenium import webdriver
from selenium.webdriver.chrome import service as fs

import config

class BaseCrawler(metaclass=ABCMeta):

    def __init__(self, driver_path=config.DRIVER_PATH, profile_path=config.PROFILE_PATH):
      self.driver_path  = driver_path
      self.profile_path = profile_path
      pass

    def _load_driver(self, driver_path, profile_path):
      """
      driver の起動
      """
      options = webdriver.chrome.options.Options()
      options.add_argument('--user-data-dir=' + profile_path)

      chrome_service = fs.Service(executable_path=driver_path)
      driver = webdriver.Chrome(service=chrome_service, options=options)
      driver.implicitly_wait(15)
      
      return driver
    
    @abstractclassmethod
    def crawl(self):
      raise NotImplementedError("実装されていません")