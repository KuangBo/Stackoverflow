import scrapy


class QuotesSpider(scrapy.Spider):
    name = 'quotes_2_3'
    start_urls = [
        'http://quotes.toscrape.com',
    ]
    allowed_domains = [
        'toscrape.com',
    ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'quote': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }
            author_page = response.css('small.author+a::attr(href)').extract_first()
            authro_full_url = response.urljoin(author_page)
            yield scrapy.Request(authro_full_url, callback=self.parse_author)

        next_page = response.css('li.next a::attr("href")').extract_first()
        if next_page is not None:
            next_full_url = response.urljoin(next_page)
            yield scrapy.Request(next_full_url, callback=self.parse)

    def parse_author(self, response):
        yield {
            'author': response.css('.author-title::text').extract_first(),
            'author_born_date': response.css('.author-born-date::text').extract_first(),
            'author_born_location': response.css('.author-born-location::text').extract_first(),
            'authro_description': response.css('.author-born-location::text').extract_first(),
        }
