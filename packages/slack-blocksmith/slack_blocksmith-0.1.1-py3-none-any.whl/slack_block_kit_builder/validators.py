"""Custom validation logic for Slack Block Kit constraints."""

from typing import Any, List, Optional


class SlackConstraints:
    """Slack Block Kit constraints and limits."""

    # Text limits
    MAX_TEXT_LENGTH = 3000
    MAX_PLAIN_TEXT_LENGTH = 3000
    MAX_MRKDWN_LENGTH = 3000

    # Block limits
    MAX_BLOCKS_PER_MESSAGE = 50
    MAX_BLOCKS_PER_MODAL = 100
    MAX_BLOCKS_PER_HOME_TAB = 100

    # Element limits
    MAX_ELEMENTS_PER_ACTIONS = 25
    MAX_ELEMENTS_PER_CONTEXT = 10
    MAX_OPTIONS_PER_SELECT = 100
    MAX_OPTIONS_PER_OVERFLOW = 5

    # Input limits
    MAX_INPUT_LABEL_LENGTH = 2000
    MAX_INPUT_HINT_LENGTH = 2000
    MAX_INPUT_PLACEHOLDER_LENGTH = 150

    # URL limits
    MAX_IMAGE_URL_LENGTH = 3000
    MAX_VIDEO_URL_LENGTH = 3000

    # Block ID limits
    MAX_BLOCK_ID_LENGTH = 255
    MAX_ACTION_ID_LENGTH = 255

    # Option limits
    MAX_OPTION_TEXT_LENGTH = 75
    MAX_OPTION_VALUE_LENGTH = 75
    MAX_OPTION_DESCRIPTION_LENGTH = 75


def validate_text_length(
    text: str, max_length: int = SlackConstraints.MAX_TEXT_LENGTH
) -> str:
    """Validate text length against Slack constraints."""
    if len(text) > max_length:
        raise ValueError(f"Text length {len(text)} exceeds maximum of {max_length}")
    return text


def validate_block_id(block_id: Optional[str]) -> Optional[str]:
    """Validate block ID length."""
    if block_id and len(block_id) > SlackConstraints.MAX_BLOCK_ID_LENGTH:
        raise ValueError(
            f"Block ID length {len(block_id)} exceeds maximum of {SlackConstraints.MAX_BLOCK_ID_LENGTH}"
        )
    return block_id


def validate_action_id(action_id: str) -> str:
    """Validate action ID length."""
    if len(action_id) > SlackConstraints.MAX_ACTION_ID_LENGTH:
        raise ValueError(
            f"Action ID length {len(action_id)} exceeds maximum of {SlackConstraints.MAX_ACTION_ID_LENGTH}"
        )
    return action_id


def validate_url(
    url: str, max_length: int = SlackConstraints.MAX_IMAGE_URL_LENGTH
) -> str:
    """Validate URL length."""
    if len(url) > max_length:
        raise ValueError(f"URL length {len(url)} exceeds maximum of {max_length}")
    return url


def validate_options_count(options: List[Any], max_count: int) -> List[Any]:
    """Validate number of options."""
    if len(options) > max_count:
        raise ValueError(
            f"Number of options {len(options)} exceeds maximum of {max_count}"
        )
    return options
