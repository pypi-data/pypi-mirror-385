"""Tests for message builders."""

import pytest

from slack_block_kit_builder.blocks import (
    Section,
)
from slack_block_kit_builder.elements import Button, PlainTextInput
from slack_block_kit_builder.message import HomeTab, Message, Modal


class TestMessage:
    """Test Message builder."""

    def test_create_basic(self):
        """Test creating basic message."""
        message = Message.create()
        assert message.blocks == []
        assert message.response_type is None
        assert message.replace_original is None
        assert message.delete_original is None
        assert message.metadata is None

    def test_add_section(self):
        """Test adding section to message."""
        message = Message.create().add_section("Hello World")
        assert len(message.blocks) == 1
        assert message.blocks[0].type == "section"
        assert message.blocks[0].text.text == "Hello World"

    def test_add_section_with_fields(self):
        """Test adding section with fields to message."""
        fields = ["Field 1", "Field 2"]
        message = Message.create().add_section(fields=fields)
        assert len(message.blocks) == 1
        assert message.blocks[0].type == "section"
        assert message.blocks[0].fields is not None
        assert len(message.blocks[0].fields) == 2

    def test_add_section_with_accessory(self):
        """Test adding section with accessory to message."""
        button = Button.create("Click me", "btn_1")
        message = Message.create().add_section(accessory=button)
        assert len(message.blocks) == 1
        assert message.blocks[0].type == "section"
        assert message.blocks[0].accessory == button

    def test_add_divider(self):
        """Test adding divider to message."""
        message = Message.create().add_divider()
        assert len(message.blocks) == 1
        assert message.blocks[0].type == "divider"

    def test_add_image(self):
        """Test adding image to message."""
        message = Message.create().add_image(
            "https://example.com/image.png", "Alt text"
        )
        assert len(message.blocks) == 1
        assert message.blocks[0].type == "image"
        assert message.blocks[0].image_url == "https://example.com/image.png"
        assert message.blocks[0].alt_text == "Alt text"

    def test_add_actions(self):
        """Test adding actions to message."""
        buttons = [
            Button.create("Button 1", "btn_1"),
            Button.create("Button 2", "btn_2"),
        ]
        message = Message.create().add_actions(buttons)
        assert len(message.blocks) == 1
        assert message.blocks[0].type == "actions"
        assert len(message.blocks[0].elements) == 2

    def test_add_context(self):
        """Test adding context to message."""
        elements = ["Context text", Button.create("Button", "btn_1")]
        message = Message.create().add_context(elements)
        assert len(message.blocks) == 1
        assert message.blocks[0].type == "context"
        assert len(message.blocks[0].elements) == 2

    def test_add_input(self):
        """Test adding input to message."""
        text_input = PlainTextInput.create("text_1")
        message = Message.create().add_input("Label", text_input)
        assert len(message.blocks) == 1
        assert message.blocks[0].type == "input"
        assert message.blocks[0].label.text == "Label"
        assert message.blocks[0].element == text_input

    def test_add_file(self):
        """Test adding file to message."""
        message = Message.create().add_file("external_123")
        assert len(message.blocks) == 1
        assert message.blocks[0].type == "file"
        assert message.blocks[0].external_id == "external_123"

    def test_add_header(self):
        """Test adding header to message."""
        message = Message.create().add_header("Header Text")
        assert len(message.blocks) == 1
        assert message.blocks[0].type == "header"
        assert message.blocks[0].text.text == "Header Text"

    def test_add_video(self):
        """Test adding video to message."""
        message = Message.create().add_video(
            "Video Title", "https://example.com/video.mp4"
        )
        assert len(message.blocks) == 1
        assert message.blocks[0].type == "video"
        assert message.blocks[0].title.text == "Video Title"
        assert message.blocks[0].video_url == "https://example.com/video.mp4"

    def test_add_rich_text(self):
        """Test adding rich text to message."""
        elements = [{"type": "text", "text": "Hello World"}]
        message = Message.create().add_rich_text(elements)
        assert len(message.blocks) == 1
        assert message.blocks[0].type == "rich_text"
        assert message.blocks[0].elements == elements

    def test_add_block(self):
        """Test adding custom block to message."""
        section = Section.create("Hello World")
        message = Message.create().add_block(section)
        assert len(message.blocks) == 1
        assert message.blocks[0] == section

    def test_builder_pattern(self):
        """Test builder pattern for message."""
        message = (
            Message.create()
            .add_section("Hello World")
            .add_divider()
            .add_actions([Button.create("Click me", "btn_1")])
            .set_response_type("in_channel")
            .set_replace_original(True)
            .set_delete_original(False)
            .set_metadata({"key": "value"})
        )
        assert len(message.blocks) == 3
        assert message.response_type == "in_channel"
        assert message.replace_original is True
        assert message.delete_original is False
        assert message.metadata == {"key": "value"}

    def test_build(self):
        """Test building message to dict."""
        message = (
            Message.create()
            .add_section("Hello World")
            .add_divider()
            .set_response_type("in_channel")
        )
        result = message.build()
        expected = {
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "plain_text", "text": "Hello World"},
                },
                {
                    "type": "divider",
                },
            ],
            "response_type": "in_channel",
        }
        assert result == expected

    def test_blocks_count_validation(self):
        """Test message blocks count validation."""
        message = Message.create()
        for i in range(51):  # Exceeds MAX_BLOCKS_PER_MESSAGE
            message.add_section(f"Section {i}")
        with pytest.raises(
            ValueError, match="Number of blocks 51 exceeds maximum of 50"
        ):
            message.build()


