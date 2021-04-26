import logging
import unittest

from crawler import Crawler


class CrawlerTest(unittest.TestCase):
    uuids = []

    def test_crawler(self):
        logging.basicConfig(level=logging.INFO)
        crawler = Crawler('https://www.faq.bag.admin.ch/en/categories/vaccination', self.callback)
        crawler.crawl()

    def callback(self, uuid, link, question, answer):
        self.assertIsNotNone(uuid)
        self.assertIsNotNone(link)
        self.assertIsNotNone(question)
        self.assertIsNotNone(answer)
        self.assertEqual(uuid.count("/"), 0)
        self.assertNotIn(uuid, self.uuids)
        self.uuids.append(uuid)
        logging.info(uuid + ' - ' + link + ' - ' + question + ' - ' + answer)


if __name__ == '__main__':
    unittest.main()
