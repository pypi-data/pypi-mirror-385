import unittest
import pytest
import os
from pydantic import BaseModel
from defog.llm.utils import (
    chat_async,
    convert_tool_outputs_to_documents,
    get_original_user_question,
)
from defog.llm.llm_providers import LLMProvider
from defog.llm.providers.base import LLMResponse
from tests.conftest import skip_if_no_api_key


class TestToolCitations(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Skip tests if API keys are not available
        self.skip_openai = not os.getenv("OPENAI_API_KEY")
        self.skip_anthropic = not os.getenv("ANTHROPIC_API_KEY")

    def test_convert_tool_outputs_to_documents(self):
        """Test converting tool outputs to document format"""
        tool_outputs = [
            {
                "tool_call_id": "call_123",
                "name": "get_weather",
                "args": {"location": "San Francisco"},
                "result": {"temperature": 72, "condition": "sunny"},
            },
            {
                "tool_call_id": "call_456",
                "name": "get_time",
                "args": {"timezone": "PST"},
                "result": "2024-03-15 10:30:00 PST",
            },
        ]

        documents = convert_tool_outputs_to_documents(tool_outputs)

        self.assertEqual(len(documents), 2)
        self.assertEqual(documents[0]["document_name"], "get_weather_call_123")
        self.assertIn("get_weather", documents[0]["document_content"])
        self.assertIn("San Francisco", documents[0]["document_content"])
        self.assertIn("72", documents[0]["document_content"])

        self.assertEqual(documents[1]["document_name"], "get_time_call_456")
        self.assertIn("get_time", documents[1]["document_content"])
        self.assertIn("PST", documents[1]["document_content"])

    def test_get_original_user_question(self):
        """Test extracting original user question from messages"""
        # Test with simple string content
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "What's the weather like?"},
            {"role": "assistant", "content": "I'll check the weather for you."},
        ]

        question = get_original_user_question(messages)
        self.assertEqual(question, "What's the weather like?")

        # Test with multimodal content
        messages_multimodal = [
            {"role": "system", "content": "You are a helpful assistant"},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this image"},
                    {"type": "image", "source": {"type": "base64", "data": "..."}},
                ],
            },
        ]

        question = get_original_user_question(messages_multimodal)
        self.assertEqual(question, "Analyze this image")

        # Test with no user message
        messages_no_user = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "assistant", "content": "Hello!"},
        ]

        question = get_original_user_question(messages_no_user)
        self.assertEqual(question, "")

    @pytest.mark.asyncio
    @pytest.mark.xfail(
        reason="Error is raised before reaching citation check due to provider initialization"
    )
    async def test_unsupported_provider_error(self):
        """Test that unsupported providers raise an error when insert_tool_citations is True"""

        # Define a simple tool with pydantic input
        class CalculateInput(BaseModel):
            x: int
            y: int

        def calculate_sum(input: CalculateInput):
            """Add two numbers"""
            return input.x + input.y

        with self.assertRaises(ValueError) as context:
            await chat_async(
                provider=LLMProvider.GEMINI,
                model="gemini-2.5-flash",
                messages=[{"role": "user", "content": "Add 2 + 3"}],
                tools=[calculate_sum],
                insert_tool_citations=True,
            )

        self.assertIn("insert_tool_citations is only supported", str(context.exception))

    @pytest.mark.asyncio
    @skip_if_no_api_key("openai")
    async def test_tool_citations_with_openai(self):
        """Test tool citations with OpenAI provider"""

        # Define a tool with pydantic input
        class WeatherInput(BaseModel):
            location: str
            unit: str = "fahrenheit"

        def get_current_weather(input: WeatherInput):
            """Get the current weather in a given location"""
            # Return mock weather data
            if input.location.lower() == "san francisco":
                return {
                    "temperature": 72,
                    "unit": input.unit,
                    "condition": "sunny",
                    "humidity": 65,
                }
            else:
                return {
                    "temperature": 65,
                    "unit": input.unit,
                    "condition": "cloudy",
                    "humidity": 80,
                }

        messages = [
            {
                "role": "user",
                "content": "What's the weather like in San Francisco? Please include temperature and humidity.",
            }
        ]

        response = await chat_async(
            provider=LLMProvider.OPENAI,
            model="gpt-4.1",
            messages=messages,
            tools=[get_current_weather],
            tool_choice="auto",
            insert_tool_citations=True,
            temperature=0.1,
        )

        # Check that we got a response
        self.assertIsNotNone(response)
        self.assertIsInstance(response, LLMResponse)

        # If tools were called, check citations
        if response.tool_outputs:
            # Citations should be present
            self.assertIsNotNone(response.citations)
            self.assertIsInstance(response.citations, list)
            self.assertGreater(len(response.citations), 0)

            # Check citation structure
            for citation in response.citations:
                self.assertIn("type", citation)
                self.assertEqual(citation["type"], "text")
                self.assertIn("text", citation)
                self.assertIn("citations", citation)

            # Check that response content mentions weather info
            self.assertIn("72", response.content.lower())

    @pytest.mark.asyncio
    @skip_if_no_api_key("anthropic")
    async def test_tool_citations_with_anthropic(self):
        """Test tool citations with Anthropic provider"""

        # Define a tool with pydantic input
        class RectangleInput(BaseModel):
            length: float
            width: float

        def calculate_area(input: RectangleInput):
            """Calculate the area of a rectangle"""
            return {
                "area": input.length * input.width,
                "perimeter": 2 * (input.length + input.width),
            }

        messages = [
            {
                "role": "user",
                "content": "Calculate the area and perimeter of a rectangle with length 10 and width 5",
            }
        ]

        response = await chat_async(
            provider=LLMProvider.ANTHROPIC,
            model="claude-sonnet-4-20250514",
            messages=messages,
            tools=[calculate_area],
            tool_choice="auto",
            insert_tool_citations=True,
            temperature=0.1,
        )

        # Check that we got a response
        self.assertIsNotNone(response)
        self.assertIsInstance(response, LLMResponse)

        # If tools were called, check citations
        if response.tool_outputs:
            # Citations should be present
            self.assertIsNotNone(response.citations)
            self.assertIsInstance(response.citations, list)
            self.assertGreater(len(response.citations), 0)

            # Check that response content mentions the calculated area
            self.assertIn("50", response.content)

    @pytest.mark.asyncio
    @skip_if_no_api_key("openai")
    async def test_no_citations_without_flag(self):
        """Test that citations are not added when insert_tool_citations is False"""

        # Define a simple tool
        class AddInput(BaseModel):
            a: int
            b: int

        def add_numbers(input: AddInput):
            """Add two numbers together"""
            return input.a + input.b

        messages = [{"role": "user", "content": "What is 5 + 3?"}]

        response = await chat_async(
            provider=LLMProvider.OPENAI,
            model="gpt-4.1",
            messages=messages,
            tools=[add_numbers],
            tool_choice="auto",
            insert_tool_citations=False,  # Citations disabled
            temperature=0.1,
        )

        # Check that citations were not added
        self.assertIsNone(response.citations)

        # But tool outputs should still be present if tools were called
        if response.tool_outputs:
            self.assertGreater(len(response.tool_outputs), 0)

    @pytest.mark.asyncio
    @skip_if_no_api_key("openai")
    async def test_multiple_tool_calls_citations(self):
        """Test citations with multiple tool calls"""

        # Define multiple tools
        class MathInput(BaseModel):
            x: float
            y: float

        class StringInput(BaseModel):
            text: str

        def multiply(input: MathInput):
            """Multiply two numbers"""
            return input.x * input.y

        def reverse_string(input: StringInput):
            """Reverse a string"""
            return input.text[::-1]

        messages = [
            {
                "role": "user",
                "content": "What is 7 times 8? Also, reverse the string 'hello world'.",
            }
        ]

        response = await chat_async(
            provider=LLMProvider.OPENAI,
            model="gpt-4.1",
            messages=messages,
            tools=[multiply, reverse_string],
            tool_choice="auto",
            insert_tool_citations=True,
            temperature=0.1,
        )

        # Check response
        self.assertIsNotNone(response)

        # If multiple tools were called
        if response.tool_outputs and len(response.tool_outputs) > 1:
            # Check citations include references to both tools
            self.assertIsNotNone(response.citations)

            # Response should mention both results
            self.assertIn("56", response.content)
            self.assertIn("dlrow olleh", response.content)


if __name__ == "__main__":
    unittest.main()
