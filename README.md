# FirstFilings
A script to fetch and analyze BSE corporate announcements, identifying first-time filings for each company in a given subcategory in the given lookback period.

## Value Proposition
The first investor presentation, analyst or earnings call intimation or media release often signifies the start of the market's discovery of the company or the promoter's interest in value creation via market capitalisation increase, often leading to rapid rerating.

## Usage
```bash
python FirstFilingsBSE.py [OPTION] DD-MM-YYYY [LOOKBACK_YEARS]
```
### Options

- `-D DD-MM-YYYY`  
  Fetch filings for the given day only.

- `-WTD DD-MM-YYYY`  
  Fetch filings for the week-to-date (Monday to the given date, inclusive).

- `-MTD DD-MM-YYYY`  
  Fetch filings for the month-to-date (first day of the month to the given date, inclusive).

- `-QTD DD-MM-YYYY`  
  Fetch filings for the quarter-to-date (first day of the quarter to the given date, inclusive).

If no option is given, the script defaults to the given date only.

### Examples

- Filings for a single day:
  ```bash
  python FirstFilingsBSE.py -D 07-06-2024
  ```

- Filings for week-to-date ending 07-06-2024:
  ```bash
  python FirstFilingsBSE.py -WTD 07-06-2024
  ```

- Filings for month-to-date ending 07-06-2024:
  ```bash
  python FirstFilingsBSE.py -MTD 07-06-2024
  ```

- Filings for quarter-to-date ending 07-06-2024:
  ```bash
  python FirstFilingsBSE.py -QTD 07-06-2024
  ```

- Specify lookback period (in years):
  ```bash
  python FirstFilingsBSE.py -WTD 07-06-2024 10
  ```

- Sample input
```bash
  python FirstFilingsBSE.py -D 29-05-2025 5
```

- Sample Final Output:
```bash
************************************************************
First filings in the last 5 years as on 2025-05-29:
  Press Release        : Network People Services Technologies Ltd
  Press Release        : Denta Water and Infra Solutions Ltd
************************************************************
```
  
## Requirements

- Python 3.8+
- Install dependencies:
  ```
  pip install -r requirements.txt
  ```

## Files

- `FirstFilingsBSE.py` - Main script

## License

See [LICENSE](LICENSE).
