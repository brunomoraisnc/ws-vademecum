# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import time

import scrapy
from scrapy.linkextractors import LinkExtractor

from bs4 import BeautifulSoup


class WsvademecumItem(scrapy.Item):
    # Set item fields
    url= scrapy.Field()
    content = scrapy.Field()


class WsvademecumSpider(scrapy.Spider):
    name = 'wsvademecum'
    allowed_domains = ['vade-mecum.vercel.app']
    start_urls =[
        'https://vade-mecum.vercel.app/',
    ]
    base_url = "https://vade-mecum.vercel.app/"


    def parse(self, response):
        """Method to parse the HTML table and extract the link to each item info"""
        links = LinkExtractor(allow_domains=self.allowed_domains).extract_links(response)
        for link in links:
            request = response.follow(link, callback=self.parse_links)
            yield request


    def remove_all_html_elements(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        return text


    def remove_html_tag_value(self, html_content, tag_name=None, tag_attrs=None):
        """Function to remove html tags and their content using BeautifulSoup"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all <tag_name> tags and remove them
        if tag_attrs is None:
            for script in soup.find_all(tag_name):
                script.extract()
        else:
            for script in soup.find_all(tag_name, attrs=tag_attrs):
                script.extract()
        return str(soup)
    

    def parse_links(self, response):
        """Method to request a new HTML link to the server, extracted with the parse method"""
        content = response.xpath('body').getall()
        content = ' '.join(content)

        html_tags_to_remove = [
            "noscript",
            "link",
            "script",
            "style",
            "footer"
        ]

        tag_attrs = [
            {"id": "footer"},
        ]

        for html_tag in html_tags_to_remove:
            content = self.remove_html_tag_value(content, html_tag)
        for tag_attr in tag_attrs:
            content = self.remove_html_tag_value(content, tag_attrs=tag_attr)
        
        # content = self.html_to_markdown(content)
        content = self.remove_all_html_elements(content)

        time.sleep(0.3)

        yield WsvademecumItem(url= response.url, content= content)


    def remove_img_tags(self, response):
        # Use XPath to select and remove all <img> tags
        response.selector.remove("//img")
        return response
