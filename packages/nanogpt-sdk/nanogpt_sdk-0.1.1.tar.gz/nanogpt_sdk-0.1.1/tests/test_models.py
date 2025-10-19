from nanogpt import Client, BearerAuth
from nanogpt.endpoints import models

def test_list_all(monkeypatch):
    class DummyResponse:
        def __init__(self):
            self.status_code = 200
            
        def json(self):
            return {'models': [{'id': 'gpt-nano-1'}]}

    class DummyClient(Client):
        def request(self, *a, **kw):
            return DummyResponse()

    client = DummyClient(BearerAuth('AN_API_KEY'))
    result = models.list_all(client)
    assert 'models' in result