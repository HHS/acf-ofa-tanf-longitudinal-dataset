"""Download CPI-U HTML Table"""

import os

import requests

from otld.paths import inter_dir


def get_cpi_u():
    session = requests.Session()
    data = {
        "request_action": "get_data",
        "reformat": True,
        "from_results_page": True,
        "years_option": "specific_years",
        "delimiter": "comma",
        "output_type": "multi",
        "periods_option": "all_periods",
        "output_view": "data",
        "to_year": "2024",
        "from_year": "1913",
        "output_format": "excelTable",
        "original_output_type": "default",
        "annualAveragesRequested": True,
        "series_id": "CUUR0000SA0",
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "JSESSIONID=371256F87D766E4527F315F573C8577A._t4_06v; nmstat=cce3aa2c-671c-e8a8-c4f6-167264c62b99; _ga=GA1.1.1240173450.1734972904; touchpoints=true; _ga_CSLL4ZEK4L=GS1.1.1735842297.5.1.1735844409.0.0.0",
        "Origin": "https://data.bls.gov",
        "Referer": "https://data.bls.gov/timeseries/CUUR0000SA0/pdq/SurveyOutputServlet",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    session.headers.update(headers)
    url = "https://data.bls.gov/pdq/SurveyOutputServlet"

    response = requests.post(url, data=data)
    with open(os.path.join(inter_dir, "cpi_u.xlsx"), "wb") as f:
        f.write(response.content)
