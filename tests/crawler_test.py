import logging
import unittest

from crawler import Crawler


class CrawlerTest(unittest.TestCase):
    faqs = {}

    def test_crawler(self):
        crawler = Crawler('https://www.faq.bag.admin.ch/en/categories/vaccination', self.callback)
        crawler.crawl()

    def callback(self, uuid, link, question, answer):
        self.assertIsNotNone(uuid)
        self.assertIsNotNone(link)
        self.assertIsNotNone(question)
        self.assertIsNotNone(answer)
        self.assertEqual(uuid.count("/"), 0)
        self.assertNotIn(uuid, self.faqs.keys())
        self.faqs['uuid'] = {'question': question, 'answer': answer}
        logging.info(uuid + ' - ' + link + ' - ' + question + ' - ' + answer)


if __name__ == '__main__':
    unittest.main()
