from openai import AsyncOpenAI
# from tenacity import retry, wait_random_exponential, stop_after_attempt

from simulated.agent_wrapper import AsyncAgentWrapper, AgentMessage

GPT_MODEL = "gpt-3.5-turbo"
client = AsyncOpenAI()

# @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
async def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            n=1
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e
    
class AsyncGPTAgent(AsyncAgentWrapper):
    async def get_response(self):
        response = await chat_completion_request(
            messages=self.message_history,
            tools=self.tools,
            model=GPT_MODEL)
        message = response.choices[0].message
        return message
