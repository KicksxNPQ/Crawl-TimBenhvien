import csv
import re
import os

import scrapy

START_PAGE = os.getenv("START_PAGE")
END_PAGE = os.getenv("END_PAGE")


class QuoteSpider(scrapy.Spider):
    name = "quote"
    custom_settings = {
        'CONCURRENT_REQUESTS': 1
    }

    def start_requests(self):
        url = "https://timbenhvien.vn/tim-kiem/trang"
        startPage = START_PAGE
        endPage = END_PAGE
        for i in range(startPage, endPage + 1):
            yield scrapy.Request(url=url + ":" + str(i), callback=self.parse, meta={'download_timeout': 10000})

    def parse(self, response):
        for item in response.css("div.result_item_box"):
            detail_url = item.css('.img_result .swiper-wrapper a::attr("href")').extract_first()
            if detail_url:
                yield scrapy.Request(
                    url=detail_url,
                    callback=self.parseDetail
                )

    def parseDetail(self, response):
        title_name = self.removeRedundant("".join(response.css(".title-name .hos_name_sp::text").extract())).strip()
        img = response.css('.pc-display img.img-responsive::attr("src")').extract_first()
        working_day = response.css(".working_day::text").extract_first()
        address = self.removeRedundant("".join(response.css(".adress *::text").extract())).strip()
        website = response.css(".col-location.col-location-globe a::text").extract_first()

        phone = ""
        lat = ""
        long = ""
        body = response.body.decode('utf-8')
        try:
            lats = re.findall('var cur_lat = "(.*)"', body)
            lat = lats[0]
        except AssertionError:
            print('Lat error')
        try:
            longs = re.findall('var cur_lon = "(.*)"', body)
            long = longs[0]
        except AssertionError:
            print('Long error')
        try:
            phones = re.findall('var cur_phone = \'(.*)\'', body)
            phone = phones[0]
        except AssertionError:
            print('Phone error')
        # print("PHONE", phone)
        # print("LAT", lat)
        # print("LONG", long)
        result = [title_name, address, phone, working_day, website, lat, long, img]
        result = [r or '' for r in result]
        with open("output/benhvien.csv", "a", newline='\n') as f:
            writer = csv.writer(f)
            writer.writerow(result)

    def removeRedundant(self, text):
        return re.sub("\s{2,}", " ", text)
