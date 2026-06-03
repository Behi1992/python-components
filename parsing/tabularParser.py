import pandas as pd
import json
from pathlib import Path
from datetime import datetime


class TabularIngestor:

    def __init__(self, output_dir="output"):

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def dataframe_to_records(self, df):

        return (
            df.fillna("")
            .astype(str)
            .to_dict(orient="records")
        )

    def write_jsonl(
        self,
        records,
        output_file
    ):

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            for record in records:

                f.write(
                    json.dumps(
                        record,
                        ensure_ascii=False
                    )
                    + "\n"
                )

    def parse_csv(
        self,
        csv_file
    ):

        df = pd.read_csv(
            csv_file,
            dtype=str
        )

        records = self.dataframe_to_records(df)

        output_file = (
            self.output_dir
            / f"{Path(csv_file).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        )

        self.write_jsonl(
            records,
            output_file
        )

        print(
            f"CSV converted successfully:\n{output_file}"
        )

        return str(output_file)

    def parse_excel(
        self,
        excel_file,
        sheet_name=0
    ):

        df = pd.read_excel(
            excel_file,
            sheet_name=sheet_name,
            dtype=str
        )

        records = self.dataframe_to_records(df)

        output_file = (
            self.output_dir
            / f"{Path(excel_file).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        )

        self.write_jsonl(
            records,
            output_file
        )

        print(
            f"Excel converted successfully:\n{output_file}"
        )

        return str(output_file)


# =========================================================
# PUBLIC API
# =========================================================

def run_tabular_ingestion(
    input_file,
    output_dir="output",
    sheet_name=0
):

    ingestor = TabularIngestor(
        output_dir=output_dir
    )

    suffix = Path(input_file).suffix.lower()

    if suffix == ".csv":

        return ingestor.parse_csv(
            input_file
        )

    elif suffix in [".xlsx", ".xls"]:

        return ingestor.parse_excel(
            input_file,
            sheet_name=sheet_name
        )

    raise ValueError(
        f"Unsupported file type: {suffix}"
    )


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    output_path = run_tabular_ingestion(
        input_file="/Users/mac/Desktop/VV_Python_Project/Australian_Sanctions_Consolidated_List.xlsx"
    )

    print(
        f"Output file: {output_path}"
    )
