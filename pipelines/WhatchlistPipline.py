# pipelines/watchlist_pipeline.py

from datetime import datetime

from database.inserts import (
    insert_watchlist_file,
    insert_watchlist_raw_record,
    insert_watchlist_staging_record,
)


class WatchlistPipeline:

    def __init__(
        self,
        config,
        downloader,
        parser,
        pre_normalizer,
        mapper,
        post_normalizer,
    ):
        self.config = config
        self.source_name = config["source_name"]

        self.downloader = downloader
        self.parser = parser

        self.pre_normalizer = pre_normalizer
        self.mapper = mapper
        self.post_normalizer = post_normalizer

    def run(self):

        print(f"Starting watchlist pipeline: {self.source_name}")

        downloaded_file_path = self.downloader.download(
            url=self.config["url"],
            source_name=self.source_name
        )

        file_id = insert_watchlist_file(
            source_name=self.source_name,
            url=self.config.get("url"),
            file_path=downloaded_file_path,
            file_type=self.config.get("file_type"),
            downloaded_at=datetime.now(),
            schedule=self.config.get("schedule"),
        )

        raw_records = self.parser.parse(
            file_path=downloaded_file_path,
            config=self.config
        )

        raw_count = 0
        staging_count = 0

        for raw_record in raw_records:

            raw_count += 1

            raw_record_id = insert_watchlist_raw_record(
                file_id=file_id,
                source_name=self.source_name,
                raw_json=raw_record,
                created_at=datetime.now(),
            )

            current_record = raw_record

            current_record = self.pre_normalizer.pre_normalize_record(
                source=self.source_name,
                raw_json=current_record
            )

            current_record = self.mapper.map_record(
                current_record
            )

            current_record = self.post_normalizer.post_normalize_record(
                current_record
            )

            insert_watchlist_staging_record(
                file_id=file_id,
                raw_record_id=raw_record_id,
                source_name=self.source_name,
                final_json=current_record,
                created_at=datetime.now(),
            )

            staging_count += 1

        print(f"Completed watchlist pipeline: {self.source_name}")
        print(f"Raw records inserted: {raw_count}")
        print(f"Staging records inserted: {staging_count}")
