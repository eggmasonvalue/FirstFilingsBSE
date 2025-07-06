from datetime import datetime, timedelta
from bse import BSE
import time

TOTAL_RETRIES = 5  # Number of retries for fetching filings
RETRY_DELAY = 3  # Delay in seconds between retries

filing_category = 'Company Update'
subcategory_general = "General" 

filing_subcategory = {
    "Concall Intimation": [
        "Analyst / Investor Meet"
    ],
    # "Press Release": [
    #     "Press Release / Media Release",
    #     "Press Release / Media Release (Revised)", 
    #     "Press release (Revised)"
    #     it can't be the first filing if it is a revised press release
    # ],
    "PPT": [
        "Investor Presentation",
        subcategory_general
    ]
}

filing_subcategory_general_keyword = {
    # "Concall Intimation": 
    #     "Analyst / Investor Meet",
    # "Press Release":
    #     "Release",
    "PPT": "Presentation"
}


def fetch_paginated_announcements(
    bse,
    from_date,
    to_date,
    category,
    subcategory,
    scripcode=None,
    segment="equity"
):
    """Fetch all paginated announcements for given filters."""
    all_ann = []
    page_count = 1
    total_count = None
    while True:
        try:
            data = bse.announcements(
                page_no=page_count,
                from_date=from_date,
                to_date=to_date,
                category=category,
                subcategory=subcategory,
                scripcode=str(scripcode) if scripcode else None,
                segment=segment
            )
            if total_count is None:
                total_count = (
                    data.get("Table1", [{}])[0].get("ROWCNT", 0)
                    if data.get("Table1") else 0
                )
            page_ann = data.get("Table", [])
            all_ann.extend(page_ann)
            if len(all_ann) >= total_count or not page_ann:
                break
            page_count += 1
        except Exception as e:
            return f"Error: {e}"
    return all_ann


def fetch_announcements_for_date(bse, date: datetime):
    """Fetch all announcements for each subcategory on a given date."""
    print(f"Fetching announcements for {date.strftime('%Y-%m-%d')} ...")
    results = {}
    for subcat_label, subcats in filing_subcategory.items():
        results_list = [] 
        for subcat in subcats:
            # key = f"{subcat_label} - {subcat}"
            # print(key)
            retries = 0
            ann = None
            while retries < TOTAL_RETRIES:
                ann = fetch_paginated_announcements(
                    bse,
                    from_date=date,
                    to_date=date,
                    category=filing_category,
                    subcategory=subcat
                )
                # Improved error check: treat only str as error, otherwise treat as valid result
                if isinstance(ann, str):
                    print(f"  Error fetching announcements for {subcat_label} - {subcat}: {ann} (retry {retries+1}/{TOTAL_RETRIES})")
                    retries += 1
                    time.sleep(RETRY_DELAY)
                elif isinstance(ann, list):
                    # print(f"  Successfully fetched announcements for {subcat_label} - {subcat}")
                    break
                else:
                    print(f"  Unexpected result type for {subcat_label} - {subcat}: {type(ann)}. Skipping.")
                    ann = []
                    break
            if isinstance(ann, str):
                print(f"  Failed to fetch announcements for {subcat_label} - {subcat} after {TOTAL_RETRIES} retries, skipping.")
                continue

            # Only filter if ann is a list (not an error string)
            if isinstance(ann, list):
                # For 'General' subcategory, filter by keyword in NEWSSUB or HEADLINE
                if subcat == subcategory_general and subcat_label in filing_subcategory_general_keyword:
                    keyword = filing_subcategory_general_keyword[subcat_label]
                    ann = [
                        filing for filing in ann
                        if (
                            (isinstance(filing, dict) and filing.get("NEWSSUB") and keyword.lower() in filing["NEWSSUB"].lower())
                            or (isinstance(filing, dict) and filing.get("HEADLINE") and keyword.lower() in filing["HEADLINE"].lower())
                        )
                    ]
                results_list.extend(ann)
        results[subcat_label] = results_list
    print("Done fetching all announcements for the date.")
    return results


