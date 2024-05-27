import sys
import logging
import json

import boto3
from toolbox import read_ssm_parameter

API_KEY_KEY = '/api/stock/finhub-key'
PORTFOLIO_KEY = '/api/stock/portfolio'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
api_key = None
portfolio = None

try:
    ssm_client = boto3.client('ssm')
    api_key = read_ssm_parameter(API_KEY_KEY, ssm_client)
    wrk = read_ssm_parameter(PORTFOLIO_KEY, ssm_client)
    portfolio = json.loads(wrk)
except Exception as wtf:
    logger.error(wtf, exc_info=True)

html_start = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
        }
        table {
            border-collapse: collapse;
            width: 50%;
        }
        th, td {
            border: 1px solid #000;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <table>
        <thead>
            <tr>
                <th>Symbol</th>
                <th>Value</th>
                <th>Value Change</th>
            </tr>
        </thead>
        <tbody>
'''

html_finish = '''        </tbody>
    </table>
</body>
</html>
'''

if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stdout,
        format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
        datefmt='%Y/%m/%d-%H:%M:%S'
    )

    logger.info(f'{api_key=}')
    logger.info(f'portifolio={json.dumps(portfolio, indent=2)}')
