import sys
import boto3

if len(sys.argv) == 2:
    config_key = sys.argv[1]
else:
    config_key = '/api/stock/dev.ini'

def get_config(key):
    ssm_client = boto3.client('ssm')
    value = None

    try:
        response = ssm_client.get_parameter(Name=key, WithDecryption=True)
        value = response.get('Parameter', {}).get('Value', None)
    except Exception as wtf:
        print(f'error: reading "{config_key}" casused "{wtf}"')
        sys.exit(1)

    return value


if __name__ == '__main__':
    wrk = get_config(config_key)
    print(wrk)
