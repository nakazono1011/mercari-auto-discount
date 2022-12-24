from crawler.mercari import DiscountCrawler, WeeklyCommentCrawler


class CrawlerFactory:

  def __init__(self):
    pass

  def create(self, mode):
    if mode == "discount":
      return DiscountCrawler()
    elif mode == "weekly_comment":
      return WeeklyCommentCrawler()
    else:
      raise NotImplementedError("実装されていません")

