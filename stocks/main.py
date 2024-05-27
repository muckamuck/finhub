import os
import sys
import json
import requests
import logging
from io import StringIO

import boto3
from toolbox import read_ssm_parameter
from cfg import portfolio
from cfg import api_key
from cfg import html_start
from cfg import html_finish

from flask import request
from zevon import FlaskLambda

'''
The FlaskLambda object that is created is the entry point for the lambda. The
LambdaTool deployer expects this to be called 'lambda_handler'
'''
lambda_handler = FlaskLambda(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@lambda_handler.route('/', methods=['GET'])
@lambda_handler.route('/portfolio', methods=['GET'])
def OK():
    '''
    Redirect to the README doc

    Args:
        None

    Returns:
        tuple of (body, status code, content type) that API Gateway understands
    '''
    report = make_report()
    return (
        report,
        200,
        {'Content-Type': 'text/html'}
    )


def get_current_price(symbol):
    url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}'
    response = requests.get(url)
    data = response.json()
    return data


def make_report():
    buf = StringIO()
    total_value = 0
    total_change = 0

    try:
        buf.write(html_start)
        for k in portfolio.keys():
            buf.write('            <tr>\n')
            count = float(portfolio.get(k))
            the_data = get_current_price(k)
            val = the_data.get('c') * count
            delta_val = the_data.get('d') * count
            total_value = total_value + val
            total_change = total_change + delta_val
            # print(f'{k}\t{val:.2f}\t{delta_val:.2f}')
            buf.write(f'                <td>{k}</td><td>{val:.2f}</td><td>{delta_val:.2f}</td>\n')
            buf.write('            </tr>\n')

        buf.write(f'                <td><strong>TOTAL</strong></td><td><strong>${total_value:.2f}</strong></td><td><strong>${total_change:.2f}</strong></td>\n')
        # print(f'TOTAL\t{total_value:.2f}\t{total_change:.2f}')
        buf.write(html_finish)
        return buf.getvalue()
    except Exception as wtf:
        logger.info(wtf, exc_info=True)


if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stdout,
        format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
        datefmt='%Y/%m/%d-%H:%M:%S'
    )
    # lambda_handler.run(debug=True)
    report = make_report()
    print(report)
