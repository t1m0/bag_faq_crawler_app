import unittest
import unittest.mock
from bag_faq_crawler import BagFaqCrawler


class TestBagFaqCrawler(unittest.TestCase):
    bag_faq_crawler = BagFaqCrawler("", "", "", "https://www.faq.bag.admin.ch/en/categories/vaccination")
    watson_wrapper = unittest.mock.Mock()
    crawler = unittest.mock.Mock()

    def setUp(self):
        self.bag_faq_crawler.watson = self.watson_wrapper
        self.bag_faq_crawler.crawler = self.crawler

    def test_faq_folder_creation(self):
        self.watson_wrapper.listDialogNodes = unittest.mock.Mock(return_value={})
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.create_dialog_folder.assert_called()

    def test_create_new(self):
        self.watson_wrapper.listDialogNodes = unittest.mock.Mock(return_value={'faq': {}})
        self.crawler.crawl = lambda: self.bag_faq_crawler.callback('test', '', 'question', 'answer')
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.createIntent.assert_called_with('test', 'question')
        self.watson_wrapper.createDialogNode.assert_called_with('test', 'question', 'answer')

    def test_no_change_since_node_already_exists(self):
        self.watson_wrapper.listDialogNodes = unittest.mock.Mock(return_value={'faq': {}, 'test': {'uuid': 'test', 'question': 'question', 'answer': 'answer'}})
        self.crawler.crawl = lambda: self.bag_faq_crawler.callback('test', '', 'question', 'answer')
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.createIntent.assert_not_called()
        self.watson_wrapper.createDialogNode.assert_not_called()

    def test_answer_changed_of_existing_node(self):
        self.watson_wrapper.listDialogNodes = unittest.mock.Mock(return_value={'faq': {}, 'test': {'uuid': 'test', 'question': 'question', 'answer': 'answer'}})
        self.crawler.crawl = lambda: self.bag_faq_crawler.callback('test', '', 'question', 'answer2')
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.update_intent.assert_not_called()
        self.watson_wrapper.update_dialog_node.assert_called_with('test', 'question', 'answer2')

    def test_delete_missing_faq_entry(self):
        self.watson_wrapper.listDialogNodes = unittest.mock.Mock(return_value={'faq': {}, 'test': {'uuid': 'test', 'question': 'question', 'answer': 'answer'}})
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.delete_dialog_node.assert_called_with('test')
        self.watson_wrapper.delete_intent.assert_called_with('test')