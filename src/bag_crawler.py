import logging

from src.faq_crawler import FaqCrawler
from src.watson import WatsonWrapper
from src.vaccination_center_crawler import VaccinationCenterCrawler


class BagCrawler:
    BAG_MARKER = ' (BAG)'
    MAX_ANSWER_LENGTH = 140
    MIN_ANSWER_LENGTH = 80
    FAQ_NODE = 'faq'
    SCHEDULE_VACCINATION_NODE = 'how-and-where-can-i-register-vaccination'
    def __init__(self, watson_api_key, watson_skill_id, watson_workspace_url, bag_faq_url, vaccination_center_url):
        self.watson = WatsonWrapper(watson_skill_id, watson_api_key, watson_workspace_url)
        self.faq_crawler = FaqCrawler(bag_faq_url, self.faq_callback)
        self.vaccination_center_crawler = VaccinationCenterCrawler(vaccination_center_url, self.vaccination_center_callback)

    def crawl(self):
        logging.basicConfig(level=logging.INFO)
        self.existing_faq_entries = self.watson.list_dialog_nodes_for_parent(self.FAQ_NODE)
        self.ensure_faq_folder_present()
        self.faq_crawler.crawl()
        self.remove_no_longer_valid_faq_entries()
        if self.watson.get_dialog_node(self.SCHEDULE_VACCINATION_NODE):
            self.existing_vaccination_centers = self.watson.list_dialog_nodes_for_parent(self.SCHEDULE_VACCINATION_NODE)
            self.vaccination_center_crawler.crawl()

    def ensure_faq_folder_present(self):
        node = self.watson.get_dialog_node(self.FAQ_NODE)
        if node is None:
            self.watson.create_dialog_folder(self.FAQ_NODE, 'FAQ')

    def faq_callback(self, uuid, link, question, answer):
        with_jump = self.SCHEDULE_VACCINATION_NODE != uuid
        question_with_marker = self.limit_question_to_128_characters(question) + self.BAG_MARKER
        short_answer = self.shorten_answer(answer)
        answer_with_link = self.add_link_to_faq(short_answer, link)
        if uuid not in self.existing_faq_entries.keys():
            logging.info("Adding " + uuid + "to watson assitant")
            self.watson.createIntent(uuid, question_with_marker)
            self.watson.createDialogNode(uuid, question_with_marker, answer_with_link, self.FAQ_NODE, with_jump)
        elif self.existing_entry_has_changed(self.existing_faq_entries[uuid], question_with_marker, answer_with_link):
            logging.info("Question or Answer for " + uuid + " changed, therefore updating watson assistant.")
            self.update_watson(uuid, question_with_marker, answer_with_link, with_jump)
            del self.existing_faq_entries[uuid]
        elif self.jump_to_missing(self.existing_faq_entries[uuid], with_jump):
            logging.info("Jump to missing for " + uuid + ", therefore updating watson assistant.")
            self.watson.update_dialog_node(uuid, question_with_marker, answer_with_link, self.FAQ_NODE, with_jump)
            del self.existing_faq_entries[uuid]
        else:
            logging.info("Not adding " + uuid + " to watson assistant, since it's already present.")
            del self.existing_faq_entries[uuid]

    def vaccination_center_callback(self, canton, link, phone):
        uuid = canton.replace(" ","").replace("-","").replace("ü","").replace(".","")
        text = 'You can schedule your vaccination <a target="_blank" href="'+link+'">online</a>'
        if phone:
            text += ' or by phone '+phone
        text += '.'
        if uuid in self.existing_vaccination_centers.keys():
            logging.info("Updating "+canton)
            self.watson.update_dialog_node(uuid,canton,text,self.SCHEDULE_VACCINATION_NODE,True)
        else:
            logging.info("Creating "+canton)
            self.watson.createIntent(uuid,canton)
            self.watson.createDialogNode(uuid,canton,text,self.SCHEDULE_VACCINATION_NODE,True)

    def limit_question_to_128_characters(self, question):
        if len(question) > (128-len(self.BAG_MARKER)):
            logging.warning("Shortening question, since it would exceed the watson limit! Actual question:\n"+question)
            return question[0:122]
        return question

    def shorten_answer(self, answer):
        cut_index = answer.find('.')
        if len(answer) <= self.MAX_ANSWER_LENGTH:
            cut_index = len(answer)
        if cut_index < self.MIN_ANSWER_LENGTH and len(answer) > self.MAX_ANSWER_LENGTH:
            cut_index = self.MAX_ANSWER_LENGTH
        return answer[0:cut_index+1] + ' ...'

    def add_link_to_faq(self, answer, link):
        return answer + '<br/>You can find more details <a target="_blank" href="' + link + '">here</a>.'

    def existing_entry_has_changed(self, existing_dialog_node, question, answer):
        return question != existing_dialog_node['question'] or answer != existing_dialog_node['answer']

    def jump_to_missing(self, existing_dialog_node, jump_to):
        return existing_dialog_node['jump_to_present'] != jump_to

    def update_watson(self, uuid, question, answer, with_jump):
        current_intent = self.watson.get_intent(uuid)
        for example in current_intent['examples']:
            if self.BAG_MARKER in example['text']:
                example['text'] = question
                break
        current_intent['description'] = question
        self.watson.update_intent(current_intent)
        self.watson.update_dialog_node(uuid, question, answer, self.FAQ_NODE, with_jump)

    def remove_no_longer_valid_faq_entries(self):
        for node in self.existing_faq_entries:
            logging.info("Deleting " + node + " since it's no longer present on bag page.")
            self.watson.delete_dialog_node(node)
            self.watson.delete_intent(node)
