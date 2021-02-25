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
    REPO_NAME = "api-with-stage-variables"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_08_23"
    MIZTIIK_SUPPORT_EMAIL = ["mystique@example.com", ]


class ApiWithStageVariablesStack(core.Stack):

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
                greeter_fn_code = f.read()
        except OSError as e:
            print("Unable to read Lambda Function Code")
            raise e

        greeter_fn = _lambda.Function(
            self,
            "secureGreeterFn",
            function_name=f"greeter_fn_{id}",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="index.lambda_handler",
            code=_lambda.InlineCode(greeter_fn_code),
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
        greeter_fn_version = greeter_fn.latest_version
        greeter_fn_version_alias = _lambda.Alias(
            self,
            "greeterFnMystiqueAutomationAlias",
            alias_name="MystiqueAutomation",
            version=greeter_fn_version
        )

        greeter_fn_dev_alias = _lambda.Alias(
            self,
            "greeterFnDevAlias",
            alias_name="dev",
            version=greeter_fn_version
        )

        greeter_fn_test_alias = _lambda.Alias(
            self,
            "greeterFnTestAlias",
            alias_name="test",
            version=greeter_fn_version
        )

        greeter_fn_prod_alias = _lambda.Alias(
            self,
            "greeterFnProdAlias",
            alias_name="prod",
            version=greeter_fn_version
        )

        # Create Custom Loggroup
        # /aws/lambda/function-name
        greeter_fn_lg = _logs.LogGroup(
            self,
            "greeterFnLoggroup",
            log_group_name=f"/aws/lambda/{greeter_fn.function_name}",
            retention=_logs.RetentionDays.ONE_WEEK,
            removal_policy=core.RemovalPolicy.DESTROY
        )
# %%

        # Create API Gateway
        wa_api = _apigw.RestApi(
            self,
            "backEnd01Api",
            rest_api_name=f"{back_end_api_name}",
            # deploy_options=wa_api_dev_stage_options,
            retain_deployments=False,
            deploy=False,
            endpoint_types=[
                _apigw.EndpointType.EDGE
            ],
            description=f"{GlobalArgs.OWNER}: API Best Practices. Stage Variables for APIs. This stack deploys an API and integrates with Lambda using Stage Variables."
        )

        wa_api_logs = _logs.LogGroup(
            self,
            "waApiLogs",
            log_group_name=f"/aws/apigateway/{back_end_api_name}/access_logs",
            removal_policy=core.RemovalPolicy.DESTROY,
            retention=_logs.RetentionDays.ONE_DAY
        )

        ######################################
        ##    CONFIG FOR API STAGE : DEV    ##
        ######################################
        dev_wa_api_deploy = _apigw.Deployment(
            self,
            "devDeploy",
            api=wa_api,
            description=f"{GlobalArgs.OWNER}: Deployment of 'dev' Api Stage",
            retain_deployments=False
        )

        dev_api_stage = _apigw.Stage(
            self,
            "devStage",
            deployment=dev_wa_api_deploy,
            stage_name="miztiik-dev",
            throttling_rate_limit=10,
            throttling_burst_limit=100,
            # Log full requests/responses data
            data_trace_enabled=True,
            # Enable Detailed CloudWatch Metrics
            metrics_enabled=True,
            logging_level=_apigw.MethodLoggingLevel.INFO,
            access_log_destination=_apigw.LogGroupLogDestination(wa_api_logs),
            variables={
                "lambdaAlias": "dev"
            }
        )

        # wa_api.deployment_stage = dev_api_stage

        test_wa_api_deploy = _apigw.Deployment(
            self,
            "testDeploy",
            api=wa_api,
            description=f"{GlobalArgs.OWNER}: Deployment of 'test' Api Stage",
            retain_deployments=False
        )
        test_api_stage = _apigw.Stage(
            self,
            "testStage",
            deployment=test_wa_api_deploy,
            stage_name="miztiik-test",
            throttling_rate_limit=10,
            throttling_burst_limit=100,
            # Log full requests/responses data
            data_trace_enabled=True,
            # Enable Detailed CloudWatch Metrics
            metrics_enabled=True,
            logging_level=_apigw.MethodLoggingLevel.INFO,
            access_log_destination=_apigw.LogGroupLogDestination(wa_api_logs),
            variables={
                "lambdaAlias": "test"
            }
        )

        wa_api.deployment_stage = test_api_stage

        prod_wa_api_deploy = _apigw.Deployment(
            self,
            "prodDeploy",
            api=wa_api,
            description=f"{GlobalArgs.OWNER}: Deployment of 'prod' Api Stage",
            retain_deployments=False
        )
        prod_api_stage = _apigw.Stage(
            self,
            "prodStage",
            deployment=prod_wa_api_deploy,
            stage_name="miztiik-prod",
            throttling_rate_limit=10,
            throttling_burst_limit=100,
            # Log full requests/responses data
            data_trace_enabled=True,
            # Enable Detailed CloudWatch Metrics
            metrics_enabled=True,
            logging_level=_apigw.MethodLoggingLevel.INFO,
            access_log_destination=_apigw.LogGroupLogDestination(wa_api_logs),
            variables={
                "lambdaAlias": "prod"
            }
        )

        prod_api_stage.node.add_dependency(test_api_stage)

        wa_api.deployment_stage = prod_api_stage

        wa_api_res = wa_api.root.add_resource("wa-api")
        greeter = wa_api_res.add_resource("greeter")

        backend_stage_uri = (
            f"arn:aws:apigateway:"
            f"{core.Aws.REGION}"
            f":lambda:path/2015-03-31/functions/"
            f"{greeter_fn.function_arn}"
            f":"
            f"${{stageVariables.lambdaAlias}}"
            f"/invocations"
        )

        greeter_method_get = greeter.add_method(
            http_method="GET",
            request_parameters={
                "method.request.header.InvocationType": True,
                "method.request.path.mystique": True
            },
            # integration=_apigw.LambdaIntegration(
            #     # handler=greeter_fn,
            #     handler=backend_stage_uri,
            #     proxy=True
            # )
            integration=_apigw.Integration(
                type=_apigw.IntegrationType.AWS_PROXY,
                integration_http_method="GET",
                uri=backend_stage_uri
            )
        )

        # "arn:aws:apigateway:eu-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-2:614517326458:function:${stageVariables.preflightFunction}/invocations",
        # https://lambda.us-east-1.amazonaws.com/2015-03-31/functions/arn:aws:lambda:us-east-1:230023004178:function:greeter_fn_well-architected-api:${stageVariable.lambdaAlias}/invocations

        # We need to manually add permissions for the stages to invoke
        # CDK By default adds permission only for the last .deployment_stage
        #####################################################################
        ##  CDK BUG: CONDITIONS DOES NOT TAKE EFFECT IN SERVICE PRINCIPAL  ##
        #####################################################################
        """
        greeter_fn.grant_invoke(
            _iam.ServicePrincipal(
                service="apigateway.amazonaws.com",
                conditions={
                    "ArnLike": {"aws:SourceArn": "this-does-not-work"}
                }
            )
        )
        """

        map(
            lambda item: item.add_permission(
                f'{item.id}_perms',
                principal=_iam.ServicePrincipal("apigateway.amazonaws.com"),
                source_arn=greeter_method_get.method_arn.replace(
                    wa_api.deployment_stage.stage_name, '*'
                ),
                action="lambda:InvokeFunction"     
            ), 
            [greeter_fn, greeter_fn_dev_alias, greeter_fn_test_alias, greeter_fn_prod_alias]
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
            "WaApiUrl",
            value=f"{greeter.url}",
            description="Use an utility like curl from the same VPC as the API to invoke it."
        )
