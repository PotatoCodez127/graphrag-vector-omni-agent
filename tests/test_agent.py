# tests/test_agent.py
import pytest
from unittest.mock import AsyncMock, patch
from core.agent import run_autonomous_agent


@pytest.mark.asyncio
async def test_agent_react_loop_flow():
    # Mocking the AsyncClient to prevent real network calls
    with patch("core.agent.client.chat", new_callable=AsyncMock) as mock_chat:
        # Simulate an agent response that requires no further tools
        mock_chat.return_value = {
            "message": {"content": "I have found the Rust documentation."}
        }

        result = await run_autonomous_agent("How do I write Rust?")
        assert result is not None
        mock_chat.assert_awaited()
