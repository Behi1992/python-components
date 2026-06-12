import os
from scrapy import Selector


class EnrichmentEngine:

    def enrich_record(self, record, rules):

        if not rules:
            return record

        for rule in rules:
            handler_name = rule["handler"]
            config = rule.get("config", {})

            handler = getattr(self, handler_name, None)

            if handler is None:
                raise ValueError(
                    f"No enrichment handler found: {handler_name}"
                )

            record = handler(record, config)

        return record

    def enrich_atc_profile_data(self, record, config):

        profile_dir = config.get(
            "profile_dir",
            "downloads/profiles"
        )

        images_dir = config.get(
            "images_dir",
            "downloads/images"
        )

        detail_url = str(record.get("detail_url", "")).strip()

        # If there is no detail_url, this record probably has no profile page.
        if not detail_url:
            return record

        slug = detail_url.rstrip("/").split("/")[-1]

        file_base_name = slug.replace("-", " ").upper()

        profile_file_name = (
            f"{file_base_name} _ Anti-Terrorism Council.html"
        )

        profile_file = os.path.join(
            profile_dir,
            profile_file_name
        )

        # Profile is optional.
        if not os.path.exists(profile_file):
            return record

        with open(profile_file, "r", encoding="utf-8") as f:
            html = f.read()

        selector = Selector(text=html)

        profile_fields = {}

        rows = selector.xpath("//article//table//tr")

        for row in rows:
            key = row.xpath("./td[1]//text()").getall()
            value = row.xpath("./td[2]//text()").getall()

            key = " ".join(key).strip()
            value = " ".join(value).strip()

            if not key:
                continue

            profile_fields[key] = value

        image_urls = selector.xpath(
            "//article//img/@src"
        ).getall()

        local_images = []

        if os.path.exists(images_dir):
            for file_name in os.listdir(images_dir):
                if file_base_name in file_name.upper():
                    local_images.append(
                        os.path.join(images_dir, file_name)
                    )

        record["profile_data"] = {
            "profile_file": profile_file,
            "profile_slug": slug,
            "profile_fields": profile_fields,
            "image_urls": image_urls,
            "local_images": local_images
        }

        return record
    