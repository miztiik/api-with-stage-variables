from aws_cdk import aws_apigateway as _apigw
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_logs as _logs
from aws_cdk import core

import os


class GlobalArgs:
    """
    Helper to define global statics
    """

    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = "secure-api-with-keys"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_08_23"
    MIZTIIK_SUPPORT_EMAIL = ["mystique@example.com", ]


class ApiWithOutStageVariablesStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        stack_log_level: str,
        back_end_api_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create Serverless Event Processor using Lambda):
        # Read Lambda Code):
        try:
            with open("api_with_stage_variables/stacks/back_end/lambda_src/serverless_greeter.py", mode="r") as f:
                backend_greeter_fn_code = f.read()
        except OSError as e:
            print("Unable to read Lambda Function Code")
            raise e

        backend_greeter_fn = _lambda.Function(
            self,
            "backendGreeterFn",
            function_name=f"greeter_fn_{id}",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="index.lambda_handler",
            code=_lambda.InlineCode(backend_greeter_fn_code),
            timeout=core.Duration.seconds(15),
            reserved_concurrent_executions=20,
            environment={
                "LOG_LEVEL": f"{stack_log_level}",
                "Environment": "Production",
                "ANDON_CORD_PULLED": "False",
                "RANDOM_SLEEP_ENABLED": "False"
            },
            description="A simple greeter function, which responds with a timestamp"
        )
        backend_greeter_fn_version = backend_greeter_fn.latest_version
        backend_greeter_fn_version_alias = _lambda.Alias(
            self,
            "greeterFnAlias",
            alias_name="MystiqueAutomation",
            version=backend_greeter_fn_version
        )

        # Create Custom Loggroup
        # /aws/lambda/function-name
        backend_greeter_fn_lg = _logs.LogGroup(
            self,
            "greeterFnLoggroup",
            log_group_name=f"/aws/lambda/{backend_greeter_fn.function_name}",
            retention=_logs.RetentionDays.ONE_WEEK,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # Add API GW front end for the Lambda
        anti_pattern_api_stage_options = _apigw.StageOptions(
            stage_name="prod",
            throttling_rate_limit=10,
            throttling_burst_limit=100,
            logging_level=_apigw.MethodLoggingLevel.INFO
        )

        # Create API Gateway
        anti_pattern_api = _apigw.RestApi(
            self,
            "backEnd01Api",
            rest_api_name=f"{back_end_api_name}",
            deploy_options=anti_pattern_api_stage_options,
            endpoint_types=[
                _apigw.EndpointType.EDGE
            ],
            description=f"{GlobalArgs.OWNER}: API Best Practices. This stack deploys an API and integrates with Lambda $LATEST alias, which is the default"
        )

        anti_pattern_api_res = anti_pattern_api.root.add_resource(
            "anti-pattern-api")
        greeter = anti_pattern_api_res.add_resource("greeter")

        greeter_method_get = greeter.add_method(
            http_method="GET",
            request_parameters={
                "method.request.header.InvocationType": True,
                "method.request.path.skon": True
            },
            integration=_apigw.LambdaIntegration(
                handler=backend_greeter_fn,
                proxy=True
            )
        )

        # Outputs
        output_0 = core.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page."
        )

        output_1 = core.CfnOutput(
            self,
            "AntiPatternApiUrl",
            value=f"{greeter.url}",
            description="Use a browser to access this url."
        )
