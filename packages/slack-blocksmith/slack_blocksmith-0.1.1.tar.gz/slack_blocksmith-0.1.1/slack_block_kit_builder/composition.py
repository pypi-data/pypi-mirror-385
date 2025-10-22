"""Composition objects for Slack Block Kit."""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator

from .validators import (
    SlackConstraints,
    validate_text_length,
    validate_url,
)


class TextObject(BaseModel):
    """Base class for text objects."""

    type: str
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate text length."""
        return validate_text_length(v)


class PlainText(TextObject):
    """Plain text object."""

    type: Literal["plain_text"] = "plain_text"
    emoji: Optional[bool] = Field(None)

    def build(self) -> Dict[str, Any]:
        """Build the text object as a dictionary."""
        result = {"type": self.type, "text": self.text}
        if self.emoji is not None:
            result["emoji"] = self.emoji  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, text: str, emoji: Optional[bool] = None) -> "PlainText":
        """Create a plain text object with builder pattern."""
        return cls(text=text, emoji=emoji)

    def set_emoji(self, emoji: bool) -> "PlainText":
        """Set emoji property and return self for chaining."""
        self.emoji = emoji
        return self


class MrkdwnText(TextObject):
    """Markdown text object."""

    type: Literal["mrkdwn"] = "mrkdwn"
    verbatim: Optional[bool] = None

    def build(self) -> Dict[str, Any]:
        """Build the text object as a dictionary."""
        result = {"type": self.type, "text": self.text}
        if self.verbatim is not None:
            result["verbatim"] = self.verbatim  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, text: str, verbatim: Optional[bool] = None) -> "MrkdwnText":
        """Create a markdown text object with builder pattern."""
        return cls(text=text, verbatim=verbatim)

    def set_verbatim(self, verbatim: bool) -> "MrkdwnText":
        """Set verbatim property and return self for chaining."""
        self.verbatim = verbatim
        return self


class ConfirmationDialog(BaseModel):
    """Confirmation dialog object."""

    title: PlainText
    text: Union[PlainText, MrkdwnText]
    confirm: PlainText
    deny: PlainText
    style: Optional[Literal["primary", "danger"]] = None

    def build(self) -> Dict[str, Any]:
        """Build the confirmation dialog as a dictionary."""
        result = {
            "title": self.title.build(),
            "text": self.text.build(),
            "confirm": self.confirm.build(),
            "deny": self.deny.build(),
        }
        if self.style is not None:
            result["style"] = self.style  # type: ignore[assignment]
        return result

    @classmethod
    def create(
        cls,
        title: str,
        text: str,
        confirm: str,
        deny: str,
        style: Optional[Literal["primary", "danger"]] = None,
    ) -> "ConfirmationDialog":
        """Create a confirmation dialog with builder pattern."""
        return cls(
            title=PlainText.create(title),
            text=MrkdwnText.create(text),
            confirm=PlainText.create(confirm),
            deny=PlainText.create(deny),
            style=style,
        )

    def set_style(self, style: Literal["primary", "danger"]) -> "ConfirmationDialog":
        """Set style property and return self for chaining."""
        self.style = style
        return self


class Option(BaseModel):
    """Option object for select menus."""

    text: Union[PlainText, MrkdwnText]
    value: str
    description: Optional[Union[PlainText, MrkdwnText]] = None
    url: Optional[str] = None

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: str) -> str:
        """Validate option value length."""
        if len(v) > SlackConstraints.MAX_OPTION_VALUE_LENGTH:
            raise ValueError(
                f"Option value length {len(v)} exceeds maximum of {SlackConstraints.MAX_OPTION_VALUE_LENGTH}"
            )
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL length."""
        if v is not None:
            return validate_url(v)
        return v

    def build(self) -> Dict[str, Any]:
        """Build the option as a dictionary."""
        result = {
            "text": self.text.build(),
            "value": self.value,
        }
        if self.description is not None:
            result["description"] = self.description.build()
        if self.url is not None:
            result["url"] = self.url
        return result

    @classmethod
    def create(
        cls,
        text: str,
        value: str,
        description: Optional[str] = None,
        url: Optional[str] = None,
    ) -> "Option":
        """Create an option with builder pattern."""
        return cls(
            text=PlainText.create(text),
            value=value,
            description=PlainText.create(description) if description else None,
            url=url,
        )

    def set_description(self, description: str) -> "Option":
        """Set description and return self for chaining."""
        self.description = PlainText.create(description)
        return self

    def set_url(self, url: str) -> "Option":
        """Set URL and return self for chaining."""
        self.url = url
        return self


