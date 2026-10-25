import json

def get_next_topic(path="queue.json"):
    with open(path, "r", encoding="utf-8") as f:
        queue = json.load(f)
    topic = queue.pop(0)
    queue.append(topic)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)
    return topic
