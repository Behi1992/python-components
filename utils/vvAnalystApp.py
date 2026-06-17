import streamlit as st
import json
import tempfile
import os
from pathlib import Path
import sys



ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from valueExplorer import extract_values
from parsing.xmlParser import XmlParser
from parsing.tabularParser import TabularParser
from schemaExtractor import extract_schema, schema_to_rows

st.set_page_config(
    page_title="VPAT",
    layout="wide"
)

st.title("VV Production Analyst Tools - VPAT")
st.caption("Production helper tools for analysts")


tool = st.sidebar.selectbox(
    "Select Tool",
    [
        "Source File Parser",
        "Schema Explorer",
        "Value Explorer"
    ]
)


# =========================================================
# Tool 1: Source File Parser
# =========================================================
if tool == "Source File Parser":
    st.header("Source File Parser")
    st.caption("Convert source files such as XML, Excel or CSV into raw JSONL records")

    uploaded_file = st.file_uploader(
        "Upload source file",
        type=["xml", "xlsx", "xls", "csv"]
    )

    if uploaded_file:
        suffix = os.path.splitext(uploaded_file.name)[1].lower()

        st.info(f"Selected file: {uploaded_file.name}")

        file_type = st.selectbox(
            "Source file type",
            ["Auto Detect", "XML", "Excel / CSV"]
        )

        config = {}

        if file_type == "XML" or suffix == ".xml":
            root_tag = st.text_input(
                "Root Tag",
                value="Designation",
                help="Example: Designation, sanctionEntity"
            )

            config["root_tag"] = root_tag

        if file_type == "Excel / CSV" or suffix in [".xlsx", ".xls", ".csv"]:
            sheet_name = st.text_input(
                "Sheet Name / Index",
                value="0",
                help="For Excel use 0 for first sheet, or write sheet name"
            )

            try:
                config["sheet_name"] = int(sheet_name)
            except ValueError:
                config["sheet_name"] = sheet_name

        if st.button("Parse File"):

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                input_path = tmp.name

            try:
                records = []

                if file_type == "Auto Detect":

                    if suffix == ".xml":
                        parser = XmlParser()
                        records = list(
                            parser.parse(
                                input_path,
                                config
                            )
                        )

                    elif suffix in [".xlsx", ".xls", ".csv"]:
                        parser = TabularParser(output_dir="output")
                        records = list(
                            parser.parse(
                                input_path,
                                config
                            )
                        )

                    else:
                        st.error(f"Unsupported file type: {suffix}")

                elif file_type == "XML":

                    parser = XmlParser()
                    records = list(
                        parser.parse(
                            input_path,
                            config
                        )
                    )

                elif file_type == "Excel / CSV":

                    parser = TabularParser(output_dir="output")
                    records = list(
                        parser.parse(
                            input_path,
                            config
                        )
                    )

                if records:
                    st.success(f"Parsed {len(records)} records successfully.")

                    st.subheader("Preview")
                    st.dataframe(
                        records[:50],
                        use_container_width=True
                    )

                    jsonl_output = "\n".join(
                        json.dumps(record, ensure_ascii=False)
                        for record in records
                    )

                    output_file_name = f"{Path(uploaded_file.name).stem}_raw.jsonl"

                    st.download_button(
                        label="Download JSONL",
                        data=jsonl_output,
                        file_name=output_file_name,
                        mime="application/jsonl"
                    )

                else:
                    st.warning("No records found. Check parser type or root tag.")

            except Exception as e:
                st.error(f"Error while parsing file: {e}")

# =========================================================
# Tool 2: Schema Explorer
# =========================================================
elif tool == "Schema Explorer":
    st.header("Schema Explorer")
    st.caption("Extract schema fields from a JSONL file")

    uploaded_file = st.file_uploader(
        "Upload JSONL file",
        type=["jsonl"]
    )

    if uploaded_file:

        if st.button("Extract Schema"):

            suffix = ".jsonl"

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                input_path = tmp.name

            try:
                final_schema, total_records, errors = extract_schema(input_path)

                schema_rows = schema_to_rows(final_schema)

                st.success(
                    f"Schema extracted successfully. Records: {total_records}, Fields: {len(schema_rows)}"
                )

                st.subheader("Schema Fields")

                st.dataframe(
                    schema_rows,
                    use_container_width=True
                )

                schema_json = json.dumps(
                    final_schema,
                    ensure_ascii=False,
                    indent=4
                )

                st.download_button(
                    label="Download Schema JSON",
                    data=schema_json,
                    file_name=f"{Path(uploaded_file.name).stem}_schema.json",
                    mime="application/json"
                )

                if errors:
                    with st.expander("Errors"):
                        st.write(errors)

            except Exception as e:
                st.error(f"Error while extracting schema: {e}")
# =========================================================
# Tool 3: Value Explorer
# =========================================================
elif tool == "Value Explorer":
    st.header("Value Explorer")
    st.caption("Extract unique values from a JSONL file by JSON path")

    uploaded_file = st.file_uploader(
        "Upload JSONL file",
        type=["jsonl"]
    )

    json_path = st.text_input(
        "JSON Path",
        placeholder="Example: names.name"
    )

    if uploaded_file and json_path:
        path_parts = json_path.split(".")
        unique_values = set()
        errors = []

        for i, line in enumerate(uploaded_file):
            try:
                data = json.loads(line.decode("utf-8"))
                values = extract_values(data, path_parts)

                for value in values:
                    if value is None:
                        continue

                    if isinstance(value, (dict, list)):
                        continue

                    clean_value = str(value).strip()

                    if clean_value:
                        unique_values.add(clean_value)

            except Exception as e:
                errors.append(f"Line {i + 1}: {e}")

        sorted_values = sorted(unique_values)

        st.success(f"Found {len(sorted_values)} unique values.")

        st.subheader("Unique Values")
        st.dataframe(
            [{"value": value} for value in sorted_values],
            use_container_width=True
        )

        output_text = "\n".join(sorted_values)

        st.download_button(
            label="Download TXT",
            data=output_text,
            file_name="unique_values.txt",
            mime="text/plain"
        )

        if errors:
            with st.expander("Errors"):
                st.write(errors)