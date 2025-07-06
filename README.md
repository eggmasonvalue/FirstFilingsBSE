# FirstFilings
A script to fetch and analyze BSE corporate announcements, identifying first-time filings for each company in a given subcategory in the given lookback period.

## Value Proposition
The first investor presentation, analyst or earnings call intimation or media release often signifies the start of the market's discovery of the company or the promoter's interest in value creation via market capitalisation increase, often leading to rapid rerating.

## Usage
```bash
python FirstFilingsBSE.py [YYYY-MM-DD] [LOOKBACK_YEARS]
```
- `YYYY-MM-DD`: Date to fetch announcements for (default: today)
- `LOOKBACK_YEARS`: Number of years to look back for first filings (default: 15)

Examples:
```bash
python FirstFilingsBSE.py
python FirstFilingsBSE.py 2025-07-06
python FirstFilingsBSE.py 2025-07-06 5
```
## Upcoming features
- Use filings within a week, a month or a quarter from the specified date to check whether it's a first filing(currently only a single day).

  
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
