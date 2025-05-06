import json
import os
import boto3
import redis
import time

# Initialize Redis client
redis_endpoint = os.environ.get('REDIS_ENDPOINT')
redis_port = os.environ.get('REDIS_PORT', 6379)
redis_client = redis.Redis(host=redis_endpoint, port=int(redis_port), decode_responses=True)

def lambda_handler(event, context):
    try:
        # Parse the request body
        body = json.loads(event['body'])
        
        # Extract user identifier from the request
        user_id = body.get('user_id')
        
        if not user_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'User ID is required'})
            }
        
        # Check if user already has an access code
        existing_code = redis_client.hget('used_access_codes', user_id)
        if existing_code:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'access_code': existing_code,
                    'message': 'You have already been assigned an access code'
                })
            }
        
        # Get an access code from the available pool
        access_code = redis_client.lpop('available_access_codes')
        
        if not access_code:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'No access codes available'})
            }
        
        # Assign the access code to the user
        redis_client.hset('used_access_codes', user_id, access_code)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'access_code': access_code,
                'message': 'Access code assigned successfully'
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
