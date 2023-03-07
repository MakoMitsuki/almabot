# Almabot
Fork of Almabot originally written by [Alma Emma](https://github.com/AlmaEmma)

## Prerequisites
- Python 3 (3.11.2)
- Discord.py (2.2.2)
- Schedule
- gspread
    - You will need separate keys for this, see `client_secret_sample.json`
- python-dotnev

## How to run
1. Clone the project
2. Install the prerequisites
3. Copy `.env.sample`, rename to `.env`, and fill in the blanks on the .env with tokens, etc.
4. Do the same above to `client_secret_sample.json` which you will be renaming to `client_secret.json`
4. Run using `python3 Almabot.py`