import json
from types import SimpleNamespace
from unittest.mock import patch

from pydantic import BaseModel

from app.services.anthropic_service import call_llm_structured


class DemoOut(BaseModel):
	foo: str
	bar: int


class _TextBlock:
	def __init__(self, text: str) -> None:
		self.type = "text"
		self.text = text


class _Resp:
	def __init__(self, content):
		self.content = content


def _fake_create(**kwargs):
	data = {"foo": "x", "bar": 3}
	return _Resp([_TextBlock(json.dumps(data))])


@patch("app.services.anthropic_service._get_client")
def test_structured_json_parsing(mock_get_client):
	client = SimpleNamespace(messages=SimpleNamespace(create=_fake_create))
	mock_get_client.return_value = client

	out = call_llm_structured("return json", DemoOut, model="haiku")
	assert out.foo == "x"
	assert out.bar == 3