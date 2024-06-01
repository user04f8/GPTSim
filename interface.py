from simulated.agent_wrapper import AsyncAgentWrapper
    
class AsyncUserAgent(AsyncAgentWrapper):
    TYPE = 'User'
    async def get_response(self):
        response = await chat_completion_request(
            messages=self.message_history,
            tools=self.tools,
            model=GPT_MODEL)
        message = response.choices[0].message
        return message
