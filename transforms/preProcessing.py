import re
import hashlib
from urllib.parse import urlparse, unquote

from nameparser import HumanName


EMPTY_VALUES = {"", "N/A", "NA", "NONE", "NULL", "UNKNOWN", "-"}


def get_nested_value(record, field_path, default=""):
    value = record

    for part in field_path.split("."):
        if not isinstance(value, dict):
            return default
        value = value.get(part, default)

    return value


def is_empty_value(value):
    return str(value).strip().upper() in EMPTY_VALUES


def detect_entity_type(record, config):
    input_field = config["input_field"]
    output_field = config.get("output_field", "detected_entity_type")

    name = str(record.get(input_field, "")).strip()
    name_upper = name.upper()

    org_keywords = [
        "INC", "CORP", "COMPANY", "CO.", "LLC", "LTD", "OPC",
        "SERVICES", "FIRM", "OFFICE", "ASSOCIATES", "PARTNERS",
        "CPA", "CPAS", "ACCOUNTING", "BOOKKEEPING", "AUDITING",
        "CONSULTANCY", "BUSINESS", "GROUP", "TRADING", "STORE",
        "SHOP", "REALTY", "BROKERAGE"
    ]

    if any(keyword in name_upper for keyword in org_keywords):
        record[output_field] = "Organization"
        return record

    parsed_name = HumanName(name)

    if parsed_name.first and parsed_name.last:
        record[output_field] = "Individual"
    else:
        record[output_field] = "Organization"

    return record


def generate_atc_unique_id(record, config):
    name_field = config.get("name_field", "name")
    resolution_field = config.get("resolution_field", "atc_resolution_no")
    output_field = config.get("output_field", "unique_id")
    prefix = config.get("prefix", "ATC")

    name = str(record.get(name_field, "")).strip()
    resolution_text = str(record.get(resolution_field, "")).strip()

    match = re.search(
        r"Resolution\s+No\.?\s*([0-9]+)",
        resolution_text,
        re.IGNORECASE
    )

    resolution_no = match.group(1) if match else "UNKNOWN"

    name_hash = hashlib.md5(
        name.lower().encode("utf-8")
    ).hexdigest()[:10]

    record[output_field] = f"{prefix}-{resolution_no}-{name_hash}"

    return record


def extract_name_from_url(record, config):
    input_field = config.get("input_field", "detail_url")
    output_field = config.get("output_field", "extracted_name_from_url")

    detail_url = str(record.get(input_field, "")).strip()

    if not detail_url:
        record[output_field] = ""
        return record

    path = urlparse(detail_url).path.strip("/")
    slug = path.split("/")[-1]

    record[output_field] = unquote(slug).strip()

    return record


def split_atc_date_and_place_of_birth(record, config):
    input_field = config.get(
        "input_field",
        "profile_data.profile_fields.Date and Place of Birth"
    )

    date_output_field = config.get("date_output_field", "atc_birth_date")
    place_output_field = config.get("place_output_field", "atc_birth_place")

    value = get_nested_value(record, input_field, "")
    value = str(value).strip()

    if is_empty_value(value):
        record[date_output_field] = ""
        record[place_output_field] = ""
        return record

    parts = value.split(",", 1)

    first_part = parts[0].strip()
    remaining_part = parts[1].strip() if len(parts) > 1 else ""

    if is_empty_value(first_part):
        record[date_output_field] = ""
        record[place_output_field] = remaining_part
        return record

    if re.search(r"\d", first_part):
        record[date_output_field] = first_part
        record[place_output_field] = remaining_part
    else:
        record[date_output_field] = ""
        record[place_output_field] = value

    return record


def clean_atc_profile_name_fields(record, config):
    fields = config.get("fields", [])

    profile_fields = (
        record.get("profile_data", {})
        .get("profile_fields", {})
    )

    for field in fields:
        value = str(profile_fields.get(field, "")).strip()

        if is_empty_value(value):
            profile_fields[field] = ""

    return record