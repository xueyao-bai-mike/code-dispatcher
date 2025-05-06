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
        # Get all available access codes
        available_codes = redis_client.lrange('available_access_codes', 0, -1)
        
        # Get all used access codes
        used_codes = redis_client.hgetall('used_access_codes')
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'available_codes': available_codes,
                'used_codes': used_codes,
                'available_count': len(available_codes),
                'used_count': len(used_codes)
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
