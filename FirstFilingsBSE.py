from datetime import datetime, timedelta
from bse import BSE
import time


filing_category = 'Company Update'
subcategory_general = "General" 

filing_subcategory = {
    # "Concall Intimation": [
    #     "Analyst / Investor Meet"
    # ],
    # "Press Release": [
    #     "Press Release / Media Release",
    #     "Press Release / Media Release (Revised)",
    #     "Press release (Revised)"
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
    results_list = [] 
    results = {}
    for subcat_label, subcats in filing_subcategory.items():
        for subcat in subcats:
            key = f"{subcat_label} - {subcat}"
            ann = fetch_paginated_announcements(
                bse,
                from_date=date,
                to_date=date,
                category=filing_category,
                subcategory=subcat
            )
            time.sleep(1)  # Sleep to avoid hitting API rate limits
            
            # Only filter if ann is a list (not an error string)
            if isinstance(ann, list):
                # For 'General' subcategory, filter by keyword in NEWSSUB or HEADLINE
                if subcat == subcategory_general and subcat_label in filing_subcategory_general_keyword:
                    keyword = filing_subcategory_general_keyword[subcat_label]
                    ann = [
                        filing for filing in ann
                        if (
                            (filing.get("NEWSSUB") and keyword.lower() in filing["NEWSSUB"].lower())
                            or (filing.get("HEADLINE") and keyword.lower() in filing["HEADLINE"].lower())
                        )
                    ]
                results_list.extend(ann)
            else:
                print(f"  Error fetching announcements for {subcat_label} - {subcat}: {ann}")
        results[subcat_label] = results_list
    print("Done fetching all announcements for the date.")
    return results


def is_first_filing(bse, scrip_cd, subcat_label, input_date, lookback_years):
    """Check if this is the first filing for the scrip/subcategory label in the lookback period."""
    print(f" Checking if it is the first {subcat_label} for SCRIP CODE={scrip_cd} in the last {lookback_years} years ...")
    lookback_start = input_date - timedelta(days=lookback_years * 365)
    all_filings = []
    for subcat in filing_subcategory[subcat_label]:
        retries = 0
        while retries < 3:
            filings = fetch_paginated_announcements(
                bse,
                from_date=lookback_start,
                to_date=input_date,
                category=filing_category,
                subcategory=subcat,
                scripcode=scrip_cd
            )
            if isinstance(filings, str):  # error string
                print(f"    Error fetching filings for {subcat}: {filings} (retry {retries+1}/3)")
                retries += 1
                time.sleep(3)
            else:
                break
        if isinstance(filings, str):  # still error after retries
            print(f"    Failed to fetch filings for {subcat} after 3 retries, skipping.")
            continue
        # For 'General' subcategory, filter by keyword in NEWSSUB or HEADLINE
        if subcat == subcategory_general and subcat_label in filing_subcategory_general_keyword:
            keyword = filing_subcategory_general_keyword[subcat_label]
            filings = [
                filing for filing in filings
                if (
                    (filing.get("NEWSSUB") and keyword.lower() in filing["NEWSSUB"].lower())
                    or (filing.get("HEADLINE") and keyword.lower() in filing["HEADLINE"].lower())
                )
            ]
        all_filings.extend(filings)
    return len(all_filings) == 1, all_filings[0]["SLONGNAME"] if all_filings else None


def main():
    import sys
    # Usage: python FirstFilingsToday.py [YYYY-MM-DD] [LOOKBACK_YEARS]
    if len(sys.argv) > 1:
        input_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
    else:
        input_date = datetime.now()
    if len(sys.argv) > 2:
        lookback_years = int(sys.argv[2])
    else:
        lookback_years = 15

    print(f"Beginning: BSE First Filings for {input_date.strftime('%Y-%m-%d')} with lookback period {lookback_years} years...")
    bse = BSE(download_folder=".")
    announcements = fetch_announcements_for_date(bse, input_date)

    first_filings = {}
    for subcat_label, filings in announcements.items():
        if not isinstance(filings, list):
            continue
        for filing in filings:
            scrip_cd = filing.get("SCRIP_CD")
            if not scrip_cd:
                continue
            is_first, slongname = is_first_filing(bse, scrip_cd, subcat_label, input_date, lookback_years)
            if is_first and slongname:
                first_filings.setdefault(subcat_label, []).append({"slongname": slongname, "scripcode": scrip_cd})

    print("\nFirst filings in the last {} years as on {}:".format(lookback_years, input_date.strftime('%Y-%m-%d')))
    for subcat_label, entries in first_filings.items():
        for entry in entries:
            print(f"  {subcat_label} : {entry['slongname']} (SCRIP_CD={entry['scripcode']})")

    print("Done.")


if __name__ == "__main__":
    main()




