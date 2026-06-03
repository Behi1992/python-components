import pandas as pd
import json
from copy import deepcopy
from datetime import datetime
import re

DATE_PATTERNS = [
    r"\b\d{4}-\d{2}-\d{2}(?:\s\d{2}:\d{2}:\d{2})?\b",  # ISO
    r"\b\d{1,2}/\d{1,2}/\d{4}\b",                      # DD/MM/YYYY
    r"\b\d{1,2}/\d{4}\b",                              # MM/YYYY
    r"\bApproximately\s+\d{4}\b",                      # Approximately 1968
    r"\b\d{4}\b",                                      # YEAR
]


def build_date_object(raw, year="", month="", day=""):
    return {
        "date_full": raw.strip(),
        "year": year,
        "month": month,
        "day": day,
    }


def parse_date_token(token):
    token = token.strip()

    try:
        dt = datetime.strptime(token[:10], "%Y-%m-%d")
        return build_date_object(
            raw=token,
            year=str(dt.year),
            month=f"{dt.month:02}",
            day=f"{dt.day:02}",
        )
    except:
        pass

    if token.startswith("Approximately"):
        year_match = re.search(r"\d{4}", token)
        if year_match:
            return build_date_object(
                raw=token,
                year=year_match.group(),
            )

    if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", token):
        day, month, year = token.split("/")
        return build_date_object(
            raw=token,
            year=year,
            month=month.zfill(2),
            day=day.zfill(2),
        )

    if re.fullmatch(r"\d{1,2}/\d{4}", token):
        month, year = token.split("/")
        return build_date_object(
            raw=token,
            year=year,
            month=month.zfill(2),
        )

    if re.fullmatch(r"\d{4}", token):
        return build_date_object(
            raw=token,
            year=token,
        )

    return None


def normalize_date_field(raw_value):
    if not raw_value:
        return []

    text = str(raw_value)
    text = re.sub(r"\s+", " ", text)

    matches = []
    consumed_spans = []

    for pattern in DATE_PATTERNS:
        for match in re.finditer(pattern, text):
            start, end = match.span()

            overlap = False
            for s, e in consumed_spans:
                if start < e and end > s:
                    overlap = True
                    break

            if overlap:
                continue

            consumed_spans.append((start, end))
            matches.append((start, match.group()))

    matches.sort(key=lambda x: x[0])

    results = []
    seen = set()

    for _, token in matches:
        parsed = parse_date_token(token)
        if not parsed:
            continue

        key = (parsed["year"], parsed["month"], parsed["day"])

        if key in seen:
            continue

        seen.add(key)
        results.append(parsed)

    return results


def date_normalization_handler(entity, rule):
    source_path = rule["condition_path"]

    if source_path not in entity:
        return

    values = entity.get(source_path)

    if not isinstance(values, list):
        return

    normalized = []

    for item in values:
        raw_date = item.get("date_full", "")
        parsed_dates = normalize_date_field(raw_date)
        normalized.extend(parsed_dates)

    # 🔥 FIX مهم: همیشه overwrite کن
    entity[source_path] = normalized


def empty_dependency_handler(entity, rule):

    def is_empty(v):
        return v is None or v == ""

    condition_path = rule["condition_path"]
    target_path = rule["target_path"]
    value = rule["value"]

    src_list_name = condition_path.split("[]")[0].strip(".")
    tgt_list_name = target_path.split("[]")[0].strip(".")

    src_key = condition_path.split("[]")[1].strip(".")
    tgt_key = target_path.split("[]")[1].strip(".")

    if src_list_name not in entity or tgt_list_name not in entity:
        return

    src_list = entity[src_list_name]
    tgt_list = entity[tgt_list_name]

    max_len = max(len(src_list), len(tgt_list))

    while len(src_list) < max_len:
        src_list.append({})
    while len(tgt_list) < max_len:
        tgt_list.append({})

    for i in range(max_len):
        if is_empty(src_list[i].get(src_key)):
            tgt_list[i][tgt_key] = value

    entity[src_list_name] = src_list
    entity[tgt_list_name] = tgt_list


def drop_empty_special_fields(entity):

    keys_to_remove_if_empty = [
        "Reference Number",
        "comment"
    ]

    for k in keys_to_remove_if_empty:
        if k in entity:
            v = entity[k]
            if v is None or v == "" or v == []:
                del entity[k]

    return entity


HANDLERS = {
    "EMPTY_DEPENDENCY": empty_dependency_handler,
    "DATE_NORMALIZATION": date_normalization_handler,
}


def run_post_normalization(jsonl_data, rules_df):

    rules_df = rules_df.sort_values("priority")

    output = []

    for entity in jsonl_data:
        entity = deepcopy(entity)

        for _, rule in rules_df.iterrows():

            rule_type = rule["rule_type"]
            handler = HANDLERS.get(rule_type)

            if handler:
                handler(entity, rule)

        entity = drop_empty_special_fields(entity)

        output.append(entity)

    return output


def load_jsonl(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data


def save_jsonl(data, path):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def post_normalize_record(record, rules_df):
    result = run_post_normalization(
        [record],
        rules_df
    )

    if not result:
        return record

    return result[0]
