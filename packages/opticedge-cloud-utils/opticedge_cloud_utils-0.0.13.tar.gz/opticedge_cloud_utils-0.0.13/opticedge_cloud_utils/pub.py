from google.cloud import pubsub_v1

_publisher_client = None

def topic_path_for(publisher: pubsub_v1.PublisherClient, project: str, topic: str) -> str:
    if not project:
        raise RuntimeError("Project id not found")
    return publisher.topic_path(project, topic)

def get_publisher():
    global _publisher_client
    if _publisher_client is None:
        _publisher_client = pubsub_v1.PublisherClient()
    return _publisher_client
