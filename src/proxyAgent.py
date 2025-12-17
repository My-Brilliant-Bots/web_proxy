from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import BaseChatMessage, TextMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool
from autogen_core.models import ModelInfo
from autogen_core import CancellationToken
import markdown
import asyncio
import os
from emailTool import send_email

# Analyse the passed in web traffic log file using LLM
async def web_traffic_analysis(model_client, traffic_log_file_content):

    system_prompt = """
    You are a proxy agent that can help with web traffic analysis. You are given the contents of a traffic log file and you need to analyze the traffic and provide a report. The report should be in markdown format. The report should be in the following sections: 1. Overview 2. List of all urls visited and the number of times they were visited. Respond with the report only, no other text or comments. Ignore requsts for images, icons or JS. Ignore any bacground tracking requests or ad requests that a website may make. Only consider core requests pertinent to what the user is actually typing in the browser
    """
    system_message = TextMessage(content=system_prompt, source="system")

    messages = []
    for i, chunk in enumerate(traffic_log_file_content):
        message_content = f"Here is chunk {i+1} of the traffic log file:\n{chunk}"
        messages.append(TextMessage(content=message_content, source="user"))

    all_agent_responses = []
    for idx, a_message in enumerate(messages):
      
        agent:AssistantAgent = AssistantAgent(name="proxy_agent",model_client=model_client)
        response: TextMessage = await agent.on_messages(messages=[system_message,a_message], cancellation_token=CancellationToken())
        all_agent_responses.append(response)

        await asyncio.sleep(70)
    return all_agent_responses

# Consolidate all agent responses using an LLM
async def create_consolidate_report(model_client, all_agent_responses):

    consolidate_report_prompt="""
    You are a smart agent responsible for merging multiple, markdown reports into a single consolidated
    report. Each individual markdown report, that you have to consolidate, contains an user's requests.These requests are captured using a proxy server. The consolidated report, should ignore requests to fetch javascript files, icons, images. It should ignore calls for health checks or requests that track an user. The report should provide a clear picture of the user's browsing behaviour but should not contain information of all networks calls to fetch images, javascript files etc. The report should be in html.Finally, nnce the consilidated report is generated, you should email the report using the email tool provided. The subject of the email should be something like : Internet Activity for $date with the $date being the date the report was generated. 
    """

    reports = []
    for i, chunk in enumerate(all_agent_responses):
        message_content = f"Here is report {i+1} of the traffic log file:\n{all_agent_responses[i]}"
        reports.append(TextMessage(content=message_content, source="user"))

    agent:AssistantAgent = AssistantAgent(
      name="consolidate_report_agent",
      model_client=model_client,
      system_message=consolidate_report_prompt,
      tools=[send_email],
      reflect_on_tool_use=True)

    
    response: TextMessage = await agent.on_messages(messages=reports, cancellation_token=CancellationToken())

    consolidate_report = markdown.markdown(response.chat_message.content)
    return consolidate_report

# Initialize AutoGen OpenAIChatCompletionClient and use it to analyse
# the passed in web traffic logs and consolidate the analysis into a single
# report , in markdown format
async def run_proxy_agent(traffic_log_file_content):
    model_client = OpenAIChatCompletionClient(
    model="gpt-4.1-nano",
    model_info=ModelInfo(vision=True, function_calling=True, json_output=True, family="unknown", structured_output=True),)

    all_agent_responses = await web_traffic_analysis(model_client, traffic_log_file_content)
    consolidated_report = await create_consolidate_report(model_client, all_agent_responses)
    return consolidated_report

    
        
        