# pipelines/watchlist_configs.py
WATCHLIST_CONFIGS = {

    "UKSL": {
        "source_name": "UKSL",
        "url": "https://sanctionslist.fcdo.gov.uk/docs/UK-Sanctions-List.xml",
        "file_type": "xml",
        "root_tag": "Designation",
        "schedule": "daily",
    },

    "OFAC-SDN": {
        "source_name": "OFAC-SDN",
        "url": "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN_ENHANCED.XML",
        "file_type": "xml",
        "root_tag": "entity",
        "schedule": "daily",
    },

    "OFAC-NON-SDN": {
        "source_name": "OFAC-NON-SDN",
        "url": "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/CONS_ENHANCED.XML",
        "file_type": "xml",
        "root_tag": "entity",
        "schedule": "daily",
    },

    "DFAT": {
        "source_name": "DFAT",
        "url": "https://www.dfat.gov.au/sites/default/files/Australian_Sanctions_Consolidated_List.xlsx",
        "file_type": "xlsx",
        "schedule": "daily",
    },

}