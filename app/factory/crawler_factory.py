from crawler.mercari import (
    DiscountCrawler,
    WeeklyCommentCreateCrawler,
    WeeklyCommentDeleteCrawler,
)


class CrawlerFactory:
    def __init__(self):
        pass

    def create(self, mode):
        if mode == "discount":
            return DiscountCrawler()
        elif mode == "weekly_comment_create":
            return WeeklyCommentCreateCrawler()
        elif mode == "weekly_comment_delete":
            return WeeklyCommentDeleteCrawler()
        else:
            raise NotImplementedError("実装されていません")
