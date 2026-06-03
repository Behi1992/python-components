import json
from typing import Any


def extract_values(obj: Any, path_parts: list[str]) -> list[Any]:


    if not path_parts:
        return [obj]

    current = path_parts[0]
    remaining = path_parts[1:]

    results = []

    if isinstance(obj, list):
        for item in obj:
            results.extend(extract_values(item, path_parts))

    elif isinstance(obj, dict):
        if current in obj:
            results.extend(extract_values(obj[current], remaining))

    return results


def extract_unique_values(
    input_jsonl: str,
    json_path: str,
    output_txt: str,
):
    path_parts = json_path.split(".")

    unique_values = set()

    with open(input_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)

                values = extract_values(data, path_parts)

                for value in values:

                    if value is None:
                        continue

                    if isinstance(value, (dict, list)):
                        continue

                    unique_values.add(str(value).strip())

            except Exception as e:
                print(f"Error: {e}")

    sorted_values = sorted(unique_values)

    with open(output_txt, "w", encoding="utf-8") as f:
        for value in sorted_values:
            f.write(value + "\n")

    print(f"Saved {len(sorted_values)} unique values.")