import logging

from crawler import Crawler
from watson import WatsonWrapper


class BagFaqCrawler:
    BAG_MARKER = ' (BAG)'
    MAX_ANSWER_LENGTH = 10
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
        question_with_marker = question + self.BAG_MARKER
        short_answer = self.shorten_answer(answer)
        if uuid not in self.existing_dialog_nodes.keys():
            logging.info("Adding " + uuid + "to watson assitant")
            self.watson.createIntent(uuid, question_with_marker)
            self.watson.createDialogNode(uuid, question_with_marker, short_answer)
        elif self.existing_entry_has_changed(self.existing_dialog_nodes[uuid], question_with_marker, short_answer):
            logging.info("Question or Answer for " + uuid + " changed, therefore updating watson assistant.")
            self.update_watson(uuid, question_with_marker, short_answer)
            del self.existing_dialog_nodes[uuid]
        else:
            logging.info("Not adding " + uuid + " to watson assistant, since it's already present.")
            del self.existing_dialog_nodes[uuid]

    def shorten_answer(self, answer):
        cut_index = answer.find('.')
        if cut_index <= 0 and self.MAX_ANSWER_LENGTH < len(answer):
            cut_index = self.MAX_ANSWER_LENGTH
        elif cut_index <= 0:
            cut_index = len(answer)
        return answer[0:cut_index+1] + ' ...'

    def existing_entry_has_changed(self, existing_dialog_node, question, answer):
        return question != existing_dialog_node['question'] or answer != existing_dialog_node['answer']

    def update_watson(self, uuid, question, answer):
        current_intent = self.watson.get_intent(uuid)
        for example in current_intent['examples']:
            if self.BAG_MARKER in example['text']:
                example['text'] = question
                break
        current_intent['description'] = question
        self.watson.update_intent(current_intent)
        self.watson.update_dialog_node(uuid, question, answer)

    def remove_no_longer_valid_faq_entries(self):
        for node in self.existing_dialog_nodes:
            logging.info("Deleting " + node + " since it's no longer present on bag page.")
            self.watson.delete_dialog_node(node)
            self.watson.delete_intent(node)
