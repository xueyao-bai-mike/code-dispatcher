import json
import os
import boto3
import redis

# Initialize Redis client
redis_endpoint = os.environ.get('REDIS_ENDPOINT')
redis_port = os.environ.get('REDIS_PORT', 6379)
redis_client = redis.Redis(host=redis_endpoint, port=int(redis_port), decode_responses=True)

def lambda_handler(event, context):
    try:
        # Parse the request body
        body = json.loads(event['body'])
        
        # Extract access codes from the request
        access_codes = body.get('access_codes', [])
        
        if not access_codes:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'No access codes provided'})
            }
        
        # Store access codes in Redis
        # Using a simple list to store unused codes
        for code in access_codes:
            redis_client.rpush('available_access_codes', code)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Successfully uploaded {len(access_codes)} access codes',
                'count': len(access_codes)
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': f'Error: {str(e)}'})
        }
