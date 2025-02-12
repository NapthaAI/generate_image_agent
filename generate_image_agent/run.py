#!/usr/bin/env python
import asyncio
import logging
from dotenv import load_dotenv
import os
from typing import Dict
from naptha_sdk.schemas import AgentDeployment, AgentRunInput, ToolRunInput
from naptha_sdk.modules.tool import Tool
from naptha_sdk.user import sign_consumer_id
from generate_image_agent.schemas import InputSchema, SystemPromptSchema

load_dotenv()

logger = logging.getLogger(__name__)

class GenerateImageAgent:
    async def create(self, deployment: AgentDeployment, *args, **kwargs):
        self.deployment = deployment
        self.tool = Tool()
        tool_deployment = await self.tool.create(deployment=deployment.tool_deployments[0])
        self.system_prompt = SystemPromptSchema(role=self.deployment.config.system_prompt["role"])

    async def run(self, module_run: AgentRunInput, *args, **kwargs):
        tool_run_input = ToolRunInput(
            consumer_id=module_run.consumer_id,
            inputs=module_run.inputs,
            deployment=self.deployment.tool_deployments[0],
            signature=sign_consumer_id(module_run.consumer_id, os.getenv("PRIVATE_KEY"))
        )
        tool_response = await self.tool.run(tool_run_input)
        return tool_response.results

async def run(module_run: Dict, *args, **kwargs):
    module_run = AgentRunInput(**module_run)
    module_run.inputs = InputSchema(**module_run.inputs)
    generate_image_agent = GenerateImageAgent()
    await generate_image_agent.create(module_run.deployment)
    tool_response = await generate_image_agent.run(module_run)
    return tool_response


if __name__ == "__main__":
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.configs import setup_module_deployment

    naptha = Naptha()

    # Configs
    deployment = asyncio.run(setup_module_deployment("agent", "generate_image_agent/configs/deployment.json", node_url = os.getenv("NODE_URL"), user_id=naptha.user.id))

    input_params = {
        "tool_name": "generate_image_tool",
        "prompt": "generate an image of a cat",
    }

    module_run = {
        "inputs": input_params,
        "deployment": deployment,
        "consumer_id": naptha.user.id,
        "signature": sign_consumer_id(naptha.user.id, os.getenv("PRIVATE_KEY"))
    }

    response = asyncio.run(run(module_run))

    print("Response: ", response)