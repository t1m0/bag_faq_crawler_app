import unittest
import unittest.mock
from src.bag_crawler import BagCrawler


class TestBagFaqCrawler(unittest.TestCase):
    find_more_link = '<br/>You can find more details <a target="_blank" href="http://localhost">here</a>.'

    text_not_cut = "Lorem ipsum dolor sit amet orci aliquam."
    text_not_cut_processed = "Lorem ipsum dolor sit amet orci aliquam. ..." + find_more_link

    text_cut_at_first_point = "Lorem ipsum dolor sit amet, consectetur adipiscing elit nama quis magna lectusda. Proin accumsan orci a imperdiet rutrum. Quisque pulvinar maximus semper. Phasellus cras amet."
    text_cut_at_first_point_cut = "Lorem ipsum dolor sit amet, consectetur adipiscing elit nama quis magna lectusda. ..." + find_more_link

    text_cut_at_max_length = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin accumsan orci a imperdiet rutrum. Quisque pulvinar maximus semper. Phasellus cras amet."
    text_cut_at_max_length_cut = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin accumsan orci a imperdiet rutrum. Quisque pulvinar maximus semper. Phasellus c ..." + find_more_link

    bag_faq_crawler = BagCrawler("", "", "", "", "")

    def setUp(self):
        self.watson_wrapper = unittest.mock.Mock()
        self.faq_crawler = unittest.mock.Mock()
        self.vaccination_center_crawler = unittest.mock.Mock()
        self.bag_faq_crawler.watson = self.watson_wrapper
        self.bag_faq_crawler.faq_crawler = self.faq_crawler
        self.bag_faq_crawler.vaccination_center_crawler = self.vaccination_center_crawler

    def test_faq_folder_creation(self):
        self.watson_wrapper.list_dialog_nodes_for_parent = unittest.mock.Mock(return_value={})
        self.watson_wrapper.get_dialog_node = unittest.mock.Mock(return_value=None)
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.create_dialog_folder.assert_called()
        self.watson_wrapper.get_dialog_node.assert_any_call('faq')

    def test_create_new_cut_at_point(self):
        self.watson_wrapper.list_dialog_nodes_for_parent = unittest.mock.Mock(return_value={'faq': {}})
        self.faq_crawler.crawl = lambda: self.bag_faq_crawler.faq_callback('test', 'http://localhost', 'question', self.text_cut_at_first_point)
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.createIntent.assert_called_with('test', 'question (BAG)')
        self.watson_wrapper.createDialogNode.assert_called_with('test', 'question (BAG)', self.text_cut_at_first_point_cut, 'faq', True)

    def test_create_new_cut_at_max_length(self):
        self.watson_wrapper.list_dialog_nodes_for_parent = unittest.mock.Mock(return_value={'faq': {}})
        self.faq_crawler.crawl = lambda: self.bag_faq_crawler.faq_callback('test', 'http://localhost', 'question', self.text_cut_at_max_length)
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.createIntent.assert_called_with('test', 'question (BAG)')
        self.watson_wrapper.createDialogNode.assert_called_with('test', 'question (BAG)', self.text_cut_at_max_length_cut, 'faq', True)

    def test_create_new_not_cut(self):
        self.watson_wrapper.list_dialog_nodes_for_parent = unittest.mock.Mock(return_value={'faq': {}})
        self.faq_crawler.crawl = lambda: self.bag_faq_crawler.faq_callback('test', 'http://localhost', 'question', self.text_not_cut)
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.createIntent.assert_called_with('test', 'question (BAG)')
        self.watson_wrapper.createDialogNode.assert_called_with('test', 'question (BAG)', self.text_not_cut_processed, 'faq',True)

    def test_no_change_since_node_already_exists(self):
        self.watson_wrapper.list_dialog_nodes_for_parent = unittest.mock.Mock(
            return_value={'faq': {}, 'test': {'uuid': 'test', 'question': 'question (BAG)', 'answer': self.text_not_cut_processed, 'jump_to_present': True}})
        self.faq_crawler.crawl = lambda: self.bag_faq_crawler.faq_callback('test', 'http://localhost', 'question', self.text_not_cut)
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.createIntent.assert_not_called()
        self.watson_wrapper.createDialogNode.assert_not_called()
        self.watson_wrapper.update_intent.assert_not_called()

    def test_jump_to_missing(self):
        self.watson_wrapper.list_dialog_nodes_for_parent = unittest.mock.Mock(
            return_value={'faq': {}, 'test': {'uuid': 'test', 'question': 'question (BAG)', 'answer': self.text_not_cut_processed, 'jump_to_present': False}})
        self.faq_crawler.crawl = lambda: self.bag_faq_crawler.faq_callback('test', 'http://localhost', 'question', self.text_not_cut)
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.createIntent.assert_not_called()
        self.watson_wrapper.createDialogNode.assert_not_called()
        self.watson_wrapper.update_intent.assert_not_called()
        self.watson_wrapper.update_dialog_node.assert_called_with('test', 'question (BAG)', self.text_not_cut_processed, 'faq', True)

    def test_answer_changed_of_existing_node(self):
        self.watson_wrapper.list_dialog_nodes_for_parent = unittest.mock.Mock(
            return_value={'faq': {}, 'test': {'uuid': 'test', 'question': 'question (BAG)', 'answer': self.text_not_cut_processed, 'jump_to_present': True}})
        self.watson_wrapper.get_intent = unittest.mock.Mock(
            return_value={'intent': 'test', 'examples': [{'text': 'question (BAG)'}, {'text': 'question (NOT_BAG)'}]})
        self.faq_crawler.crawl = lambda: self.bag_faq_crawler.faq_callback('test', 'http://localhost', 'question', self.text_cut_at_first_point)
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.update_intent.assert_called_with(
            {'intent': 'test', 'examples': [{'text': 'question (BAG)'}, {'text': 'question (NOT_BAG)'}], 'description': 'question (BAG)'})
        self.watson_wrapper.update_dialog_node.assert_called_with('test', 'question (BAG)', self.text_cut_at_first_point_cut, 'faq', True)

    def test_question_changed_of_existing_node(self):
        self.watson_wrapper.list_dialog_nodes_for_parent = unittest.mock.Mock(
            return_value={'faq': {}, 'test': {'uuid': 'test', 'question': 'question (BAG)', 'answer': self.text_not_cut_processed, 'jump_to_present': True}})
        self.watson_wrapper.get_intent = unittest.mock.Mock(
            return_value={'intent': 'test', 'examples': [{'text': 'question (BAG)'}, {'text': 'question (NOT_BAG)'}]})
        self.faq_crawler.crawl = lambda: self.bag_faq_crawler.faq_callback('test', 'http://localhost', 'question2', self.text_not_cut)
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.update_intent.assert_called_with(
            {'intent': 'test', 'examples': [{'text': 'question2 (BAG)'}, {'text': 'question (NOT_BAG)'}], 'description': 'question2 (BAG)'})
        self.watson_wrapper.update_dialog_node.assert_called_with('test', 'question2 (BAG)', self.text_not_cut_processed, 'faq', True)

    def test_delete_missing_faq_entry(self):
        self.watson_wrapper.list_dialog_nodes_for_parent = unittest.mock.Mock(
            return_value={'faq': {}, 'test': {'uuid': 'test', 'question': 'question (BAG)', 'answer': 'answer ...', 'jump_to_present': True}})
        self.bag_faq_crawler.crawl()
        self.watson_wrapper.delete_dialog_node.assert_called_with('test')
        self.watson_wrapper.delete_intent.assert_called_with('test')
