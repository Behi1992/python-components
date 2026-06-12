import json

json_file = r"/Users/mac/Desktop/VV_Python_Project/parsing/EU_full.jsonl"
OUTPUT_SCHEMA_FILE = "EU_full_schema.json"


schema = {}
total_records = 0


def detect_type(value):

    if isinstance(value, dict):
        return "object"

    if isinstance(value, list):
        return "array"

    if isinstance(value, bool):
        return "boolean"

    if isinstance(value, int):
        return "integer"

    if isinstance(value, float):
        return "float"

    if value is None:
        return "null"

    return "string"


def merge_types(old_type, new_type):

    if old_type == new_type:
        return old_type

    types = set(old_type.split(" | "))
    types.add(new_type)

    return " | ".join(sorted(types))


def update_schema(data, path=""):

    global schema

    if isinstance(data, dict):

        for key, value in data.items():

            full_path = f"{path}.{key}" if path else key

            value_type = detect_type(value)

            if full_path not in schema:

                schema[full_path] = {
                    "type": value_type,
                    "count": 1
                }

            else:

                schema[full_path]["type"] = merge_types(
                    schema[full_path]["type"],
                    value_type
                )

                schema[full_path]["count"] += 1

            update_schema(value, full_path)

    elif isinstance(data, list):

        array_path = f"{path}[]"

        if array_path not in schema:

            schema[array_path] = {
                "type": "array",
                "count": 1
            }

        else:
            schema[array_path]["count"] += 1

        for item in data:
            update_schema(item, array_path)


with open(json_file, "r", encoding="utf-8") as f:

    for line in f:

        line = line.strip()

        if not line:
            continue

        try:

            data = json.loads(line)

            update_schema(data)

            total_records += 1

        except Exception as e:

            print("Error:", e)


final_schema = {}

for field, info in schema.items():

    final_schema[field] = {
        "type": info["type"],
        "optional": info["count"] < total_records,
        "occurrences": info["count"]
    }


with open(OUTPUT_SCHEMA_FILE, "w", encoding="utf-8") as f:

    json.dump(final_schema, f, ensure_ascii=False, indent=4)


print("Done:", total_records)
print("Schema fields:", len(final_schema))