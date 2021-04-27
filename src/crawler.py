import requests
from parsel import Selector
from html.parser import HTMLParser
import re


class Crawler:
    html_tag_regex = re.compile('<.*?>')

    uuid_regex = re.compile(r"[^/]*$", re.IGNORECASE)

    def __init__(self, base_faq_url, entry_callback):
        self.base_faq_url = base_faq_url
        self.entry_callback = entry_callback

    def crawl(self):
        response = requests.get(self.base_faq_url)
        selector = Selector(response.text)
        self.__extract_entries(selector)
        faq_page_selectors = selector.css('a[title][href]')
        for page in faq_page_selectors:
            url = page.xpath('@href').get()
            if "page" in url:
                response = requests.get('https://www.faq.bag.admin.ch' + url)
                selector = Selector(response.text)
                self.__extract_entries(selector)

    def __extract_entries(self, current_page):
        current_entries = current_page.css('span a[href]')
        for e in current_entries:
            relative_link = e.xpath('@href').get()
            question = e.xpath('text()').get()
            link = 'https://www.faq.bag.admin.ch' + relative_link
            answer = self.__extract_answer(link)
            uuid = self.__extract_uuid(relative_link)
            if answer:
                self.entry_callback(uuid, link, question, self.__replace_html_tags(answer))

    def __extract_answer(self, link):
        response = requests.get(link)
        selector = Selector(response.text)
        return selector.css('.field-item.even *').xpath('text()').get()

    def __replace_html_tags(self, answer):
        return re.sub(self.html_tag_regex, '', answer)

    def __extract_uuid(self, link):
        last_index = link.rindex('/')
        uuid = link[last_index + 1:len(link)]
        return uuid.replace("%E2%80%99", "")
