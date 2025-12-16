from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import BaseChatMessage, TextMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelInfo
from autogen_core import CancellationToken
import markdown

import os

async def run_proxy_agent(traffic_log_file_content):
    model_client = OpenAIChatCompletionClient(
    model="gpt-4.1",
    model_info=ModelInfo(vision=True, function_calling=True, json_output=True, family="unknown", structured_output=True),
)

    messages = []
    

    for i, chunk in enumerate(traffic_log_file_content):
        message_content = f"Here is chunk {i+1} of the traffic log file:\n{{chunk}}"
        messages.append(TextMessage(content=message_content, source="user"))

    # Final message to prompt for analysis after all chunks are sent
    final_prompt_message = TextMessage(
        content="All traffic log file chunks have been provided. Please analyze the complete traffic data and generate the report as previously instructed.",
        source="user"
    )
    messages.append(final_prompt_message)

    agent = AssistantAgent(
        name="proxy_agent",
        model_client=model_client,
        system_message="You are a proxy agent that can help with web traffic analysis. You are given the contents of a traffic log file and you need to analyze the traffic and provide a report. The report should be in markdown format. The report should be in the following sections: 1. Overview 2. List of all websites visited and the number of times they were visited. Respond with the report only, no other text or comments.",
    )

    response:TextMessage = await agent.on_messages(messages,cancellation_token=CancellationToken())
    agent_response = markdown.markdown(response.chat_message.content)
    print(agent_response)