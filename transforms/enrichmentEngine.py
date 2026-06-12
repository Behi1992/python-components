import os
from scrapy import Selector


class EnrichmentEngine:

    def enrich_dataset(self, records, rules):

        if not rules:
            return records

        for rule in rules:

            if rule.get("level", "record") != "dataset":
                continue

            handler_name = rule["handler"]
            config = rule.get("config", {})

            handler = getattr(self, handler_name, None)

            if handler is None:
                raise ValueError(
                    f"No enrichment handler found: {handler_name}"
                )

            records = handler(records, config)

        return records


    def enrich_record(self, record, rules):

        if not rules:
            return record

        for rule in rules:

            if rule.get("level", "record") != "record":
                continue

            handler_name = rule["handler"]
            config = rule.get("config", {})

            handler = getattr(self, handler_name, None)

            if handler is None:
                raise ValueError(
                    f"No enrichment handler found: {handler_name}"
                )

            record = handler(record, config)

        return record


    def fix_eu_vessel_multiline_rows(self, records, config):
        
        records = list(records)

        fixed_records = []

        for record in records:

            vessel_name = str(
                record.get("Vessel name at designation time", "")
            ).strip()

            imo_number = str(
                record.get("IMO number", "")
            ).strip()

            date_value = str(
                record.get("Date of application", "")
            ).strip()

            link_value = str(
                record.get("Link to relevant EU Official Journal ", "")
            ).strip()

            if not vessel_name or not imo_number:
                continue

            if date_value == "#REF!":
                date_value = ""

            if link_value == "#REF!":
                link_value = ""

            record["Vessel name at designation time"] = vessel_name
            record["IMO number"] = imo_number
            record["Date of application"] = date_value
            record["Link to relevant EU Official Journal "] = link_value

            fixed_records.append(record)

        print(
            f"EU vessel enrichment: {len(records)} rows -> {len(fixed_records)} vessels"
        )

        return fixed_records

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
                        os.path.join(
                            images_dir,
                            file_name
                        )
                    )


        record["profile_data"] = {
            "profile_file": profile_file,
            "profile_slug": slug,
            "profile_fields": profile_fields,
            "image_urls": image_urls,
            "local_images": local_images,
        }

        return record