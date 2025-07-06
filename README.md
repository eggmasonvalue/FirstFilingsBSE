# FirstFilings
A script to fetch and analyze BSE corporate announcements, identifying first-time filings for each company in a given subcategory in the given lookback period.

## Value Proposition
The first investor presentation, analyst or earnings call intimation or media release often signifies the start of the market's discovery of the company or the promoter's interest in value creation via market capitalisation increase, often leading to rapid rerating.

## Usage
```bash
python FirstFilingsToday.py [YYYY-MM-DD] [LOOKBACK_YEARS]
```
- `YYYY-MM-DD`: Date to fetch announcements for (default: today)
- `LOOKBACK_YEARS`: Number of years to look back for first filings (default: 15)

## Requirements

- Python 3.8+
- Install dependencies:
  ```
  pip install -r requirements.txt
  ```

## Files

- `FirstFilingsToday.py` - Main script

## License

See [LICENSE](LICENSE).
