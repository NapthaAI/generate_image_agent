#!/usr/bin/env python
import asyncio
import logging
from dotenv import load_dotenv
from naptha_sdk.schemas import AgentDeployment, AgentRunInput
from naptha_sdk.tool import Tool
from generate_image_agent.schemas import InputSchema, SystemPromptSchema

load_dotenv()

logger = logging.getLogger(__name__)

class GenerateImageAgent:

    def __init__(self, agent_deployment: AgentDeployment):
        self.agent_deployment = agent_deployment
        self.tool = Tool(tool_deployment=self.agent_deployment.tool_deployments[0])
        self.system_prompt = SystemPromptSchema(role=agent_deployment.agent_config.system_prompt["role"])

    async def call_tool(self, agent_run: AgentRunInput):

        tool_response = await self.tool.call_tool_func(agent_run)

        return tool_response

async def run(agent_run: AgentRunInput, *args, **kwargs):
    logger.info(f"Running with inputs {agent_run.inputs.tool_input_data}")

    generate_image_agent = GenerateImageAgent(agent_run.agent_deployment)

    return await generate_image_agent.call_tool(agent_run)


if __name__ == "__main__":
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.configs import load_agent_deployments, load_tool_deployments

    naptha = Naptha()

    # Configs
    agent_deployments = load_agent_deployments("generate_image_agent/configs/agent_deployments.json", load_persona_data=False, load_persona_schema=False)

    input_params = InputSchema(
        tool_name="generate_image_tool",
        tool_input_data="generate an image of a cat",
    )

    agent_run = AgentRunInput(
        inputs=input_params,
        agent_deployment=agent_deployments[0],
        consumer_id=naptha.user.id,
    )

    response = asyncio.run(run(agent_run))


