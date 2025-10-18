import os
from unittest.mock import patch

import pytest

from .fixtures.http_server import *
from .fixtures.simple_app import *


class MockContext:
    class RequestContext:
        class LifespanContext:
            def __init__(self):
                self.session_id = "test-session"

        def __init__(self):
            self.lifespan_context = self.LifespanContext()

    def __init__(self):
        self.request_context = self.RequestContext()


@pytest.fixture
def mock_context():
    return MockContext()


@pytest.fixture
def simulation_env():
    import base64
    import json
    from veris_ai import veris

    # Set session_id to enable simulation mode using proper token format
    token_data = {"session_id": "test-session-123", "thread_id": "test-thread-123"}
    token = base64.b64encode(json.dumps(token_data).encode("utf-8")).decode("utf-8")
    veris.set_session_id(token)

    with patch.dict(
        os.environ,
        {
            "VERIS_ENDPOINT_URL": "http://test-endpoint",
        },
    ):
        yield
        # Clean up session_id after test
        veris.clear_session_id()


@pytest.fixture
def production_env():
    from veris_ai import veris

    # Clear session_id to ensure production mode (no simulation)
    veris.clear_session_id()

    with patch.dict(
        os.environ,
        {
            "VERIS_ENDPOINT_URL": "http://test-endpoint",
        },
    ):
        yield
