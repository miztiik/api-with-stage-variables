#!/usr/bin/env python3

from aws_cdk import core

from api_with_stage_variables.api_with_stage_variables_stack import ApiWithStageVariablesStack


app = core.App()
ApiWithStageVariablesStack(app, "api-with-stage-variables")

app.synth()
