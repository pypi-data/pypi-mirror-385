"""Tests for composition objects."""

import pytest

from slack_block_kit_builder.composition import (
    ConfirmationDialog,
    ConversationFilter,
    DispatchActionConfiguration,
    Filter,
    MrkdwnText,
    Option,
    OptionGroup,
    PlainText,
)


class TestPlainText:
    """Test PlainText composition object."""

    def test_create_basic(self):
        """Test creating basic plain text."""
        text = PlainText.create("Hello World")
        assert text.type == "plain_text"
        assert text.text == "Hello World"
        assert text.emoji is None

    def test_create_with_emoji(self):
        """Test creating plain text with emoji."""
        text = PlainText.create("Hello World", emoji=True)
        assert text.emoji is True

    def test_builder_pattern(self):
        """Test builder pattern for plain text."""
        text = PlainText.create("Hello").set_emoji(True)
        assert text.emoji is True

    def test_build(self):
        """Test building plain text to dict."""
        text = PlainText.create("Hello World", emoji=True)
        result = text.build()
        expected = {
            "type": "plain_text",
            "text": "Hello World",
            "emoji": True,
        }
        assert result == expected

    def test_text_length_validation(self):
        """Test text length validation."""
        long_text = "x" * 3001
        with pytest.raises(
            ValueError, match="Text length 3001 exceeds maximum of 3000"
        ):
            PlainText.create(long_text)


class TestMrkdwnText:
    """Test MrkdwnText composition object."""

    def test_create_basic(self):
        """Test creating basic markdown text."""
        text = MrkdwnText.create("Hello *World*")
        assert text.type == "mrkdwn"
        assert text.text == "Hello *World*"
        assert text.verbatim is None

    def test_create_with_verbatim(self):
        """Test creating markdown text with verbatim."""
        text = MrkdwnText.create("Hello *World*", verbatim=True)
        assert text.verbatim is True

    def test_builder_pattern(self):
        """Test builder pattern for markdown text."""
        text = MrkdwnText.create("Hello").set_verbatim(True)
        assert text.verbatim is True

    def test_build(self):
        """Test building markdown text to dict."""
        text = MrkdwnText.create("Hello *World*", verbatim=True)
        result = text.build()
        expected = {
            "type": "mrkdwn",
            "text": "Hello *World*",
            "verbatim": True,
        }
        assert result == expected


class TestConfirmationDialog:
    """Test ConfirmationDialog composition object."""

    def test_create_basic(self):
        """Test creating basic confirmation dialog."""
        dialog = ConfirmationDialog.create(
            title="Confirm",
            text="Are you sure?",
            confirm="Yes",
            deny="No",
        )
        assert dialog.title.text == "Confirm"
        assert dialog.text.text == "Are you sure?"
        assert dialog.confirm.text == "Yes"
        assert dialog.deny.text == "No"
        assert dialog.style is None

    def test_create_with_style(self):
        """Test creating confirmation dialog with style."""
        dialog = ConfirmationDialog.create(
            title="Delete",
            text="Are you sure?",
            confirm="Delete",
            deny="Cancel",
            style="danger",
        )
        assert dialog.style == "danger"

    def test_builder_pattern(self):
        """Test builder pattern for confirmation dialog."""
        dialog = ConfirmationDialog.create(
            title="Confirm",
            text="Are you sure?",
            confirm="Yes",
            deny="No",
        ).set_style("primary")
        assert dialog.style == "primary"

    def test_build(self):
        """Test building confirmation dialog to dict."""
        dialog = ConfirmationDialog.create(
            title="Delete",
            text="Are you sure?",
            confirm="Delete",
            deny="Cancel",
            style="danger",
        )
        result = dialog.build()
        expected = {
            "title": {"type": "plain_text", "text": "Delete"},
            "text": {"type": "mrkdwn", "text": "Are you sure?"},
            "confirm": {"type": "plain_text", "text": "Delete"},
            "deny": {"type": "plain_text", "text": "Cancel"},
            "style": "danger",
        }
        assert result == expected


class TestOption:
    """Test Option composition object."""

    def test_create_basic(self):
        """Test creating basic option."""
        option = Option.create("Option 1", "value1")
        assert option.text.text == "Option 1"
        assert option.value == "value1"
        assert option.description is None
        assert option.url is None

    def test_create_with_description(self):
        """Test creating option with description."""
        option = Option.create("Option 1", "value1", description="Description")
        assert option.description.text == "Description"

    def test_create_with_url(self):
        """Test creating option with URL."""
        option = Option.create("Option 1", "value1", url="https://example.com")
        assert option.url == "https://example.com"

    def test_builder_pattern(self):
        """Test builder pattern for option."""
        option = (
            Option.create("Option 1", "value1")
            .set_description("Description")
            .set_url("https://example.com")
        )
        assert option.description.text == "Description"
        assert option.url == "https://example.com"

    def test_build(self):
        """Test building option to dict."""
        option = Option.create(
            "Option 1", "value1", description="Description", url="https://example.com"
        )
        result = option.build()
        expected = {
            "text": {"type": "plain_text", "text": "Option 1"},
            "value": "value1",
            "description": {"type": "plain_text", "text": "Description"},
            "url": "https://example.com",
        }
        assert result == expected

    def test_value_length_validation(self):
        """Test option value length validation."""
        long_value = "x" * 76
        with pytest.raises(
            ValueError, match="Option value length 76 exceeds maximum of 75"
        ):
            Option.create("Option 1", long_value)


