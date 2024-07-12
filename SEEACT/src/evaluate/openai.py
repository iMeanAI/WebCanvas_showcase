import os
import sys
import openai
import asyncio
from functools import partial
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

openai_api_key = os.getenv("OPENAI_API_KEY")


openai.api_key = openai_api_key


class GPTGenerator:
    def __init__(self, model=None):
        self.model = model

    async def request(self, messages: list = None, max_tokens: int = 500, temperature: float = 0.7
                      ) -> (str, str):
        try:
            cpu_count = multiprocessing.cpu_count()
            with ThreadPoolExecutor(max_workers=cpu_count * 2) as pool:
                future_answer = pool.submit(
                    self.chat, messages, max_tokens, temperature)
                future_answer_result = await future_answer.result()
                # Get the first option
                choice = future_answer_result.choices[0]
                openai_response = list(future_answer_result.choices)[
                    0].to_dict()['message']['content']
                pool.shutdown()
                return openai_response, ""
        except openai.error.APIError as e:
            error_message = f"OpenAI API returned an API Error: {e}"
            return "", error_message
        except openai.error.APIConnectionError as e:
            # Handle connection error here
            return "", error_message
        except openai.error.RateLimitError as e:
            return "", error_message

    async def chat(self, messages, max_tokens=500, temperature=0.7):
        loop = asyncio.get_event_loop()
        data = {
            'model': self.model,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': messages,
            # 'stop': ["Observation:"]
        }
        if hasattr(self, 'response_format'):
            data['response_format'] = self.response_format

        func = partial(openai.ChatCompletion.create, **data)
        return await loop.run_in_executor(None, func)


class JSONModeMixin(GPTGenerator):
    """
    A mixin to add JSON mode support to GPTGenerator classes.
    """

    def __init__(self, model=None):
        super().__init__(model=model)  # Ensure initialization from base class
        # Set response format to JSON object
        self.response_format = {"type": "json_object"}

    @staticmethod
    def prepare_messages_for_json_mode(messages):
        # Ensure there's a system message instructing the model to generate JSON
        if not any("json" in message.get('content', '').lower() for message in messages):
            messages.insert(
                0, {"role": "system", "content": "You are a helpful assistant designed to output json."})
        return messages

    async def request(self, messages: list = None, max_tokens: int = 500, temperature: float = 0.7) -> (str, str):
        messages = self.prepare_messages_for_json_mode(
            messages)  # Prepare messages for JSON mode
        return await super().request(messages, max_tokens, temperature)


class GPTGenerator35(GPTGenerator):
    def __init__(self, model=None):
        super().__init__(model=model if model is not None else "gpt-3.5-turbo")


class GPTGenerator4(GPTGenerator):
    def __init__(self, model=None):
        super().__init__(model=model if model is not None else "gpt-4-turbo")
