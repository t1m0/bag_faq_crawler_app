import requests
from parsel import Selector
import re
import logging

class FaqCrawler:
    html_tag_regex = re.compile('<.*?>')

    uuid_regex = re.compile(r"[^/]*$", re.IGNORECASE)
    uuids = []

    def __init__(self, base_faq_url, entry_callback):
        self.base_faq_url = base_faq_url
        self.entry_callback = entry_callback

    def crawl(self):
        response = requests.get(self.base_faq_url)
        selector = Selector(response.text)
        faq_category_page_selectors = selector.css('span.field-content a[href]')
        for category_page in faq_category_page_selectors:
            logging.info("Crawling category +"+category_page.xpath('text()').get())
            url = category_page.xpath('@href').get()
            if "categories" in url:
                self.__process_category_page(self.__compile_full_url(url))

    def __process_category_page(self, page_link):
        response = requests.get(page_link)
        selector = Selector(response.text)
        self.__extract_entries(selector)
        faq_page_selectors = selector.css('a[title][href]')
        for page in faq_page_selectors:
            url = page.xpath('@href').get()
            if "page" in url:
                response = requests.get(self.__compile_full_url(url))
                selector = Selector(response.text)
                self.__extract_entries(selector)

    def __extract_entries(self, current_page):
        current_entries = current_page.css('span a[href]')
        for e in current_entries:
            relative_link = e.xpath('@href').get()
            question = e.xpath('text()').get()
            link = self.__compile_full_url(relative_link)
            answer = self.__extract_answer(link)
            uuid = self.__extract_uuid(relative_link)
            if answer and uuid not in self.uuids:
                self.entry_callback(uuid, link, question, self.__replace_html_tags(answer))
                self.uuids.append(uuid)
            elif answer:
                logging.info("Ignoring "+uuid+", since it was already processed!")

    def __compile_full_url(self, relative_url):
        relative_url_without_language = relative_url[3:len(relative_url)]
        return self.base_faq_url + relative_url_without_language

    def __extract_answer(self, link):
        response = requests.get(link)
        selector = Selector(response.text)
        return selector.css('.field-item.even *').xpath('text()').get()

    def __replace_html_tags(self, answer):
        return re.sub(self.html_tag_regex, '', answer)

    def __extract_uuid(self, link):
        last_index = link.rindex('/')
        uuid = link[last_index + 1:len(link)]
        uuid = uuid.replace("%E2%80%99", "").replace("%E2%80%93","").replace("%E2%80%98","").replace("%E2%80%9C","").replace("%E2%80%9D","").replace("%","")
        if len(uuid) > 128:
            uuid = uuid[0:128]
        return uuid
