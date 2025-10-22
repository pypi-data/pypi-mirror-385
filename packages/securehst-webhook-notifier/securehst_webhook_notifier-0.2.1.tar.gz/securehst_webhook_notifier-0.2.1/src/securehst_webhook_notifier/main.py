import re
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any

import requests

try:
    from prefect import flow
    from prefect.states import StateType

    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False
    flow = None
    StateType = None


def notify_webhook(
    webhook_url: str,
    func_identifier: str,
    platform: str = "mattermost",
    user_id: str | None = None,
    custom_message: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator that sends start, end, and error notifications via a webhook.

    Args:
        webhook_url (str): The webhook URL to send notifications to.
        func_identifier (str): A string identifier representing the function being decorated.
        platform (str, optional): Messaging platform type: "mattermost", "slack",
        or "discord". Defaults to "mattermost".
        user_id (Optional[str], optional): User ID or username to mention on errors.
        Platform-specific formatting is applied. Defaults to None.
        custom_message (Optional[str], optional): Optional custom message to include.
        Defaults to None.

    Returns:
        Callable: A wrapped function with webhook notifications.

    """
    platform = platform.lower()

    if platform not in {"mattermost", "slack", "discord"}:
        raise ValueError(f"Unsupported platform '{platform}'. Supported platforms are: mattermost, slack, discord.")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = datetime.now()
            start_message = (
                f"⏳ Automation has started.\n"
                f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Function Caller: {func_identifier}"
            )
            send_webhook_message(webhook_url, start_message, platform)

            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                duration = end_time - start_time

                custom_message_str = f"\nReturn Message: {result}" if result else ""
                end_message = (
                    f"✅ Automation has completed successfully.\n"
                    f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Duration: {duration}\n"
                    f"Function Caller: {func_identifier}"
                    f"{custom_message_str}"
                )
                send_webhook_message(webhook_url, end_message, platform)
                return result

            except Exception as err:
                end_time = datetime.now()
                duration = end_time - start_time

                error_message = str(err)
                # Attempt to clean long SQL errors if detected
                if "SQL: " in error_message:
                    error_message = re.sub(r"\[SQL: .*?\]", "", error_message).strip()

                # User mention formatting per platform
                user_mention = ""
                if user_id:
                    if platform == "slack":
                        user_mention = f"<@{user_id}> "
                    elif platform in {"mattermost", "discord"}:
                        user_mention = f"@{user_id} "

                error_message_text = (
                    f"{user_mention}\n"
                    f"🆘 Automation has crashed.\n"
                    f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Duration: {duration}\n"
                    f"Function Caller: {func_identifier}\n"
                    f"Error: {error_message}"
                )
                send_webhook_message(webhook_url, error_message_text, platform)
                raise err

        return wrapper

    return decorator


def send_webhook_message(webhook_url: str, message: str, platform: str) -> None:
    """
    Sends a formatted message to the specified webhook URL.

    Args:
        webhook_url (str): The destination webhook URL.
        message (str): The message content to send.
        platform (str): Platform type to determine payload structure
        ("mattermost", "slack", "discord").

    Raises:
        ValueError: If the platform is unsupported.
        requests.RequestException: If the HTTP request fails.

    """
    platform = platform.lower()

    if platform == "discord":
        payload = {"content": message}
    elif platform in {"mattermost", "slack"}:
        payload = {"text": message}
    else:
        raise ValueError(f"Unsupported platform '{platform}' for webhook messaging.")

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to send webhook notification to {platform}: {e}")
        raise


def send_prefect_notification(webhook_url: str, message: str) -> None:
    """
    Send a notification to the webhook URL with error swallowing.

    Args:
        webhook_url (str): The destination webhook URL.
        message (str): The message content to send.

    """
    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        # Swallow errors to prevent affecting flow state
        print(f"Failed to send Prefect webhook notification: {e}")


def send_start_notification(webhook_url: str, display_name: str, start_message: str | None = None) -> None:
    """Send flow start notification."""
    message = start_message or f"🚀 {display_name} started"
    send_prefect_notification(webhook_url, message)


def create_state_hooks(
    webhook_url: str,
    display_name: str,
    user_id: str | None,
    silent_success: bool,
    success_message: str | None = None,
    failure_message: str | None = None,
) -> dict:
    """Create state change hooks for Prefect flow lifecycle notifications."""
    if not PREFECT_AVAILABLE:
        return {}

    def on_completion_hook(flow, flow_run, state):
        message = success_message or f"✅ {display_name} completed successfully"
        if not silent_success and user_id:
            message = f"@{user_id} {message}"
        send_prefect_notification(webhook_url, message)

    def on_failure_hook(flow, flow_run, state):
        # Determine failure type based on state
        failure_type = "failed"
        if state.type == StateType.CRASHED:
            failure_type = "crashed"
        elif state.type == StateType.CANCELLED:
            failure_type = "was cancelled"
        elif state.type == StateType.CANCELLING:
            failure_type = "is being cancelled"

        base_message = failure_message or f"❌ {display_name} {failure_type}"
        message = f"@{user_id} {base_message}" if user_id else base_message
        send_prefect_notification(webhook_url, message)

    return {
        "on_completion": [on_completion_hook],
        "on_failure": [on_failure_hook],
        "on_crashed": [on_failure_hook],
        "on_cancellation": [on_failure_hook],
    }


def prefect_notify_webhook(
    webhook_url: str,
    display_name: str,
    user_id: str | None = None,
    silent_success: bool = True,
    start_message: str | None = None,
    success_message: str | None = None,
    failure_message: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to add comprehensive Prefect flow notifications.

    This decorator should be applied BEFORE the @flow decorator to ensure proper
    integration with Prefect's state management system.

    Args:
        webhook_url (str): The webhook URL to send notifications to.
        display_name (str): Human readable name for the flow (e.g., "D. Miller & Associates - dmiller-etl").
        user_id (Optional[str], optional): User to mention on failures (e.g., "securehst"). Defaults to None.
        silent_success (bool, optional): If True, success notifications won't mention users. Defaults to True.
        start_message (Optional[str], optional): Custom start message. Defaults to "🚀 {display_name} started".
        success_message (Optional[str], optional): Custom success message.
            Defaults to "✅ {display_name} completed successfully".
        failure_message (Optional[str], optional): Custom failure message.
            Defaults to "❌ {display_name} {failure_type}".

    Returns:
        Callable: A wrapped function with Prefect webhook notifications.

    Raises:
        ImportError: If Prefect is not available.

    Example:
        @prefect_notify_webhook(
            webhook_url="https://mattermost.example.com/hooks/abc123",
            display_name="ETL Pipeline",
            user_id="admin"
        )
        @flow
        def my_etl_flow():
            pass

    """
    if not PREFECT_AVAILABLE:
        raise ImportError("Prefect is required to use prefect_notify_webhook. Install with: pip install prefect>=3.0.0")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Check if the function is already a Prefect flow
        if hasattr(func, "with_options"):
            # Function is already a flow, add hooks to it
            hooks = create_state_hooks(
                webhook_url, display_name, user_id, silent_success, success_message, failure_message
            )

            # Send start notification when flow starts
            original_fn = func.fn if hasattr(func, "fn") else func

            @wraps(original_fn)
            def wrapper_with_start_notification(*args: Any, **kwargs: Any) -> Any:
                send_start_notification(webhook_url, display_name, start_message)
                return original_fn(*args, **kwargs)

            # Update the flow with hooks and new function
            return func.with_options(fn=wrapper_with_start_notification, **hooks)
        else:
            # Function is not a flow yet, create a regular wrapper
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                send_start_notification(webhook_url, display_name, start_message)
                return func(*args, **kwargs)

            # Store webhook config for when this becomes a flow
            wrapper._webhook_config = {
                "webhook_url": webhook_url,
                "display_name": display_name,
                "user_id": user_id,
                "silent_success": silent_success,
                "success_message": success_message,
                "failure_message": failure_message,
            }

            return wrapper

    return decorator
