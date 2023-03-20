# Almabot
Re-host of Almabot originally written by [Alma Emma](https://github.com/AlmaEmma)

A fun little sort of dive back into Python even if I really suck at it.
See original code under `/original` folder

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
5. Create a `nitro_data.json` file with the following structure
```
{
    "idhere": {
       "Name": "",
       "Display Name": "",
       "Nitro Start": "",
       "Nitro Status": "",
       "Nitro Total": "",
       "gspread Index": "",
       "emoji": "1"
    },
    ...
}
```
6. Run using `python3 Almabot.py`
