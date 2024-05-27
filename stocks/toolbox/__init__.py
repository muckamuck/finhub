'''
A collection of shared stuff for this Lambda function
'''
# pylint: disable=broad-except
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=pointless-string-statement
# pylint: disable=no-else-raise

import sys
import logging
import datetime
import json
from io import BytesIO

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def date_converter(o):
    '''
    Helper thing to convert dates for JSON modulet.

    Args:
        o - the thing to dump as string.

    Returns:
        if an instance of datetime the a string else None
    '''
    if isinstance(o, datetime.datetime):
        return o.__str__()

    return None


def read_ssm_parameter(key, ssm_client):
    '''
    Helper thing to read SSM parameters

    Args:
        key - key to read from SSM

    Returns:
        value or None
    '''
    value = None
    if ssm_client is None:
        ssm_client = boto3.client('ssm')

    try:
        response = ssm_client.get_parameter(Name=key, WithDecryption=True)
        value = response.get('Parameter', {}).get('Value', None)
    except Exception as wtf:
        logger.warning('reading "%s" casused "%s"', key, wtf)

    return value


def is_object(bucket, key, s3_client):
    '''
    Determine if the given bucket/key is a thing

    Args:
        bucket - bucket of interest
        key - object key of interest
        s3_client - Boto3 client

    Returns:
        Extistence or Not extistence; True or False
    '''
    try:
        response = s3_client.head_object(
            Bucket=bucket,
            Key=key
        )
        logger.debug(json.dumps(response, indent=2, default=date_converter))
        return True
    except NoCredentialsError as nce:
        logger.error(nce)
    except Exception as wtf:
        error = wtf.response.get('Error', {}).get('Code', 500)
        if error == '404':
            logger.debug('head_object: %s => %s', wtf, error)
        else:
            logger.error('head_object: %s => %s', wtf, error)

    return False


def get_object_age(bucket, key, s3_client):
    '''
    Determine if the given bucket/key is a thing

    Args:
        bucket - bucket of interest
        key - object key of interest
        s3_client - Boto3 client

    Returns:
        Extistence or Not extistence; True or False
    '''
    try:
        response = s3_client.head_object(
            Bucket=bucket,
            Key=key
        )

        then = response.get('LastModified')
        return datetime.datetime.now().timestamp() - then.timestamp()
    except Exception as wtf:
        logger.error(wtf, exc_info=True)

    return None

def get_object_size(bucket, key, s3_client):
    '''
    Determine if the given bucket/key is a thing

    Args:
        bucket - bucket of interest
        key - object key of interest
        s3_client - Boto3 client

    Returns:
        Extistence or Not extistence; True or False
    '''
    try:
        response = s3_client.head_object(
            Bucket=bucket,
            Key=key
        )
        logger.debug(json.dumps(response, indent=2, default=date_converter))
        return response.get('ContentLength', -1)
    except NoCredentialsError as nce:
        logger.error(nce)
    except Exception as wtf:
        error = wtf.response.get('Error', {}).get('Code', 500)
        if error == '404':
            logger.debug('head_object: %s => %s', wtf, error)
        else:
            logger.error('head_object: %s => %s', wtf, error)

    return -1


def put_object(bucket, key, the_data, s3_client, **kwargs):
    '''
    Put a blob of data into an S3 object

    Args:
        bucket - the S3 bucket to accecpt the data
        key - the object key
        the_data - object contents
        s3_client - boto3 client to put the data
        kwargs[dryrun] - do or do not
    '''
    try:
        logger.info('put_object() called')
        dryrun = kwargs.get('dryrun', True)
        read_grants = kwargs.get('readGrants')
        full_grants = kwargs.get('fullGrants')
        logger.info('put_object() for s3://%s/%s dryrun=%s', bucket, key, dryrun)
        if dryrun:
            return True

        if None in [read_grants, full_grants]:
            response = s3_client.put_object(
                Bucket=bucket,
                ACL='bucket-owner-full-control',
                Key=key,
                Body=the_data,
                ServerSideEncryption='AES256'
            )
        else:
            response = s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=the_data,
                ServerSideEncryption='AES256',
                GrantRead=read_grants,
                GrantFullControl=full_grants
            )

        logger.info(json.dumps(response, indent=2, default=date_converter))
        return True
    except Exception as wtf:
        logger.error(wtf, exc_info=True)

    return False


def get_object(bucket, key, s3_client):
    '''
    Put a blob of data into an S3 object

    Args:
        bucket - the S3 bucket to accecpt the data
        key - the object key
        s3_client - boto3 client to put the data

    Returns:
        the data in the S3 object
    '''
    try:
        the_data = BytesIO(s3_client.get_object(Bucket=bucket, Key=key)["Body"].read())
        return the_data
    except Exception as wtf:
        logger.error(wtf, exc_info=True)

    return None


def split_list(the_list, thing_count):
    '''
    Split a list into a list of lists

    Args:
        the_list - the list to split up
        thing_count - number of things in the parts

    Returns:
        A list of lists
    '''
    buf = []
    tmp = []
    for thing in the_list:
        tmp.append(thing)
        if len(tmp) >= thing_count:
            buf.append(tmp)
            tmp = []

    if len(tmp) > 0:
        buf.append(tmp)

    return buf


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
        datefmt='%Y/%m/%d-%H:%M:%S'
    )

    s3_client = boto3.client('s3')
    the_data = get_object('specify-a-bucket', 'zex-dev-template-1548878441.json', s3_client)
    print(f'get_object() returned something of type={type(the_data)}')
    sz = get_object_size('specify-a-bucket', 'zex-dev-template-1548878441.json', s3_client)
    print(f'sz = {sz}')
    age = get_object_age('specify-a-bucket', 'zex-dev-template-1548878441.json', s3_client)
    print(age)
    age = get_object_age('takle', 'ARCHIVE/water-sensor/reading.log', s3_client)
    print(age)
