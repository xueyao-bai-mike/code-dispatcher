# Access Code Dispatcher

A serverless web application for dispatching access codes to users. The application consists of an admin portal for uploading access codes and a user portal for users to retrieve their access codes.

## Architecture

- **Frontend**: Static website hosted on S3 and served through CloudFront
- **Backend**: AWS Lambda functions
- **Storage**: ElastiCache Redis for storing access codes
- **API**: API Gateway for REST endpoints

## Features

### Admin Portal
- Upload multiple access codes at once
- View available and used access codes
- Reset all access codes with a single click
- Monitor usage statistics

### User Portal
- Request an access code by providing a user ID
- View assigned access code
- Simple and intuitive interface

## Project Structure

```
access-code-dispatcher/
├── backend/
│   ├── admin/
│   │   ├── upload_codes.py
│   │   ├── list_codes.py
│   │   └── reset_codes.py
│   ├── user/
│   │   └── get_code.py
│   └── requirements.txt
├── frontend/
│   ├── admin/
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── script.js
│   └── user/
│       ├── index.html
│       ├── styles.css
│       └── script.js
├── infrastructure/
│   ├── app.py
│   └── requirements.txt
└── README.md
```

## Deployment Instructions

### Prerequisites
- AWS CLI configured with appropriate permissions
- Node.js and npm installed
- Python 3.9 or later
- AWS CDK installed

### Steps to Deploy

1. Install CDK dependencies:
   ```
   cd infrastructure
   pip install -r requirements.txt
   ```

2. Bootstrap your AWS environment (if not already done):
   ```
   cdk bootstrap aws://ACCOUNT-NUMBER/REGION
   ```

3. Deploy the stack:
   ```
   cdk deploy
   ```

4. After deployment, note the CloudFront URL and API Gateway URL from the outputs.

5. Update the API endpoint in the frontend code:
   - Open `frontend/admin/script.js` and `frontend/user/script.js`
   - Replace `https://YOUR_API_GATEWAY_URL` with the actual API Gateway URL

6. Redeploy the frontend:
   ```
   aws s3 sync frontend/ s3://YOUR_S3_BUCKET_NAME/
   ```

## Technologies Used

- **AWS Services**: Lambda, API Gateway, S3, CloudFront, ElastiCache Redis, VPC
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python
- **Infrastructure as Code**: AWS CDK

## Notes
- This application does not include authentication or user management
- Access codes are stored in ElastiCache Redis and are not persisted long-term
- The application is designed to be simple and can be extended as needed
