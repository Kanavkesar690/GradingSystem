from flask import request, Response
import asyncio
import json
from collections import OrderedDict
from autogen_agentchat.base import TaskResult
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from AutomatedGradingFeedback.GetBlobUrls import get_blob_urls_for_folder
from AutomatedGradingFeedback.Agents import GetChunksAgent, EduEvaluator, CriticAgent


def Automated_Grading_Feedback(StudyFiles, AssignmentFiles):
    """ Runs a task and streams the conversation in real-time with dynamic agent tracking """
    StudyFiles, AssignmentFiles = get_blob_urls_for_folder(StudyFiles, AssignmentFiles)
   
    text_termination = TextMentionTermination("APPROVE")
 
    team = RoundRobinGroupChat(
        [GetChunksAgent, EduEvaluator, CriticAgent],
        termination_condition=text_termination
    )

    
    results = []
    class AsyncStream:
        def __init__(self, task):
            self.task = task

        async def generate_messages(self):
            async for message in team.run_stream(task=self.task):
                if isinstance(message, TaskResult):
                    final_message = f"Task Completed. Stop Reason: {message.stop_reason}"
                    final_message = final_message.encode('utf-8', errors='ignore').decode('utf-8')
                    yield f"Agent >> {final_message}\n\n"
                else:
                    current_agent = message.source

                    if isinstance(message.content, list):
                        output = " ".join(map(str, message.content))
                    elif isinstance(message.content, dict):
                        output = json.dumps(message.content, ensure_ascii=False)
                    else:
                        output = str(message.content)

                    output = output.encode('windows-1252', errors='ignore').decode('utf-8', errors='ignore')

                    msg = f"Agent >> {current_agent}: {output}"

                    if current_agent != "user":
                        yield f"{msg}\n\n"
            await team.reset()

        def __iter__(self):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                async_gen = self.generate_messages()
                while True:
                    try:
                        yield loop.run_until_complete(async_gen.__anext__())
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()   


    # def generate_stream(local_task):
    def generate_stream(StudyFiles, AssignmentFiles):
        local_task = f"StudyFiles: {StudyFiles}, AssignmentFiles: {AssignmentFiles}"
        results.clear()
        agent_outputs = OrderedDict()

        agent_names = [
            "EduEvaluator"
        ]
        
        thought_map = {
            "GetChunksAgent": "Break down the feedback into manageable chunks for analysis.",
            "EduEvaluator": "Evaluate the feedback based on predefined criteria and assign a grade.",
            "CriticAgent": "Review all outputs for accuracy, completeness, and consistency before finalizing the report."
        }

        printed_thoughts = set()
        step = True

        for thoughts in AsyncStream(local_task):
            if "Agent >>" in thoughts:
                try:
                    prefix = "Agent >> "
                    content_part = thoughts.split(prefix, 1)[1]
                    agent_name, raw_content = content_part.split(":", 1)
                    agent_name = agent_name.strip()
                    content = raw_content.strip()

                    if agent_name in thought_map and agent_name not in printed_thoughts:
                        if not step:
                            yield "\n\n\n"
                        yield f'**{agent_name}**: {thought_map[agent_name]}'
                        printed_thoughts.add(agent_name)

                    try:
                        parsed_content = json.loads(content)
                        agent_outputs[agent_name] = parsed_content
                    except json.JSONDecodeError:
                        agent_outputs[agent_name] = content

                    # Capture final response for Summary
                    cleaned_msg = thoughts.replace('\n', ' ').replace('\\n', ' ').replace('"', '\\"').strip()
                    if (
                        "APPROVE" not in cleaned_msg and
                        "Structured Data Collected" not in cleaned_msg and
                        "Getting Details" not in cleaned_msg and
                        "Action:" not in cleaned_msg
                    ):
                        final_response = cleaned_msg

                except Exception:
                    pass

            step = False

        yield '",\n'  

        # Output main agents' results
        json_output = {
            "AgentOutputs": {name: agent_outputs.get(name, None) for name in agent_names}
        }
        yield "\n\n"
        yield json.dumps(json_output, ensure_ascii=False, indent=2)

    return Response(generate_stream(StudyFiles, AssignmentFiles), content_type='text/event-stream')
