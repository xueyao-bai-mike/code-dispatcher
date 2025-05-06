#!/usr/bin/env python3
from aws_cdk import (
    App,
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    Environment,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_elasticache as elasticache,
    aws_ec2 as ec2,
)

class AccessCodeDispatcherStack(Stack):
    def __init__(self, scope: App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC for ElastiCache
        vpc = ec2.Vpc(
            self, "AccessCodeDispatcherVPC",
            max_azs=2,
            nat_gateways=1
        )
        
        # Create ElastiCache Redis cluster
        redis_subnet_group = elasticache.CfnSubnetGroup(
            self, "RedisSubnetGroup",
            description="Subnet group for Redis cluster",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets]
        )
        
        redis_security_group = ec2.SecurityGroup(
            self, "RedisSecurityGroup",
            vpc=vpc,
            description="Security group for Redis cluster",
            allow_all_outbound=True
        )
        
        redis_security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(6379),
            "Allow Redis access from within VPC"
        )
        
        redis_cluster = elasticache.CfnCacheCluster(
            self, "RedisCluster",
            cache_node_type="cache.t3.micro",
            engine="redis",
            num_cache_nodes=1,
            cache_subnet_group_name=redis_subnet_group.ref,
            vpc_security_group_ids=[redis_security_group.security_group_id]
        )
        
        # Create Lambda functions
        lambda_layer = _lambda.LayerVersion(
            self, "RedisLayer",
            code=_lambda.Code.from_asset("../backend"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="Layer containing Redis package"
        )
        
        # Common Lambda environment variables
        lambda_env = {
            "REDIS_ENDPOINT": redis_cluster.attr_redis_endpoint_address,
            "REDIS_PORT": "6379"
        }
        
        # Admin Lambda functions
        upload_codes_lambda = _lambda.Function(
            self, "UploadCodesFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("../backend"),
            handler="admin.upload_codes.lambda_handler",
            environment=lambda_env,
            vpc=vpc,
            layers=[lambda_layer],
            timeout=Duration.seconds(30)
        )
        
        list_codes_lambda = _lambda.Function(
            self, "ListCodesFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("../backend"),
            handler="admin.list_codes.lambda_handler",
            environment=lambda_env,
            vpc=vpc,
            layers=[lambda_layer],
            timeout=Duration.seconds(30)
        )
        
        reset_codes_lambda = _lambda.Function(
            self, "ResetCodesFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("../backend"),
            handler="admin.reset_codes.lambda_handler",
            environment=lambda_env,
            vpc=vpc,
            layers=[lambda_layer],
            timeout=Duration.seconds(30)
        )
        
        # User Lambda function
        get_code_lambda = _lambda.Function(
            self, "GetCodeFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("../backend"),
            handler="user.get_code.lambda_handler",
            environment=lambda_env,
            vpc=vpc,
            layers=[lambda_layer],
            timeout=Duration.seconds(30)
        )
        
        # Create API Gateway
        api = apigw.RestApi(
            self, "AccessCodeDispatcherApi",
            rest_api_name="Access Code Dispatcher API",
            description="API for access code dispatcher application",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS
            )
        )
        
        # Admin API endpoints
        admin = api.root.add_resource("admin")
        upload = admin.add_resource("upload")
        upload.add_method("POST", apigw.LambdaIntegration(upload_codes_lambda))
        
        list_resource = admin.add_resource("list")
        list_resource.add_method("GET", apigw.LambdaIntegration(list_codes_lambda))
        
        reset = admin.add_resource("reset")
        reset.add_method("POST", apigw.LambdaIntegration(reset_codes_lambda))
        
        # User API endpoints
        user = api.root.add_resource("user")
        code = user.add_resource("code")
        code.add_method("POST", apigw.LambdaIntegration(get_code_lambda))
        
        # Create S3 bucket for frontend
        website_bucket = s3.Bucket(
            self, "WebsiteBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        # Create CloudFront Origin Access Identity
        origin_access_identity = cloudfront.OriginAccessIdentity(
            self, "OriginAccessIdentity",
            comment="Allow CloudFront to access the website bucket"
        )
        
        # Grant read permissions to CloudFront
        website_bucket.grant_read(origin_access_identity)
        
        # Create CloudFront distribution
        distribution = cloudfront.Distribution(
            self, "WebsiteDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    website_bucket,
                    origin_access_identity=origin_access_identity
                ),
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html"
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html"
                )
            ]
        )
        
        # Deploy frontend files to S3
        s3deploy.BucketDeployment(
            self, "DeployWebsite",
            sources=[s3deploy.Source.asset("../frontend")],
            destination_bucket=website_bucket,
            distribution=distribution,
            distribution_paths=["/*"]
        )
        
        # Output the CloudFront URL and API Gateway URL
        CfnOutput(
            self, "CloudFrontURL",
            value=f"https://{distribution.distribution_domain_name}",
            description="URL for the CloudFront distribution"
        )
        
        CfnOutput(
            self, "APIGatewayURL",
            value=api.url,
            description="URL for the API Gateway"
        )


app = App()
AccessCodeDispatcherStack(app, "AccessCodeDispatcherStack", env=Environment(
    region="us-west-2"
))
app.synth()
