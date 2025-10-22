# tests/test_pubsub_client.py
import types
import pytest
from unittest.mock import MagicMock

# adjust this import if your module lives at a different path
import opticedge_cloud_utils.pub as pubsub_client


def test_topic_path_for_returns_expected():
    class FakePublisher:
        def topic_path(self, project: str, topic: str) -> str:
            return f"projects/{project}/topics/{topic}"

    pub = FakePublisher()
    path = pubsub_client.topic_path_for(pub, "my-project", "my-topic")
    assert path == "projects/my-project/topics/my-topic"


@pytest.mark.parametrize("bad_project", ("", None, 0))
def test_topic_path_for_raises_when_no_project(bad_project):
    # Fake publisher doesn't matter since function should raise before using it
    fake_pub = MagicMock()
    with pytest.raises(RuntimeError) as excinfo:
        pubsub_client.topic_path_for(fake_pub, bad_project, "topic-name")
    assert "Project id not found" in str(excinfo.value)


def test_get_publisher_initializes_singleton(monkeypatch):
    # ensure module-level client cache is cleared
    monkeypatch.setattr(pubsub_client, "_publisher_client", None, raising=False)

    # Replace the real PublisherClient with a dummy class so no network calls happen
    class DummyPublisher:
        instances = 0

        def __init__(self):
            DummyPublisher.instances += 1

    monkeypatch.setattr(pubsub_client.pubsub_v1, "PublisherClient", DummyPublisher)

    # Call twice: should only create one instance
    p1 = pubsub_client.get_publisher()
    p2 = pubsub_client.get_publisher()

    assert p1 is p2
    assert DummyPublisher.instances == 1
    # And the module-level _publisher_client should be set to that instance
    assert pubsub_client._publisher_client is p1


def test_get_publisher_returns_existing_and_does_not_recreate(monkeypatch):
    sentinel = object()
    # Put a sentinel in the module-level cache and ensure PublisherClient is NOT called
    monkeypatch.setattr(pubsub_client, "_publisher_client", sentinel, raising=False)

    # Make PublisherClient raise if called (should not be called)
    def fail_constructor(*args, **kwargs):
        raise RuntimeError("should not be called")

    monkeypatch.setattr(pubsub_client.pubsub_v1, "PublisherClient", fail_constructor)

    got = pubsub_client.get_publisher()
    assert got is sentinel
