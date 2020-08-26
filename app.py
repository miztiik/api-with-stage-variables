#!/usr/bin/env python3

from aws_cdk import core

from api_with_stage_variables.stacks.back_end.api_without_stage_variable_stack import ApiWithOutStageVariablesStack
from api_with_stage_variables.stacks.back_end.api_with_stage_variables_stack import ApiWithStageVariablesStack

app = core.App()

api_without_stage_variable = ApiWithOutStageVariablesStack(
    app,
    "anti-pattern-api",
    stack_log_level="INFO",
    back_end_api_name="anti-pattern-api",
    description="Miztiik Automation: API Best Practice Demonstration. This stack deploys an API and integrates with Lambda $LATEST alias, which is the default"
)

api_with_stage_variable = ApiWithStageVariablesStack(
    app,
    "well-architected-api",
    stack_log_level="INFO",
    back_end_api_name="well-architected-api",
    description="Miztiik Automation: API Best Practice Demonstration. Stage Variables for APIs. This stack deploys an API and integrates with Lambda using Stage Variables Keys."
)

# Stack Level Tagging
core.Tag.add(app, key="Owner",
             value=app.node.try_get_context("owner"))
core.Tag.add(app, key="OwnerProfile",
             value=app.node.try_get_context("github_profile"))
core.Tag.add(app, key="Project",
             value=app.node.try_get_context("service_name"))
core.Tag.add(app, key="GithubRepo",
             value=app.node.try_get_context("github_repo_url"))
core.Tag.add(app, key="Udemy",
             value=app.node.try_get_context("udemy_profile"))
core.Tag.add(app, key="SkillShare",
             value=app.node.try_get_context("skill_profile"))
core.Tag.add(app, key="AboutMe",
             value=app.node.try_get_context("about_me"))


app.synth()
