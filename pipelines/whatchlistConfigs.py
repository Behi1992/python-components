# pipelines/watchlist_configs.py

WATCHLIST_CONFIGS = {
    "UKSL": {
        "source_name": "UKSL",
        "url": "https://sanctionslist.fcdo.gov.uk/docs/UK-Sanctions-List.xml",
        "file_type": "xml",
        "root_tag": "Designation",
        "schedule": "daily",
    },

    "AUSTRALIA": {
        "source_name": "AUSTRALIA",
        "url": "https://www.dfat.gov.au/sites/default/files/Australian_Sanctions_Consolidated_List.xlsx",
        "file_type": "excel",
        "sheet_name": 0,
        "schedule": "monthly",
    },

    "OFAC-SDN": {
        "source_name": "OFAC-SDN",
        "url": "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN_ENHANCED.XML",
        "file_type": "xml",
        "root_tag": "SanctionsEntry",
        "schedule": "daily",
    },
}