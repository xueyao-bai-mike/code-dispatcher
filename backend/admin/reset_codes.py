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
        # Delete all keys related to access codes
        redis_client.delete('available_access_codes')
        redis_client.delete('used_access_codes')
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'All access codes have been reset successfully',
                'success': True
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
