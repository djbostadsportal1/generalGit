# -*- coding: utf-8 -*-
import scrapy
import re


class ImmonetSpider(scrapy.Spider):
    name = 'Immonet'
    allowed_domains = ['https://www.immonet.de']
    start_urls = ['https://www.immonet.de/berlin/wohnung-mieten.html?gclid=CjwKCAjwiPbWBRBtEiwAJakcpDW_07gC7QoRH1u4or7tkuqzYA4q9xaz7xMgYSDhzwP1UcVp24IlCxoCQuUQAvD_BwE']
    def parse(self, response):
        AdType = 'RENTAL'
        counter = 0

        # Wrapping all the content i want to scrape
        ads = response.xpath('//div[@id="result-list-stage"]/div')

        # Starts scraping and yielding to meta
        for ad in ads:
            response.meta['Title'] = ad.xpath('.//a[contains(@id,"lnkToDetails")]/@title').extract_first()
            ExternalReference = ad.xpath('.//a[contains(@id,"lnkToDetails")]/@href').extract_first()
            ExternalReference = response.urljoin(ExternalReference)
            response.meta['ExternalReference'] = ExternalReference
            response.meta['PropertyType'] = defPropertyType(noneToString(ad.xpath('.//p[@class="block text-gray-dark ellipsis"]/text()').extract_first()))
            response.meta['Rent'] = ad.xpath('.//div[contains(@id,"selPrice")]/span/text()').re_first('[\d,.]+')
            response.meta['LivingArea'] = ad.xpath('.//div[contains(@id,"selArea")]/p[2]/text()').re_first('\d+')
            response.meta['Municipality'] = findMunicipality(ad.xpath('.//p[@class="block text-gray-dark ellipsis"]/text()').re('[A-Z]+[a-z]+'))
            response.meta['AdType'] = AdType
            response.meta['counter'] = counter
            counter = counter + 1

            yield scrapy.Request(ExternalReference,
                                 callback=self.parse_details,
                                 meta=response.meta,
                                 dont_filter=True,
                                 )

        # next_page_url = response.xpath('//a[@class="col-sm-3 col-xs-1 pull-right text-right"]/@href').extract_first()
        # next_page_url = response.urljoin(next_page_url)
        # yield scrapy.Request(next_page_url, callback=self.parse, dont_filter=True)

    def parse_details(self, response):
        response.meta['Rooms'] = response.xpath('//span[@id="kfroomsValue"]/text()').re_first('\d+')
        response.meta['Placement'] = response.xpath('//p[@id="locationDescription"]/text()').extract_first()
        response.meta['AdditionalCost'] = response.xpath('//div[@id="priceid_20"]/text()').re_first('[\d,.]+')
        response.meta['HeatIncluded'] = trueStatement(noneToString(response.xpath('//div[@id="rentincludingheating"]/text()').extract_first()))
        response.meta['SecurityDeposit'] = response.xpath('//div[@id="priceid_19"]/text()').re_first('[\d,.]+')
        response.meta['BuildYear'] = response.xpath('//div[@id="yearbuild"]/text()').extract_first()
        response.meta['RentalPeriodFrom'] = response.xpath('//div[@id="deliveryValue"]/text()').extract_first()
        response.meta['EnergyClass'] = response.xpath('//div[@id="efficiencyValue"]/text()').extract_first()
        response.meta['Description'] = " ".join(response.xpath('//p[@id="otherDescription"]/text()').extract())



        yield response.meta

def noneToString(variable):
    # The backend can't handle option None.
    if variable == None:
        variable = ''
    else:
        variable = variable

    return variable

def defPropertyType(property):
    if 'apartment' in property.lower():
        PropertyType = 'APARTMENT'
    elif 'etagenwohnung' in property.lower():
        PropertyType = 'APARTMENT'
    elif 'zimmer' in property.lower():
        PropertyType = 'ROOM'
    elif 'room' in property.lower():
        PropertyType = 'ROOM'
    elif 'dachgeschosswohnung' in property.lower():
        PropertyType = 'PENTHOUSE'
    else:
        PropertyType = 'UNKNOWN'

    return PropertyType

def findMunicipality(vector):
    if len(vector) == 3:
        Municpality = vector[2]
    else:
        Municpality = 'UNKNOWN'

    return Municpality

def trueStatement(string):
    if 'ja' in string.lower():
        Statement = 'TRUE'
    elif 'nej' in string.lower():
        Statement = 'FALSE'
    else:
        Statement = 'UNKNOWN'
    return Statement
