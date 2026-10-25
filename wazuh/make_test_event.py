#!/usr/bin/env python3
"""Print a synthetic Authentik event, wrapped the way Docker's json-file driver stores it, for wazuh-logtest.

Usage:
    python3 make_test_event.py login_failed user | /var/ossec/bin/wazuh-logtest
    python3 make_test_event.py model_created webauthndevice | /var/ossec/bin/wazuh-logtest

All values are fake (documentation IP range 192.0.2.0/24, user "logtest").
"""
import json
import sys


def event(action: str, model: str) -> str:
    inner = {
        "logger": "authentik.events.models",
        "event": "Created Event",
        "action": action,
        "context": {"model": {"app": "authentik_test", "model_name": model, "pk": 1, "name": "test"}},
        "client_ip": "192.0.2.1",
        "user": {"username": "logtest"},
    }
    return json.dumps({"log": json.dumps(inner) + "\n", "stream": "stderr", "time": "2026-01-01T00:00:00Z"})


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print(event(sys.argv[1], sys.argv[2]))
