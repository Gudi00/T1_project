import pytest
from unittest.mock import patch
from intent import detect_intent
from chain import create_chain
from app import app  # Для integration

# Mock models
class MockZeroShot:
    def __call__(self, *args, **kwargs):
        return {'labels': ['приветствие'], 'scores': [0.8]}

class MockKW:
    def extract_keywords(self, *args, **kwargs):
        return [('привет', 0.5)]

@pytest.fixture
def mock_models():
    return None, None, MockZeroShot(), MockKW()

def test_intent_greeting(mock_models):
    _, _, zero_shot, kw_model = mock_models
    intent, _ = detect_intent("Привет, хочу начать", "", zero_shot, kw_model)
    assert intent == "приветствие"

# Similar for other intents...

# Integration: 50 synthetic dialogs
def test_integration():
    examples = [
        {"query": "Привет, хочу начать", "expected": "приветствие"},
        # Add 49 more based on examples...
    ]
    for ex in examples:
        # Simulate chain run...
        pass

# Mock Telegram
@patch('telebot.TeleBot.send_message')
def test_telegram_notify(mock_send):
    # Simulate admin intent
    mock_send.assert_called()