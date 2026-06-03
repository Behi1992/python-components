import json
from pathlib import Path

import pdfplumber


class PdfParser:

    def parse(self, pdf_path):

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        result = {
            "metadata": {},
            "tables": []
        }

        with pdfplumber.open(pdf_path) as pdf:

            total_pages = len(pdf.pages)

            result["metadata"] = {
                "file_name": pdf_path.name,
                "page_count": total_pages
            }

            print(f"PDF opened: {pdf_path.name}")
            print(f"Total pages: {total_pages}")

            for page_number, page in enumerate(pdf.pages, start=1):

                print(f"Processing page {page_number}/{total_pages} ...")

                tables = page.extract_tables()

                if not tables:
                    print(f"  No table found on page {page_number}")
                    continue

                print(f"  Found {len(tables)} table(s) on page {page_number}")

                for table_index, table in enumerate(tables, start=1):

                    if not table:
                        print(f"  Table {table_index} is empty")
                        continue

                    print(
                        f"  Table {table_index}: "
                        f"{len(table)} row(s)"
                    )

                    result["tables"].append({
                        "page_number": page_number,
                        "table_index": table_index,
                        "rows": table
                    })

        print(f"Parsing finished. Total tables: {len(result['tables'])}")

        return result

    def _export_json(self, result, output_file):

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                result,
                f,
                ensure_ascii=False,
                indent=2
            )

        print(f"JSON saved: {output_file}")

    def _clean_header(self, header):

        if header is None:
            return None

        header = str(header).strip()

        if not header:
            return None

        return (
            header
            .replace("\n", " ")
            .replace(".", "")
            .strip()
        )

    def _is_same_header(self, row, headers):

        if not row or not headers:
            return False

        cleaned_row = [
            self._clean_header(cell)
            for cell in row
        ]

        cleaned_row = [
            cell for cell in cleaned_row
            if cell
        ]

        cleaned_headers = [
            self._clean_header(header)
            for header in headers
        ]

        cleaned_headers = [
            header for header in cleaned_headers
            if header
        ]

        if not cleaned_row or not cleaned_headers:
            return False

        matched = 0

        for cell in cleaned_row:
            if cell in cleaned_headers:
                matched += 1

        return matched >= 2

    def _export_jsonl(self, result, output_file):

        global_headers = None
        written_count = 0

        with open(output_file, "w", encoding="utf-8") as f:

            for table in result["tables"]:

                rows = table["rows"]

                if not rows:
                    continue

                page_number = table["page_number"]
                table_index = table["table_index"]

                print(
                    f"Exporting page {page_number}, "
                    f"table {table_index}"
                )

                start_row_index = 0

                if global_headers is None:
                    global_headers = rows[0]
                    start_row_index = 1

                    print("  Header detected from first table:")
                    print(f"  {global_headers}")

                else:
                    if self._is_same_header(rows[0], global_headers):
                        start_row_index = 1
                        print("  Repeated header skipped")
                    else:
                        start_row_index = 0

                for row in rows[start_row_index:]:

                    if not row:
                        continue

                    record = {
                        "source_page": page_number,
                        "source_table": table_index
                    }

                    has_value = False

                    for idx, header in enumerate(global_headers):

                        clean_header = self._clean_header(header)

                        if not clean_header:
                            continue

                        value = row[idx] if idx < len(row) else None

                        if isinstance(value, str):
                            value = value.strip()

                        record[clean_header] = value

                        if value not in [None, ""]:
                            has_value = True

                    if has_value:
                        f.write(
                            json.dumps(
                                record,
                                ensure_ascii=False
                            )
                            + "\n"
                        )
                        written_count += 1

        print(f"JSONL saved: {output_file}")
        print(f"Total records written: {written_count}")

    def convert(
        self,
        input_file,
        output_file,
        output_type="jsonl"
    ):

        result = self.parse(input_file)

        output_type = output_type.lower()

        if output_type == "json":
            self._export_json(
                result,
                output_file
            )

        elif output_type == "jsonl":
            self._export_jsonl(
                result,
                output_file
            )

        else:
            raise ValueError(
                f"Unsupported output type: {output_type}"
            )

        return output_file