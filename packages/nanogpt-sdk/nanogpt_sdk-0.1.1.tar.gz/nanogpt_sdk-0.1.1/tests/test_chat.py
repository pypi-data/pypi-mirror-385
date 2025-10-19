from nanogpt import Client, BearerAuth
from nanogpt.endpoints import chat

def test_create_completion(monkeypatch):
    class DummyResponse:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {
                'id': '0',
                'choices': [
                    {'message': {'content': 'Hello, NanoGPT!'}}
                ]
            }

    class DummyClient(Client):
        def request(self, *a, **kw):
            return DummyResponse()

    client = DummyClient(BearerAuth('AN_API_KEY'))
    result = chat.create_completion(
        client,
        model = 'gpt-nano-1',
        messages = [{'role': 'user', 'content': 'Hi'}]
    )
    assert result['choices'][0]['message']['content'] == 'Hello, NanoGPT!'
