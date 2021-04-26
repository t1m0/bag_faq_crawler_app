import logging

from .crawler import Crawler
from .watson import WatsonWrapper


class BagFaqCrawler:

    def __init__(self, watson_api_key, watson_skill_id, watson_workspace_url, bag_faq_url):
        self.watson = WatsonWrapper(watson_skill_id, watson_api_key, watson_workspace_url)
        self.crawler = Crawler(bag_faq_url, self.callback)

    def crawl(self):
        logging.basicConfig(level=logging.INFO)
        self.existing_dialog_nodes = self.watson.listDialogNodes()
        self.ensure_faq_folder_present()
        self.crawler.crawl()

    def ensure_faq_folder_present(self):
        if 'faq' not in self.existing_dialog_nodes.keys():
            self.watson.create_dialog_folder('faq','FAQ')


    def callback(self, uuid, link, question, answer):
        if uuid not in self.existing_dialog_nodes.keys():
            logging.info("Adding " + uuid + "to watson assitant")
            self.watson.createIntent(uuid, question)
            self.watson.createDialogNode(uuid, question, answer)
        else:
            logging.info("Not adding " + uuid + "to watson assitant, since it's already present")
