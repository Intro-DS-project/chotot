import scrapy
from scrapy.exceptions import CloseSpider
from datetime import datetime

from crawler_nhatot.items import RoomItem
from crawler_nhatot.gemini import extract_location


class NhatotSpider(scrapy.Spider):
    name = "nhatot"
    stop = False

    def start_requests(self):
        i = 0
        while i <= 0:
            yield scrapy.Request(url=f"https://phongtro.com/cho-thue-nha-tro-phong-tro-ha-noi-xc1-ci57.html?pi={i}", callback=self.parse)
            if self.stop:
                raise CloseSpider("Completed scraping the current day's item.")
            i += 1

    def parse(self, response):
        room_items = response.css("h3.re__card-title")
        for item in room_items:
            room_href = item.css("::attr(href)").get()
            yield response.follow(room_href, callback=self.parse_room_detail)

    def parse_room_detail(self, response):
        item = RoomItem()
        item["current_floor"] = 1
        # Thời gian: 06-04-2024
        post_date_str = response.css('.re__pr-short-info .title:contains("Ngày cập nhật") + .value::text').get()
        post_date_datetime = datetime.strptime(post_date_str, "%d-%m-%Y").date()
        item["post_date"] = post_date_str


        # Giá : 2,5 Triệu/tháng
        price_str = response.css('.re__pr-short-info .title:contains("Mức giá") + .value::text').get()
        try:
            item["price"] = float(price_str.split()[0].replace(',', '.'))
        except ValueError:  # Giá thỏa thuận
            item["price"] = 0

        # Diện tích : 20m
        area_str = response.css('.re__pr-short-info .title:contains("Diện tích") + .value::text').get()
        item["area"] = int(area_str.split()[0]) if area_str else 0

        # Phòng ngủ
        bedroom_str = response.css('.re__pr-short-info .title:contains("Phòng ngủ") + .value::text').get()
        item["num_bedroom"] = int(bedroom_str.split()[0]) if bedroom_str else 0

        # Phòng tắm
        bathroom_str = response.css('.re__pr-short-info .title:contains("Toilet") + .value::text').get()
        item["num_toilet"] = int(bathroom_str.split()[0]) if bathroom_str else 0

        # Lấy số tầng
        num_floor_str = response.css('.re__pr-specs-content-item-title:contains("Số tầng") + .re__pr-specs-content-item-value::text').get()
        item["num_floor"] = int(num_floor_str.split()[0]) if num_floor_str else 0
        
        # Lấy độ rộng đường
        street_width_str = response.css('.re__pr-specs-content-item-title:contains("Độ rộng đường") + .re__pr-specs-content-item-value::text').get()
        item["street_width"] = int(street_width_str.split()[0]) if street_width_str else 0
        
        # Lấy hướng nhà
        direction_str = response.css('.re__pr-specs-content-item-title:contains("Hướng nhà") + .re__pr-specs-content-item-value::text').get()
        item["direction"] = direction_str.strip() if direction_str else ""


        # # Địa chỉ
        address = response.css('.re__section-body.re__detail-content.js__section-body.js__pr-description.js__tracking').get()
        (item["street"], item["ward"], item["district"], *_) = extract_location(address).split(',')

        item["num_diningroom"] = 0
        item["num_kitchen"] = 0
        item["current_floor"] = 0

        yield item
