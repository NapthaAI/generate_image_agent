#!/usr/bin/env python
from dotenv import load_dotenv
from litellm import completion
from naptha_sdk.schemas import AgentDeployment
import os
from simple_chat_agent.schemas import InputSchema
from simple_chat_agent.utils import get_logger

load_dotenv()

logger = get_logger(__name__)

class SimpleChatAgent:

    def __init__(self, agent_deployment: AgentDeployment):
        self.agent_deployment = agent_deployment

    def chat(self, inputs: InputSchema):

        messages = [msg for msg in inputs.tool_input_data if msg["role"] != "system"]
        messages.insert(0, {"role": "system", "content": self.agent_deployment.agent_config.system_prompt.model_dump_json()})

        api_key = None if self.agent_deployment.agent_config.llm_config.client == "ollama" else ("EMPTY" if self.agent_deployment.agent_config.llm_config.client == "vllm" else os.getenv("OPENAI_API_KEY"))

        response = completion(
            model=self.agent_deployment.agent_config.llm_config.model,
            messages=messages,
            temperature=self.agent_deployment.agent_config.llm_config.temperature,
            max_tokens=self.agent_deployment.agent_config.llm_config.max_tokens,
            api_base=self.agent_deployment.agent_config.llm_config.api_base,
            api_key=api_key
        )

        response = response.choices[0].message.content
        logger.info(f"Response: {response}")

        messages.append({"role": "assistant", "content": response})

        return messages

def run(inputs: InputSchema, agent_deployment: AgentDeployment, *args, **kwargs):
    logger.info(f"Running with inputs {inputs.tool_input_data}")

    simple_chat_agent = SimpleChatAgent(agent_deployment)

    method = getattr(simple_chat_agent, inputs.tool_name, None)

    return method(inputs)


if __name__ == "__main__":
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.schemas import AgentRunInput
    from naptha_sdk.configs import load_agent_deployments

    naptha = Naptha()

    # Configs
    agent_deployments = load_agent_deployments("simple_chat_agent/configs/agent_deployments.json")


    input_params = InputSchema(
        tool_name="chat",
        tool_input_data=[{"role": "user", "content": "tell me a joke"}],
    )

    agent_run = AgentRunInput(
        inputs=input_params,
        agent_deployment=agent_deployments[0],
        consumer_id=naptha.user.id,
    )

    response = run(input_params, agent_deployments[0], naptha.user.id)