class OptionGroup(BaseModel):
    """Option group for select menus."""

    label: Union[PlainText, MrkdwnText]
    options: List[Option]

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: List[Option]) -> List[Option]:
        """Validate number of options."""
        if len(v) > SlackConstraints.MAX_OPTIONS_PER_SELECT:
            raise ValueError(
                f"Number of options {len(v)} exceeds maximum of {SlackConstraints.MAX_OPTIONS_PER_SELECT}"
            )
        return v

    def build(self) -> Dict[str, Any]:
        """Build the option group as a dictionary."""
        return {
            "label": self.label.build(),
            "options": [option.build() for option in self.options],
        }

    @classmethod
    def create(cls, label: str, options: List[Option]) -> "OptionGroup":
        """Create an option group with builder pattern."""
        return cls(label=PlainText.create(label), options=options)

    def add_option(self, option: Option) -> "OptionGroup":
        """Add an option to the group and return self for chaining."""
        self.options.append(option)
        return self


class DispatchActionConfiguration(BaseModel):
    """Dispatch action configuration."""

    trigger_actions_on: List[Literal["on_enter_pressed", "on_character_entered"]]

    def build(self) -> Dict[str, Any]:
        """Build the dispatch action configuration as a dictionary."""
        return {"trigger_actions_on": self.trigger_actions_on}

    @classmethod
    def create(
        cls,
        trigger_actions_on: List[Literal["on_enter_pressed", "on_character_entered"]],
    ) -> "DispatchActionConfiguration":
        """Create a dispatch action configuration with builder pattern."""
        return cls(trigger_actions_on=trigger_actions_on)


class Filter(BaseModel):
    """Filter for conversations and channels."""

    include: Optional[List[Literal["im", "mpim", "private", "public"]]] = None
    exclude_external_shared_channels: Optional[bool] = None
    exclude_bot_users: Optional[bool] = None

    def build(self) -> Dict[str, Any]:
        """Build the filter as a dictionary."""
        result = {}
        if self.include is not None:
            result["include"] = self.include
        if self.exclude_external_shared_channels is not None:
            result["exclude_external_shared_channels"] = (
                self.exclude_external_shared_channels
            )  # type: ignore[assignment]
        if self.exclude_bot_users is not None:
            result["exclude_bot_users"] = self.exclude_bot_users  # type: ignore[assignment]
        return result

    @classmethod
    def create(
        cls,
        include: Optional[List[Literal["im", "mpim", "private", "public"]]] = None,
        exclude_external_shared_channels: Optional[bool] = None,
        exclude_bot_users: Optional[bool] = None,
    ) -> "Filter":
        """Create a filter with builder pattern."""
        return cls(
            include=include,
            exclude_external_shared_channels=exclude_external_shared_channels,
            exclude_bot_users=exclude_bot_users,
        )

    def set_include(
        self, include: List[Literal["im", "mpim", "private", "public"]]
    ) -> "Filter":
        """Set include property and return self for chaining."""
        self.include = include
        return self

    def set_exclude_external_shared_channels(self, exclude: bool) -> "Filter":
        """Set exclude_external_shared_channels property and return self for chaining."""
        self.exclude_external_shared_channels = exclude
        return self

    def set_exclude_bot_users(self, exclude: bool) -> "Filter":
        """Set exclude_bot_users property and return self for chaining."""
        self.exclude_bot_users = exclude
        return self


class ConversationFilter(Filter):
    """Conversation filter extending base filter."""

    def build(self) -> Dict[str, Any]:
        """Build the conversation filter as a dictionary."""
        return super().build()
