import logging
import unittest

from vaccination_center_crawler import VaccinationCenterCrawler


class VaccinationCenterTest(unittest.TestCase):
    cantons = []

    def test_crawler(self):
        logging.basicConfig(level=logging.INFO)
        crawler = VaccinationCenterCrawler('https://bag-coronavirus.ch/impfung/wann-kann-ich-impfen/#cantons', self.callback)
        crawler.crawl()
        self.assertEqual(26, len(self.cantons))

    def callback(self, canton, link, phone):
        self.assertIsNotNone(canton)
        self.assertIsNotNone(link)
        self.assertNotIn(canton, self.cantons)
        self.cantons.append(canton)
        logging.info(canton + ' - ' + link + ' - ' + str(phone))


if __name__ == '__main__':
    unittest.main()