class TestOptionGroup:
    """Test OptionGroup composition object."""

    def test_create_basic(self):
        """Test creating basic option group."""
        options = [
            Option.create("Option 1", "value1"),
            Option.create("Option 2", "value2"),
        ]
        group = OptionGroup.create("Group 1", options)
        assert group.label.text == "Group 1"
        assert len(group.options) == 2

    def test_builder_pattern(self):
        """Test builder pattern for option group."""
        options = [Option.create("Option 1", "value1")]
        group = OptionGroup.create("Group 1", options)
        new_option = Option.create("Option 2", "value2")
        group.add_option(new_option)
        assert len(group.options) == 2

    def test_build(self):
        """Test building option group to dict."""
        options = [
            Option.create("Option 1", "value1"),
            Option.create("Option 2", "value2"),
        ]
        group = OptionGroup.create("Group 1", options)
        result = group.build()
        expected = {
            "label": {"type": "plain_text", "text": "Group 1"},
            "options": [
                {"text": {"type": "plain_text", "text": "Option 1"}, "value": "value1"},
                {"text": {"type": "plain_text", "text": "Option 2"}, "value": "value2"},
            ],
        }
        assert result == expected

    def test_options_count_validation(self):
        """Test option group options count validation."""
        options = [Option.create(f"Option {i}", f"value{i}") for i in range(101)]
        with pytest.raises(
            ValueError, match="Number of options 101 exceeds maximum of 100"
        ):
            OptionGroup.create("Group 1", options)


class TestDispatchActionConfiguration:
    """Test DispatchActionConfiguration composition object."""

    def test_create_basic(self):
        """Test creating basic dispatch action configuration."""
        config = DispatchActionConfiguration.create(["on_enter_pressed"])
        assert config.trigger_actions_on == ["on_enter_pressed"]

    def test_create_multiple_triggers(self):
        """Test creating dispatch action configuration with multiple triggers."""
        config = DispatchActionConfiguration.create(
            ["on_enter_pressed", "on_character_entered"]
        )
        assert config.trigger_actions_on == ["on_enter_pressed", "on_character_entered"]

    def test_build(self):
        """Test building dispatch action configuration to dict."""
        config = DispatchActionConfiguration.create(["on_enter_pressed"])
        result = config.build()
        expected = {"trigger_actions_on": ["on_enter_pressed"]}
        assert result == expected


class TestFilter:
    """Test Filter composition object."""

    def test_create_basic(self):
        """Test creating basic filter."""
        filter_obj = Filter.create()
        assert filter_obj.include is None
        assert filter_obj.exclude_external_shared_channels is None
        assert filter_obj.exclude_bot_users is None

    def test_create_with_include(self):
        """Test creating filter with include."""
        filter_obj = Filter.create(include=["public", "private"])
        assert filter_obj.include == ["public", "private"]

    def test_builder_pattern(self):
        """Test builder pattern for filter."""
        filter_obj = (
            Filter.create()
            .set_include(["public"])
            .set_exclude_external_shared_channels(True)
            .set_exclude_bot_users(True)
        )
        assert filter_obj.include == ["public"]
        assert filter_obj.exclude_external_shared_channels is True
        assert filter_obj.exclude_bot_users is True

    def test_build(self):
        """Test building filter to dict."""
        filter_obj = Filter.create(
            include=["public", "private"],
            exclude_external_shared_channels=True,
            exclude_bot_users=True,
        )
        result = filter_obj.build()
        expected = {
            "include": ["public", "private"],
            "exclude_external_shared_channels": True,
            "exclude_bot_users": True,
        }
        assert result == expected


class TestConversationFilter:
    """Test ConversationFilter composition object."""

    def test_inherits_from_filter(self):
        """Test that ConversationFilter inherits from Filter."""
        filter_obj = ConversationFilter.create(include=["public"])
        assert isinstance(filter_obj, Filter)
        assert filter_obj.include == ["public"]

    def test_build(self):
        """Test building conversation filter to dict."""
        filter_obj = ConversationFilter.create(include=["public"])
        result = filter_obj.build()
        expected = {"include": ["public"]}
        assert result == expected
