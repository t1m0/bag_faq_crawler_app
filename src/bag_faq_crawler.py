import logging

from crawler import Crawler
from watson import WatsonWrapper


class BagFaqCrawler:

    def __init__(self, watson_api_key, watson_skill_id, watson_workspace_url, bag_faq_url):
        self.watson = WatsonWrapper(watson_skill_id, watson_api_key, watson_workspace_url)
        self.crawler = Crawler(bag_faq_url, self.callback)

    def crawl(self):
        logging.basicConfig(level=logging.INFO)
        self.existing_dialog_nodes = self.watson.listDialogNodes()
        self.ensure_faq_folder_present()
        self.crawler.crawl()
        self.remove_no_longer_valid_faq_entries()

    def ensure_faq_folder_present(self):
        if 'faq' not in self.existing_dialog_nodes.keys():
            self.watson.create_dialog_folder('faq', 'FAQ')
        else:
            del self.existing_dialog_nodes['faq']

    def callback(self, uuid, link, question, answer):
        if uuid not in self.existing_dialog_nodes.keys():
            logging.info("Adding " + uuid + "to watson assitant")
            self.watson.createIntent(uuid, question)
            self.watson.createDialogNode(uuid, question, answer)
        elif self.existing_entry_has_changed(self.existing_dialog_nodes[uuid], question, answer):
            logging.info("Question or Answer for " + uuid + " changed, therefore updating watson assistant.")
            self.update_watson(uuid, self.existing_dialog_nodes[uuid], question, answer)
            del self.existing_dialog_nodes[uuid]
        else:
            logging.info("Not adding " + uuid + " to watson assistant, since it's already present.")
            del self.existing_dialog_nodes[uuid]

    def existing_entry_has_changed(self, existing_dialog_node, question, answer):
        return question != existing_dialog_node['question'] or answer != existing_dialog_node['answer']

    def update_watson(self, uuid, existing_node, question, answer):
        # for now we only update the dialog node - if the question changes the uuid changes as well
        self.watson.update_dialog_node(uuid, question, answer)

    def remove_no_longer_valid_faq_entries(self):
        for node in self.existing_dialog_nodes:
            logging.info("Deleting " + node + " since it's no longer present on bag page.")
            self.watson.delete_dialog_node(node)
            self.watson.delete_intent(node)
