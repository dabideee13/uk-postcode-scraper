import scrapy


class UkPostcodeSpider(scrapy.Spider):
    name = "uk_postcode"
    start_urls = ["https://www.doogal.co.uk/AdministrativeAreas.php/"]
    home_url = "https://www.doogal.co.uk/"

    def parse(self, response):
        rows = response.xpath("//tr")

        for row in rows:
            data_url = row.xpath("./td/a/@href").extract()
            data_area = row.xpath("./td/a/text()").extract()

            try:
                admin_url, county_url = data_url
                admin_area, county_area = data_area

                admin_url = self.home_url + admin_url
                county_url = self.home_url + county_url

                urls = admin_url + county_url
                areas = admin_area + county_area

                for url, area in zip(urls, areas):
                    yield response.follow(
                        url,
                        callback=self.parse_area,
                        cb_kwargs={
                            "area": area
                        }
                    )

            except ValueError:
                try:
                    admin_url, admin_area = data_url[0], data_area[0]
                    county_url, county_area = "", ""

                    url = self.home_url + admin_url

                    yield response.follow(
                        url,
                        callback=self.parse_area,
                        cb_kwargs={
                            "area": admin_area
                        }
                    )

                except IndexError:
                    pass

    def parse_area(self, response, area):
        district_code = ""
        district_page_number = 2
        area_start_url = f"https://www.doogal.co.uk/AdministrativeAreas.php?district={district_page_number}&page=1"

        rows = response.xpath("//tr")

        for row in rows:
            postcode_url = row.xpath("./td/a/@href").get()
            postcode = row.xpath("./td/a/text()").get()

            try:
                url = self.home_url + postcode_url
                ward = row.xpath("./td/text()").extract()[0]

                yield response.follow(
                    url,
                    callback=self.parse_postcode,
                    cb_kwargs={
                        "area": area,
                        "postcode": postcode,
                        "ward": ward
                    }
                )

            except TypeError:
                continue

        next_page = f"https://www.doogal.co.uk/AdministrativeAreas.php?district={district_code}&page={district_page_number}"

    def parse_postcode(self, response, area, postcode, ward):
        try:
            table = response.xpath("//div[@class='col-md-6']")[3]
            headers = table.xpath(".//th/text()").extract()

            if "Date usage ended" not in headers:
                yield {
                    "area": area,
                    "postcode": postcode,
                    "ward": ward
                }

        except Exception:
            pass


# TODO: Add pagination in extracting postcodes
# TODO: Extract district number to enable pagination
