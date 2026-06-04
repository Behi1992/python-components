from nameparser import HumanName


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