class TestModal:
    """Test Modal builder."""

    def test_create_basic(self):
        """Test creating basic modal."""
        modal = Modal.create("Modal Title")
        assert modal.type == "modal"
        assert modal.title == "Modal Title"
        assert modal.blocks == []
        assert modal.submit is None
        assert modal.close is None
        assert modal.private_metadata is None
        assert modal.callback_id is None
        assert modal.clear_on_close is None
        assert modal.notify_on_close is None
        assert modal.external_id is None

    def test_create_with_properties(self):
        """Test creating modal with properties."""
        modal = Modal.create(
            "Modal Title",
            submit="Submit",
            close="Close",
            private_metadata="metadata",
            callback_id="callback_123",
            clear_on_close=True,
            notify_on_close=True,
            external_id="external_123",
        )
        assert modal.submit == "Submit"
        assert modal.close == "Close"
        assert modal.private_metadata == "metadata"
        assert modal.callback_id == "callback_123"
        assert modal.clear_on_close is True
        assert modal.notify_on_close is True
        assert modal.external_id == "external_123"

    def test_add_section(self):
        """Test adding section to modal."""
        modal = Modal.create("Modal Title").add_section("Hello World")
        assert len(modal.blocks) == 1
        assert modal.blocks[0].type == "section"
        assert modal.blocks[0].text.text == "Hello World"

    def test_add_input(self):
        """Test adding input to modal."""
        text_input = PlainTextInput.create("text_1")
        modal = Modal.create("Modal Title").add_input("Label", text_input)
        assert len(modal.blocks) == 1
        assert modal.blocks[0].type == "input"
        assert modal.blocks[0].label.text == "Label"
        assert modal.blocks[0].element == text_input

    def test_builder_pattern(self):
        """Test builder pattern for modal."""
        modal = (
            Modal.create("Modal Title")
            .add_section("Hello World")
            .add_input("Label", PlainTextInput.create("text_1"))
            .set_submit("Submit")
            .set_close("Close")
            .set_private_metadata("metadata")
            .set_callback_id("callback_123")
            .set_clear_on_close(True)
            .set_notify_on_close(True)
            .set_external_id("external_123")
        )
        assert len(modal.blocks) == 2
        assert modal.submit == "Submit"
        assert modal.close == "Close"
        assert modal.private_metadata == "metadata"
        assert modal.callback_id == "callback_123"
        assert modal.clear_on_close is True
        assert modal.notify_on_close is True
        assert modal.external_id == "external_123"

    def test_build(self):
        """Test building modal to dict."""
        modal = (
            Modal.create("Modal Title")
            .add_section("Hello World")
            .set_submit("Submit")
            .set_close("Close")
        )
        result = modal.build()
        expected = {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Modal Title"},
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "plain_text", "text": "Hello World"},
                },
            ],
            "submit": {"type": "plain_text", "text": "Submit"},
            "close": {"type": "plain_text", "text": "Close"},
        }
        assert result == expected

    def test_blocks_count_validation(self):
        """Test modal blocks count validation."""
        modal = Modal.create("Modal Title")
        for i in range(101):  # Exceeds MAX_BLOCKS_PER_MODAL
            modal.add_section(f"Section {i}")
        with pytest.raises(
            ValueError, match="Number of blocks 101 exceeds maximum of 100"
        ):
            modal.build()


class TestHomeTab:
    """Test HomeTab builder."""

    def test_create_basic(self):
        """Test creating basic home tab."""
        home_tab = HomeTab.create()
        assert home_tab.type == "home"
        assert home_tab.blocks == []
        assert home_tab.private_metadata is None
        assert home_tab.callback_id is None
        assert home_tab.external_id is None

    def test_create_with_properties(self):
        """Test creating home tab with properties."""
        home_tab = HomeTab.create(
            private_metadata="metadata",
            callback_id="callback_123",
            external_id="external_123",
        )
        assert home_tab.private_metadata == "metadata"
        assert home_tab.callback_id == "callback_123"
        assert home_tab.external_id == "external_123"

    def test_add_section(self):
        """Test adding section to home tab."""
        home_tab = HomeTab.create().add_section("Hello World")
        assert len(home_tab.blocks) == 1
        assert home_tab.blocks[0].type == "section"
        assert home_tab.blocks[0].text.text == "Hello World"

    def test_add_actions(self):
        """Test adding actions to home tab."""
        buttons = [
            Button.create("Button 1", "btn_1"),
            Button.create("Button 2", "btn_2"),
        ]
        home_tab = HomeTab.create().add_actions(buttons)
        assert len(home_tab.blocks) == 1
        assert home_tab.blocks[0].type == "actions"
        assert len(home_tab.blocks[0].elements) == 2

    def test_builder_pattern(self):
        """Test builder pattern for home tab."""
        home_tab = (
            HomeTab.create()
            .add_section("Hello World")
            .add_actions([Button.create("Click me", "btn_1")])
            .set_private_metadata("metadata")
            .set_callback_id("callback_123")
            .set_external_id("external_123")
        )
        assert len(home_tab.blocks) == 2
        assert home_tab.private_metadata == "metadata"
        assert home_tab.callback_id == "callback_123"
        assert home_tab.external_id == "external_123"

    def test_build(self):
        """Test building home tab to dict."""
        home_tab = (
            HomeTab.create().add_section("Hello World").set_private_metadata("metadata")
        )
        result = home_tab.build()
        expected = {
            "type": "home",
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "plain_text", "text": "Hello World"},
                },
            ],
            "private_metadata": "metadata",
        }
        assert result == expected

    def test_blocks_count_validation(self):
        """Test home tab blocks count validation."""
        home_tab = HomeTab.create()
        for i in range(101):  # Exceeds MAX_BLOCKS_PER_HOME_TAB
            home_tab.add_section(f"Section {i}")
        with pytest.raises(
            ValueError, match="Number of blocks 101 exceeds maximum of 100"
        ):
            home_tab.build()
