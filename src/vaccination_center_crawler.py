import logging

import requests
from parsel import Selector


class VaccinationCenterCrawler:
    cantons = []

    def __init__(self, vaccination_center_url, entry_callback):
        self.vaccination_center_url = vaccination_center_url
        self.entry_callback = entry_callback
        self.cantons.clear()

    def crawl(self):
        response = requests.get(self.vaccination_center_url)
        selector = Selector(response.text)
        canton_entries = selector.css('article')
        for canton_entry in canton_entries:
            self.__process_canton_entry(canton_entry)

    def __process_canton_entry(self, canton_entry):
        canton = canton_entry.css('p strong').xpath('text()').get()
        url = canton_entry.css('p small a[href]').xpath('@href').get()
        phone = canton_entry.css('p small').xpath('text()').get()
        if phone:
            phone = phone.replace("\n", "")
        if canton not in self.cantons:
            self.entry_callback(canton, url, phone)
            self.cantons.append(canton)
        else:
            logging.warning(canton + " was already processed - not processing twice")
