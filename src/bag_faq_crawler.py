import logging

from .crawler import Crawler
from .watson import WatsonWrapper


class BagFaqCrawler:

    def __init__(self, watson_api_key, watson_skill_id, watson_workspace_url, bag_faq_url):
        self.watson = WatsonWrapper(watson_skill_id, watson_api_key, watson_workspace_url)
        self.crawler = Crawler(bag_faq_url, self.callback)

    def crawl(self):
        self.crawler.crawl()

    def callback(self, uuid, link, question, answer):
        logging.info("Adding " + uuid)
        self.watson.createIntent(uuid, question)
        self.watson.createDialogNode(uuid, question, answer)
