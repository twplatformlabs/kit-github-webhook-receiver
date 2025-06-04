"""
Webhook event handlers for GitHub events.

Define functions that respond to different GitHub webhook actions.
"""

from typing import Dict, Any


def on_push(payload: Dict[str, Any]):
    """
    Handle GitHub 'push' webhook events.

    This function can be customized to perform actions (e.g., CI triggers, logging, metrics)
    in response to push events sent by GitHub webhooks.

    :param payload: The JSON payload from the GitHub webhook.
    """
    print("Push event data:", payload)