def is_first_filing(bse, scrip_cd, subcat_label, input_date, lookback_years, longname):
    """Check if this is the first filing for the scrip/subcategory label in the lookback period."""
    lookback_start = input_date - timedelta(days=lookback_years * 365)
    print(f" Checking if it is the first {subcat_label} for {longname} in the last {lookback_years} years ...")
    all_filings = []
    for subcat_values in filing_subcategory[subcat_label]:
        retries = 0
        filings = None
        while retries < TOTAL_RETRIES:
            filings = fetch_paginated_announcements(
                bse,
                from_date=lookback_start,
                to_date=input_date,
                category=filing_category,
                subcategory=subcat_values,
                scripcode=scrip_cd
            )
            # Improved error check: treat only str as error, otherwise treat as valid result
            if isinstance(filings, str):
                print(f"    Error fetching filings for {longname}: {filings} (retry {retries+1}/{TOTAL_RETRIES})")
                retries += 1
                time.sleep(RETRY_DELAY)
            elif isinstance(filings, list):
                # print(f"    Successfully fetched filings for {longname} - {subcat_values}")
                break
            else:
                print(f"    Unexpected result type for {longname} - {subcat_values}: {type(filings)}. Skipping.")
                filings = []
                break
        if isinstance(filings, str):
            print(f"    Failed to fetch filings for {subcat_values} after {TOTAL_RETRIES} retries, skipping.")
            continue

        # dump into json file for debugging
        # with open(f"filings_{scrip_cd}_{subcat_label}.json", "w") as f:
        #     import json
        #     json.dump(filings, f, indent=4) 
        # For 'General' subcategory, filter by keyword in NEWSSUB or HEADLINE
        if subcat_values == subcategory_general and subcat_label in filing_subcategory_general_keyword:
            keyword = filing_subcategory_general_keyword[subcat_label]
            filings = [
                filing for filing in filings
                if (
                    (isinstance(filing, dict) and filing.get("NEWSSUB") and keyword.lower() in filing["NEWSSUB"].lower())
                    or (isinstance(filing, dict) and filing.get("HEADLINE") and keyword.lower() in filing["HEADLINE"].lower())
                )
            ]
        all_filings.extend(filings)
    # Defensive: Only return True if there is exactly one filing, and at least one subcat succeeded
    if all_filings:
        return len(all_filings) == 1
    else:
        return False


def main():
    import sys
    # Usage: python FirstFilingsToday.py [YYYY-MM-DD] [LOOKBACK_YEARS]
    if len(sys.argv) > 1:
        input_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
    else:
        input_date = datetime.now()
    if len(sys.argv) > 2:
        lookback_years = int(sys.argv[2])
        # print(f"Using lookback period of {lookback_years} years.")
    else:
        lookback_years = 15

    print(f"Starting: BSE First Filings for {input_date.strftime('%Y-%m-%d')} with lookback period {lookback_years} years...")
    bse = BSE(download_folder=".")
    announcements = fetch_announcements_for_date(bse, input_date)

    # dump to json file for debugging
    # with open(f"announcements_{input_date.strftime('%Y-%m-%d')}.json", "w") as f:
    #     import json
    #     json.dump(announcements, f, indent=4)

    first_filings = {}
    for subcat_label, filings in announcements.items():
        if not isinstance(filings, list):
            continue
        for filing in filings:
            scrip_cd = filing.get("SCRIP_CD")
            longname = filing.get("SLONGNAME")
            if not scrip_cd:
                continue
            is_first = is_first_filing(bse, scrip_cd, subcat_label, input_date, lookback_years, longname)
            if is_first and longname:
                first_filings.setdefault(subcat_label, []).append(longname)

    # Highlighted output
    print("\n" + "*" * 60)
    print("First filings in the last {} years as on {}:".format(lookback_years, input_date.strftime('%Y-%m-%d')))
    for subcat_label, names in first_filings.items():
        for name in names:
            print(f"  {subcat_label:<20} : {name}")
    print("*" * 60 + "\n")

    print("Done.")


if __name__ == "__main__":
    main()




