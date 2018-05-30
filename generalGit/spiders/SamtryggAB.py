# -*- coding: utf-8 -*-
"""
Created 17-01-2018
Last-edit: 26-03-2018
@author: Dennis
"""

import scrapy
import scrapy_splash
import sys
import time
import re

counter = 0

debug = False

if debug:
    reload(sys)
    sys.setdefaultencoding('utf-8')


class SamtryggAB(scrapy.Spider):

    # Name of scraper
    name = 'SamtryggAB'


    # Start page you start scraping from, den her hjemmeside er speciel og det kan godt ske hvis man kun har en start
    # url, at den så ikke fanger noget. Så nu giver den 4 forsøg og kan derfor også skrabe 4 gange det den skal
    # men fanger i sidste ende så altid noget.
    start_urls = ['https://www.samtrygg.se/RentalObject/NewSearch']

    # The domain you are allowed to scrape on
    allowed_domains = ['www.samtrygg.se']

    # writes string to log file located at ./log/scrapyLog.txt if no log file exists, one is created
    def writeToLogFile(self, logMessage):
        logFile = open("log/infoLog.txt", "a+")
        logFile.write(
            "Message logged at: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " " + logMessage + "\n")
        logFile.close()

    # Scraping the first page
    def parse(self, response):
        global counter

        # Wrapping all the content we want to extract
        ads = response.xpath('//div[@class="large-12 columns objects"]/div')

        # Starts scraping and yielding data
        for ad in ads:
            response.meta['StreetName'] = NoneToString(ad.xpath('.//div[@class="data"]//div[@class="objrow1"]/div[1]/text()').re_first('\D+'))
            response.meta['StreetNumber'] = NoneToString(ad.xpath('.//div[@class="data"]//div[@class="objrow1"]/div[1]/text()').re_first('\d+\s?\D?'))
            response.meta['City'] = NoneToString(ad.xpath('.//div[@class="objrow2"]/div[1]/text()').re_first('[A-Z]+[a-z]+'))
            response.meta['ZipCode'] = NoneToString(ad.xpath('//div[@class="objrow2"]/div[1]/text()').re_first('[\d\s]+'))
            response.meta['Rent'] = NoneToString(ad.xpath('.//span[@class="price"]/text()').re_first('[\d\s]+'))
            response.meta['LivingSpace'] = NoneToString(ad.xpath('.//div[@class="area"]/text()').re_first('\d+'))
            response.meta['Rooms'] = NoneToString(ad.xpath('.//div[@class="rooms"]/text()').re_first('\d+'))
            response.meta['AdType'] = 'RENTAL'
            response.meta['RegistrationRequired'] = 'TRUE'
            response.meta['Name'] = 'Samtrygg AB'



            relative_url = ad.xpath('.//a[@class="image-link"]/@href').extract_first()
            absolute_url = response.urljoin(relative_url)
            counter = counter + 1

            response.meta['ExternalReference'] = NoneToString(absolute_url)
            response.meta['Counter'] = counter

            yield scrapy.Request(absolute_url, callback=self.parse_details, meta=response.meta, dont_filter=True)

    def parse_details(self, response):
        response.meta['Description'] = NoneToString(response.xpath('//p[@itemprop="description"]/text()').extract_first())
        response.meta['Images'] = "|".join(response.xpath('//div[@id="p-gallery"]/a/@href').extract())

        RentalPeriodFrom = response.xpath('//div[@class="boendet row"]/div[2]//ul/li[1]/text()').extract_first()
        RentalPeriodTo = response.xpath('//div[@class="boendet row"]/div[2]//ul/li[2]/text()').extract_first()
        RentalPeriod = ''

        if 'tillsvidare' in RentalPeriodTo.lower():
            RentalPeriod = 'UNLIMITED'
            RentalPeriodTo = ''

        itemprops = " ".join(response.xpath('//li[@itemprop="amenityFeature"]/text()').re('\w+'))

        Balcony = 'FALSE'
        Bathtub = 'FALSE'
        HeatIncluded = 'FALSE'
        ChildFriendly = 'FALSE'
        Parking = ''
        DisabledAccess = 'FALSE'
        Elevator = 'FALSE'


        if 'balkong' in itemprops.lower():
            Balcony = 'TRUE'
        if 'badkar' in itemprops.lower():
            Bathtub = 'TRUE'
        if 'värme' in itemprops.lower():
            HeatIncluded = 'TRUE'
        if 'barnvänligt' in itemprops.lower():
            ChildFriendly = 'TRUE'
        if 'parkeringsplats' in itemprops.lower():
            Parking = 'INCLUDED'
        if 'handikappsvänligt' in itemprops.lower():
            DisabledAccess = 'TRUE'
        if 'hiss' in itemprops.lower():
            Elevator = 'TRUE'




        response.meta['Balcony'] = Balcony
        response.meta['Bathtud'] = Bathtub
        response.meta['HeatIncluded'] = HeatIncluded
        response.meta['ChildFriendly'] = ChildFriendly
        response.meta['Parking'] = Parking
        response.meta['DisabledAccess'] = DisabledAccess
        response.meta['Elevator'] = Elevator
        response.meta['RentalPeriod'] = NoneToString(RentalPeriod)
        response.meta['RentalPeriodFrom'] = NoneToString(RentalPeriodFrom)
        response.meta['RentalPeriodTo'] = NoneToString(RentalPeriodTo)

        yield response.meta


def NoneToString(variable):
    # The backend can't handle option None.
    if variable == None:
        variable = ''
    else:
        variable = variable

    return variable

