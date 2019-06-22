import itsdangerous
from . import constants

def lambda_handler(event, context):
    '''
    '''
    signature = event['queryStringParameters']['signature']
    id = itsdangerous.Signer(constants.SECRET).unsign(signature).decode('utf8')
    
    return {
        'statusCode': '200',
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': {
            'id': id,
            }
        }
