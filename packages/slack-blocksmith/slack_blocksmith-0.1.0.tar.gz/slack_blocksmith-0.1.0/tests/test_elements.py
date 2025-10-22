"""Tests for elements."""

import pytest

from slack_block_kit_builder.composition import (
    ConfirmationDialog,
    Option,
)
from slack_block_kit_builder.elements import (
    Button,
    ChannelsSelect,
    Checkboxes,
    ConversationsSelect,
    DatePicker,
    DatetimePicker,
    EmailInput,
    ExternalSelect,
    FileInput,
    Image,
    MultiChannelsSelect,
    MultiConversationsSelect,
    MultiExternalSelect,
    MultiStaticSelect,
    MultiUsersSelect,
    NumberInput,
    OverflowMenu,
    PlainTextInput,
    RadioButtons,
    RichTextInput,
    StaticSelect,
    TimePicker,
    URLInput,
    UsersSelect,
)


class TestButton:
    """Test Button element."""

    def test_create_basic(self):
        """Test creating basic button."""
        button = Button.create("Click me", "btn_1")
        assert button.type == "button"
        assert button.text.text == "Click me"
        assert button.action_id == "btn_1"
        assert button.url is None
        assert button.value is None
        assert button.style is None

    def test_create_with_properties(self):
        """Test creating button with properties."""
        button = Button.create(
            "Click me",
            "btn_1",
            url="https://example.com",
            value="value1",
            style="primary",
        )
        assert button.url == "https://example.com"
        assert button.value == "value1"
        assert button.style == "primary"

    def test_builder_pattern(self):
        """Test builder pattern for button."""
        button = (
            Button.create("Click me", "btn_1")
            .set_url("https://example.com")
            .set_value("value1")
            .set_style("danger")
        )
        assert button.url == "https://example.com"
        assert button.value == "value1"
        assert button.style == "danger"

    def test_build(self):
        """Test building button to dict."""
        button = Button.create(
            "Click me",
            "btn_1",
            url="https://example.com",
            value="value1",
            style="primary",
        )
        result = button.build()
        expected = {
            "type": "button",
            "text": {"type": "plain_text", "text": "Click me"},
            "action_id": "btn_1",
            "url": "https://example.com",
            "value": "value1",
            "style": "primary",
        }
        assert result == expected

    def test_action_id_validation(self):
        """Test action ID validation."""
        long_action_id = "x" * 256
        with pytest.raises(
            ValueError, match="Action ID length 256 exceeds maximum of 255"
        ):
            Button.create("Click me", long_action_id)


class TestCheckboxes:
    """Test Checkboxes element."""

    def test_create_basic(self):
        """Test creating basic checkboxes."""
        options = [
            Option.create("Option 1", "value1"),
            Option.create("Option 2", "value2"),
        ]
        checkboxes = Checkboxes.create("checkboxes_1", options)
        assert checkboxes.type == "checkboxes"
        assert checkboxes.action_id == "checkboxes_1"
        assert len(checkboxes.options) == 2

    def test_builder_pattern(self):
        """Test builder pattern for checkboxes."""
        options = [Option.create("Option 1", "value1")]
        checkboxes = Checkboxes.create("checkboxes_1", options)
        initial_options = [Option.create("Option 1", "value1")]
        checkboxes.set_initial_options(initial_options).set_focus_on_load(True)
        assert checkboxes.initial_options == initial_options
        assert checkboxes.focus_on_load is True

    def test_build(self):
        """Test building checkboxes to dict."""
        options = [
            Option.create("Option 1", "value1"),
            Option.create("Option 2", "value2"),
        ]
        checkboxes = Checkboxes.create("checkboxes_1", options)
        result = checkboxes.build()
        expected = {
            "type": "checkboxes",
            "action_id": "checkboxes_1",
            "options": [
                {"text": {"type": "plain_text", "text": "Option 1"}, "value": "value1"},
                {"text": {"type": "plain_text", "text": "Option 2"}, "value": "value2"},
            ],
        }
        assert result == expected

    def test_options_count_validation(self):
        """Test checkboxes options count validation."""
        options = [Option.create(f"Option {i}", f"value{i}") for i in range(101)]
        with pytest.raises(
            ValueError, match="Number of options 101 exceeds maximum of 100"
        ):
            Checkboxes.create("checkboxes_1", options)


class TestDatePicker:
    """Test DatePicker element."""

    def test_create_basic(self):
        """Test creating basic date picker."""
        picker = DatePicker.create("date_1")
        assert picker.type == "datepicker"
        assert picker.action_id == "date_1"
        assert picker.placeholder is None
        assert picker.initial_date is None

    def test_builder_pattern(self):
        """Test builder pattern for date picker."""
        picker = (
            DatePicker.create("date_1")
            .set_placeholder("Select date")
            .set_initial_date("2023-01-01")
            .set_focus_on_load(True)
        )
        assert picker.placeholder.text == "Select date"
        assert picker.initial_date == "2023-01-01"
        assert picker.focus_on_load is True

    def test_build(self):
        """Test building date picker to dict."""
        picker = (
            DatePicker.create("date_1")
            .set_placeholder("Select date")
            .set_initial_date("2023-01-01")
        )
        result = picker.build()
        expected = {
            "type": "datepicker",
            "action_id": "date_1",
            "placeholder": {"type": "plain_text", "text": "Select date"},
            "initial_date": "2023-01-01",
        }
        assert result == expected


class TestTimePicker:
    """Test TimePicker element."""

    def test_create_basic(self):
        """Test creating basic time picker."""
        picker = TimePicker.create("time_1")
        assert picker.type == "timepicker"
        assert picker.action_id == "time_1"

    def test_builder_pattern(self):
        """Test builder pattern for time picker."""
        picker = (
            TimePicker.create("time_1")
            .set_placeholder("Select time")
            .set_initial_time("12:00")
            .set_focus_on_load(True)
        )
        assert picker.placeholder.text == "Select time"
        assert picker.initial_time == "12:00"
        assert picker.focus_on_load is True

    def test_build(self):
        """Test building time picker to dict."""
        picker = (
            TimePicker.create("time_1")
            .set_placeholder("Select time")
            .set_initial_time("12:00")
        )
        result = picker.build()
        expected = {
            "type": "timepicker",
            "action_id": "time_1",
            "placeholder": {"type": "plain_text", "text": "Select time"},
            "initial_time": "12:00",
        }
        assert result == expected


class TestDatetimePicker:
    """Test DatetimePicker element."""

    def test_create_basic(self):
        """Test creating basic datetime picker."""
        picker = DatetimePicker.create("datetime_1")
        assert picker.type == "datetimepicker"
        assert picker.action_id == "datetime_1"

    def test_builder_pattern(self):
        """Test builder pattern for datetime picker."""
        picker = (
            DatetimePicker.create("datetime_1")
            .set_initial_date_time(1640995200)
            .set_focus_on_load(True)
        )
        assert picker.initial_date_time == 1640995200
        assert picker.focus_on_load is True

    def test_build(self):
        """Test building datetime picker to dict."""
        picker = DatetimePicker.create("datetime_1").set_initial_date_time(1640995200)
        result = picker.build()
        expected = {
            "type": "datetimepicker",
            "action_id": "datetime_1",
            "initial_date_time": 1640995200,
        }
        assert result == expected


class TestEmailInput:
    """Test EmailInput element."""

    def test_create_basic(self):
        """Test creating basic email input."""
        input_elem = EmailInput.create("email_1")
        assert input_elem.type == "email_text_input"
        assert input_elem.action_id == "email_1"

    def test_builder_pattern(self):
        """Test builder pattern for email input."""
        input_elem = (
            EmailInput.create("email_1")
            .set_placeholder("Enter email")
            .set_initial_value("test@example.com")
            .set_focus_on_load(True)
        )
        assert input_elem.placeholder.text == "Enter email"
        assert input_elem.initial_value == "test@example.com"
        assert input_elem.focus_on_load is True

    def test_build(self):
        """Test building email input to dict."""
        input_elem = (
            EmailInput.create("email_1")
            .set_placeholder("Enter email")
            .set_initial_value("test@example.com")
        )
        result = input_elem.build()
        expected = {
            "type": "email_text_input",
            "action_id": "email_1",
            "placeholder": {"type": "plain_text", "text": "Enter email"},
            "initial_value": "test@example.com",
        }
        assert result == expected


class TestNumberInput:
    """Test NumberInput element."""

    def test_create_basic(self):
        """Test creating basic number input."""
        input_elem = NumberInput.create("number_1")
        assert input_elem.type == "number_input"
        assert input_elem.action_id == "number_1"

    def test_builder_pattern(self):
        """Test builder pattern for number input."""
        input_elem = (
            NumberInput.create("number_1")
            .set_is_decimal_allowed(True)
            .set_initial_value("10")
            .set_min_value("0")
            .set_max_value("100")
            .set_focus_on_load(True)
        )
        assert input_elem.is_decimal_allowed is True
        assert input_elem.initial_value == "10"
        assert input_elem.min_value == "0"
        assert input_elem.max_value == "100"
        assert input_elem.focus_on_load is True

    def test_build(self):
        """Test building number input to dict."""
        input_elem = (
            NumberInput.create("number_1")
            .set_is_decimal_allowed(True)
            .set_initial_value("10")
        )
        result = input_elem.build()
        expected = {
            "type": "number_input",
            "action_id": "number_1",
            "is_decimal_allowed": True,
            "initial_value": "10",
        }
        assert result == expected


class TestPlainTextInput:
    """Test PlainTextInput element."""

    def test_create_basic(self):
        """Test creating basic plain text input."""
        input_elem = PlainTextInput.create("text_1")
        assert input_elem.type == "plain_text_input"
        assert input_elem.action_id == "text_1"

    def test_builder_pattern(self):
        """Test builder pattern for plain text input."""
        input_elem = (
            PlainTextInput.create("text_1")
            .set_placeholder("Enter text")
            .set_initial_value("Hello")
            .set_multiline(True)
            .set_min_length(1)
            .set_max_length(100)
            .set_focus_on_load(True)
        )
        assert input_elem.placeholder.text == "Enter text"
        assert input_elem.initial_value == "Hello"
        assert input_elem.multiline is True
        assert input_elem.min_length == 1
        assert input_elem.max_length == 100
        assert input_elem.focus_on_load is True

    def test_build(self):
        """Test building plain text input to dict."""
        input_elem = (
            PlainTextInput.create("text_1")
            .set_placeholder("Enter text")
            .set_multiline(True)
        )
        result = input_elem.build()
        expected = {
            "type": "plain_text_input",
            "action_id": "text_1",
            "placeholder": {"type": "plain_text", "text": "Enter text"},
            "multiline": True,
        }
        assert result == expected


class TestURLInput:
    """Test URLInput element."""

    def test_create_basic(self):
        """Test creating basic URL input."""
        input_elem = URLInput.create("url_1")
        assert input_elem.type == "url_text_input"
        assert input_elem.action_id == "url_1"

    def test_builder_pattern(self):
        """Test builder pattern for URL input."""
        input_elem = (
            URLInput.create("url_1")
            .set_placeholder("Enter URL")
            .set_initial_value("https://example.com")
            .set_focus_on_load(True)
        )
        assert input_elem.placeholder.text == "Enter URL"
        assert input_elem.initial_value == "https://example.com"
        assert input_elem.focus_on_load is True

    def test_build(self):
        """Test building URL input to dict."""
        input_elem = (
            URLInput.create("url_1")
            .set_placeholder("Enter URL")
            .set_initial_value("https://example.com")
        )
        result = input_elem.build()
        expected = {
            "type": "url_text_input",
            "action_id": "url_1",
            "placeholder": {"type": "plain_text", "text": "Enter URL"},
            "initial_value": "https://example.com",
        }
        assert result == expected


class TestRadioButtons:
    """Test RadioButtons element."""

    def test_create_basic(self):
        """Test creating basic radio buttons."""
        options = [
            Option.create("Option 1", "value1"),
            Option.create("Option 2", "value2"),
        ]
        radio = RadioButtons.create("radio_1", options)
        assert radio.type == "radio_buttons"
        assert radio.action_id == "radio_1"
        assert len(radio.options) == 2

    def test_builder_pattern(self):
        """Test builder pattern for radio buttons."""
        options = [Option.create("Option 1", "value1")]
        radio = RadioButtons.create("radio_1", options)
        initial_option = Option.create("Option 1", "value1")
        radio.set_initial_option(initial_option).set_focus_on_load(True)
        assert radio.initial_option == initial_option
        assert radio.focus_on_load is True

    def test_build(self):
        """Test building radio buttons to dict."""
        options = [
            Option.create("Option 1", "value1"),
            Option.create("Option 2", "value2"),
        ]
        radio = RadioButtons.create("radio_1", options)
        result = radio.build()
        expected = {
            "type": "radio_buttons",
            "action_id": "radio_1",
            "options": [
                {"text": {"type": "plain_text", "text": "Option 1"}, "value": "value1"},
                {"text": {"type": "plain_text", "text": "Option 2"}, "value": "value2"},
            ],
        }
        assert result == expected


class TestStaticSelect:
    """Test StaticSelect element."""

    def test_create_basic(self):
        """Test creating basic static select."""
        options = [
            Option.create("Option 1", "value1"),
            Option.create("Option 2", "value2"),
        ]
        select = StaticSelect.create("select_1", "Choose option", options)
        assert select.type == "static_select"
        assert select.action_id == "select_1"
        assert select.placeholder.text == "Choose option"
        assert len(select.options) == 2

    def test_builder_pattern(self):
        """Test builder pattern for static select."""
        options = [Option.create("Option 1", "value1")]
        select = StaticSelect.create("select_1", "Choose option", options)
        initial_option = Option.create("Option 1", "value1")
        select.set_initial_option(initial_option).set_focus_on_load(True)
        assert select.initial_option == initial_option
        assert select.focus_on_load is True

    def test_build(self):
        """Test building static select to dict."""
        options = [
            Option.create("Option 1", "value1"),
            Option.create("Option 2", "value2"),
        ]
        select = StaticSelect.create("select_1", "Choose option", options)
        result = select.build()
        expected = {
            "type": "static_select",
            "action_id": "select_1",
            "placeholder": {"type": "plain_text", "text": "Choose option"},
            "options": [
                {"text": {"type": "plain_text", "text": "Option 1"}, "value": "value1"},
                {"text": {"type": "plain_text", "text": "Option 2"}, "value": "value2"},
            ],
        }
        assert result == expected


class TestExternalSelect:
    """Test ExternalSelect element."""

    def test_create_basic(self):
        """Test creating basic external select."""
        select = ExternalSelect.create("select_1", "Choose option")
        assert select.type == "external_select"
        assert select.action_id == "select_1"
        assert select.placeholder.text == "Choose option"

    def test_builder_pattern(self):
        """Test builder pattern for external select."""
        select = ExternalSelect.create("select_1", "Choose option")
        initial_option = Option.create("Option 1", "value1")
        select.set_initial_option(initial_option).set_min_query_length(
            2
        ).set_focus_on_load(True)
        assert select.initial_option == initial_option
        assert select.min_query_length == 2
        assert select.focus_on_load is True

    def test_build(self):
        """Test building external select to dict."""
        select = ExternalSelect.create("select_1", "Choose option")
        result = select.build()
        expected = {
            "type": "external_select",
            "action_id": "select_1",
            "placeholder": {"type": "plain_text", "text": "Choose option"},
        }
        assert result == expected


class TestUsersSelect:
    """Test UsersSelect element."""

    def test_create_basic(self):
        """Test creating basic users select."""
        select = UsersSelect.create("users_1", "Choose user")
        assert select.type == "users_select"
        assert select.action_id == "users_1"
        assert select.placeholder.text == "Choose user"

    def test_builder_pattern(self):
        """Test builder pattern for users select."""
        select = UsersSelect.create("users_1", "Choose user")
        select.set_initial_user("U123456").set_focus_on_load(True)
        assert select.initial_user == "U123456"
        assert select.focus_on_load is True

    def test_build(self):
        """Test building users select to dict."""
        select = UsersSelect.create("users_1", "Choose user")
        result = select.build()
        expected = {
            "type": "users_select",
            "action_id": "users_1",
            "placeholder": {"type": "plain_text", "text": "Choose user"},
        }
        assert result == expected


class TestConversationsSelect:
    """Test ConversationsSelect element."""

    def test_create_basic(self):
        """Test creating basic conversations select."""
        select = ConversationsSelect.create("conversations_1", "Choose conversation")
        assert select.type == "conversations_select"
        assert select.action_id == "conversations_1"
        assert select.placeholder.text == "Choose conversation"

    def test_builder_pattern(self):
        """Test builder pattern for conversations select."""
        from slack_block_kit_builder.composition import Filter

        filter_obj = Filter.create(include=["public"])
        select = ConversationsSelect.create("conversations_1", "Choose conversation")
        select.set_initial_conversation("C123456").set_default_to_current_conversation(
            True
        ).set_filter(filter_obj).set_focus_on_load(True)
        assert select.initial_conversation == "C123456"
        assert select.default_to_current_conversation is True
        assert select.filter == filter_obj
        assert select.focus_on_load is True

    def test_build(self):
        """Test building conversations select to dict."""
        select = ConversationsSelect.create("conversations_1", "Choose conversation")
        result = select.build()
        expected = {
            "type": "conversations_select",
            "action_id": "conversations_1",
            "placeholder": {"type": "plain_text", "text": "Choose conversation"},
        }
        assert result == expected


class TestChannelsSelect:
    """Test ChannelsSelect element."""

    def test_create_basic(self):
        """Test creating basic channels select."""
        select = ChannelsSelect.create("channels_1", "Choose channel")
        assert select.type == "channels_select"
        assert select.action_id == "channels_1"
        assert select.placeholder.text == "Choose channel"

    def test_builder_pattern(self):
        """Test builder pattern for channels select."""
        select = ChannelsSelect.create("channels_1", "Choose channel")
        select.set_initial_channel("C123456").set_focus_on_load(True)
        assert select.initial_channel == "C123456"
        assert select.focus_on_load is True

    def test_build(self):
        """Test building channels select to dict."""
        select = ChannelsSelect.create("channels_1", "Choose channel")
        result = select.build()
        expected = {
            "type": "channels_select",
            "action_id": "channels_1",
            "placeholder": {"type": "plain_text", "text": "Choose channel"},
        }
        assert result == expected


class TestMultiStaticSelect:
    """Test MultiStaticSelect element."""

    def test_create_basic(self):
        """Test creating basic multi static select."""
        options = [
            Option.create("Option 1", "value1"),
            Option.create("Option 2", "value2"),
        ]
        select = MultiStaticSelect.create("multi_select_1", "Choose options", options)
        assert select.type == "multi_static_select"
        assert select.action_id == "multi_select_1"
        assert select.placeholder.text == "Choose options"
        assert len(select.options) == 2

    def test_builder_pattern(self):
        """Test builder pattern for multi static select."""
        options = [Option.create("Option 1", "value1")]
        select = MultiStaticSelect.create("multi_select_1", "Choose options", options)
        initial_options = [Option.create("Option 1", "value1")]
        select.set_initial_options(initial_options).set_max_selected_items(
            5
        ).set_focus_on_load(True)
        assert select.initial_options == initial_options
        assert select.max_selected_items == 5
        assert select.focus_on_load is True

    def test_build(self):
        """Test building multi static select to dict."""
        options = [
            Option.create("Option 1", "value1"),
            Option.create("Option 2", "value2"),
        ]
        select = MultiStaticSelect.create("multi_select_1", "Choose options", options)
        result = select.build()
        expected = {
            "type": "multi_static_select",
            "action_id": "multi_select_1",
            "placeholder": {"type": "plain_text", "text": "Choose options"},
            "options": [
                {"text": {"type": "plain_text", "text": "Option 1"}, "value": "value1"},
                {"text": {"type": "plain_text", "text": "Option 2"}, "value": "value2"},
            ],
        }
        assert result == expected


class TestMultiExternalSelect:
    """Test MultiExternalSelect element."""

    def test_create_basic(self):
        """Test creating basic multi external select."""
        select = MultiExternalSelect.create("multi_external_1", "Choose options")
        assert select.type == "multi_external_select"
        assert select.action_id == "multi_external_1"
        assert select.placeholder.text == "Choose options"

    def test_builder_pattern(self):
        """Test builder pattern for multi external select."""
        select = MultiExternalSelect.create("multi_external_1", "Choose options")
        initial_options = [Option.create("Option 1", "value1")]
        select.set_initial_options(initial_options).set_min_query_length(
            2
        ).set_max_selected_items(5).set_focus_on_load(True)
        assert select.initial_options == initial_options
        assert select.min_query_length == 2
        assert select.max_selected_items == 5
        assert select.focus_on_load is True

    def test_build(self):
        """Test building multi external select to dict."""
        select = MultiExternalSelect.create("multi_external_1", "Choose options")
        result = select.build()
        expected = {
            "type": "multi_external_select",
            "action_id": "multi_external_1",
            "placeholder": {"type": "plain_text", "text": "Choose options"},
        }
        assert result == expected


class TestMultiUsersSelect:
    """Test MultiUsersSelect element."""

    def test_create_basic(self):
        """Test creating basic multi users select."""
        select = MultiUsersSelect.create("multi_users_1", "Choose users")
        assert select.type == "multi_users_select"
        assert select.action_id == "multi_users_1"
        assert select.placeholder.text == "Choose users"

    def test_builder_pattern(self):
        """Test builder pattern for multi users select."""
        select = MultiUsersSelect.create("multi_users_1", "Choose users")
        select.set_initial_users(["U123456", "U789012"]).set_max_selected_items(
            5
        ).set_focus_on_load(True)
        assert select.initial_users == ["U123456", "U789012"]
        assert select.max_selected_items == 5
        assert select.focus_on_load is True

    def test_build(self):
        """Test building multi users select to dict."""
        select = MultiUsersSelect.create("multi_users_1", "Choose users")
        result = select.build()
        expected = {
            "type": "multi_users_select",
            "action_id": "multi_users_1",
            "placeholder": {"type": "plain_text", "text": "Choose users"},
        }
        assert result == expected


class TestMultiConversationsSelect:
    """Test MultiConversationsSelect element."""

    def test_create_basic(self):
        """Test creating basic multi conversations select."""
        select = MultiConversationsSelect.create(
            "multi_conversations_1", "Choose conversations"
        )
        assert select.type == "multi_conversations_select"
        assert select.action_id == "multi_conversations_1"
        assert select.placeholder.text == "Choose conversations"

    def test_builder_pattern(self):
        """Test builder pattern for multi conversations select."""
        from slack_block_kit_builder.composition import Filter

        filter_obj = Filter.create(include=["public"])
        select = MultiConversationsSelect.create(
            "multi_conversations_1", "Choose conversations"
        )
        select.set_initial_conversations(
            ["C123456", "C789012"]
        ).set_default_to_current_conversation(True).set_filter(
            filter_obj
        ).set_max_selected_items(5).set_focus_on_load(True)
        assert select.initial_conversations == ["C123456", "C789012"]
        assert select.default_to_current_conversation is True
        assert select.filter == filter_obj
        assert select.max_selected_items == 5
        assert select.focus_on_load is True

    def test_build(self):
        """Test building multi conversations select to dict."""
        select = MultiConversationsSelect.create(
            "multi_conversations_1", "Choose conversations"
        )
        result = select.build()
        expected = {
            "type": "multi_conversations_select",
            "action_id": "multi_conversations_1",
            "placeholder": {"type": "plain_text", "text": "Choose conversations"},
        }
        assert result == expected


class TestMultiChannelsSelect:
    """Test MultiChannelsSelect element."""

    def test_create_basic(self):
        """Test creating basic multi channels select."""
        select = MultiChannelsSelect.create("multi_channels_1", "Choose channels")
        assert select.type == "multi_channels_select"
        assert select.action_id == "multi_channels_1"
        assert select.placeholder.text == "Choose channels"

    def test_builder_pattern(self):
        """Test builder pattern for multi channels select."""
        select = MultiChannelsSelect.create("multi_channels_1", "Choose channels")
        select.set_initial_channels(["C123456", "C789012"]).set_max_selected_items(
            5
        ).set_focus_on_load(True)
        assert select.initial_channels == ["C123456", "C789012"]
        assert select.max_selected_items == 5
        assert select.focus_on_load is True

    def test_build(self):
        """Test building multi channels select to dict."""
        select = MultiChannelsSelect.create("multi_channels_1", "Choose channels")
        result = select.build()
        expected = {
            "type": "multi_channels_select",
            "action_id": "multi_channels_1",
            "placeholder": {"type": "plain_text", "text": "Choose channels"},
        }
        assert result == expected


class TestOverflowMenu:
    """Test OverflowMenu element."""

    def test_create_basic(self):
        """Test creating basic overflow menu."""
        options = [
            Option.create("Option 1", "value1"),
            Option.create("Option 2", "value2"),
        ]
        overflow = OverflowMenu.create("overflow_1", options)
        assert overflow.type == "overflow"
        assert overflow.action_id == "overflow_1"
        assert len(overflow.options) == 2

    def test_builder_pattern(self):
        """Test builder pattern for overflow menu."""
        options = [Option.create("Option 1", "value1")]
        overflow = OverflowMenu.create("overflow_1", options)
        overflow.set_confirm(
            ConfirmationDialog.create("Confirm", "Are you sure?", "Yes", "No")
        )
        assert overflow.confirm is not None

    def test_build(self):
        """Test building overflow menu to dict."""
        options = [
            Option.create("Option 1", "value1"),
            Option.create("Option 2", "value2"),
        ]
        overflow = OverflowMenu.create("overflow_1", options)
        result = overflow.build()
        expected = {
            "type": "overflow",
            "action_id": "overflow_1",
            "options": [
                {"text": {"type": "plain_text", "text": "Option 1"}, "value": "value1"},
                {"text": {"type": "plain_text", "text": "Option 2"}, "value": "value2"},
            ],
        }
        assert result == expected

    def test_options_count_validation(self):
        """Test overflow menu options count validation."""
        options = [Option.create(f"Option {i}", f"value{i}") for i in range(6)]
        with pytest.raises(
            ValueError, match="Number of options 6 exceeds maximum of 5"
        ):
            OverflowMenu.create("overflow_1", options)


class TestFileInput:
    """Test FileInput element."""

    def test_create_basic(self):
        """Test creating basic file input."""
        file_input = FileInput.create("file_1")
        assert file_input.type == "file_input"
        assert file_input.action_id == "file_1"
        assert file_input.filetypes is None
        assert file_input.max_files is None

    def test_builder_pattern(self):
        """Test builder pattern for file input."""
        file_input = (
            FileInput.create("file_1").set_filetypes(["pdf", "doc"]).set_max_files(3)
        )
        assert file_input.filetypes == ["pdf", "doc"]
        assert file_input.max_files == 3

    def test_build(self):
        """Test building file input to dict."""
        file_input = (
            FileInput.create("file_1").set_filetypes(["pdf", "doc"]).set_max_files(3)
        )
        result = file_input.build()
        expected = {
            "type": "file_input",
            "action_id": "file_1",
            "filetypes": ["pdf", "doc"],
            "max_files": 3,
        }
        assert result == expected


class TestRichTextInput:
    """Test RichTextInput element."""

    def test_create_basic(self):
        """Test creating basic rich text input."""
        input_elem = RichTextInput.create("rich_text_1")
        assert input_elem.type == "rich_text_input"
        assert input_elem.action_id == "rich_text_1"

    def test_builder_pattern(self):
        """Test builder pattern for rich text input."""
        input_elem = (
            RichTextInput.create("rich_text_1")
            .set_placeholder("Enter rich text")
            .set_initial_value("Hello")
            .set_focus_on_load(True)
        )
        assert input_elem.placeholder.text == "Enter rich text"
        assert input_elem.initial_value == "Hello"
        assert input_elem.focus_on_load is True

    def test_build(self):
        """Test building rich text input to dict."""
        input_elem = (
            RichTextInput.create("rich_text_1")
            .set_placeholder("Enter rich text")
            .set_initial_value("Hello")
        )
        result = input_elem.build()
        expected = {
            "type": "rich_text_input",
            "action_id": "rich_text_1",
            "placeholder": {"type": "plain_text", "text": "Enter rich text"},
            "initial_value": "Hello",
        }
        assert result == expected


class TestImage:
    """Test Image element."""

    def test_create_basic(self):
        """Test creating basic image."""
        image = Image.create("https://example.com/image.png", "Alt text")
        assert image.type == "image"
        assert image.image_url == "https://example.com/image.png"
        assert image.alt_text == "Alt text"

    def test_build(self):
        """Test building image to dict."""
        image = Image.create("https://example.com/image.png", "Alt text")
        result = image.build()
        expected = {
            "type": "image",
            "image_url": "https://example.com/image.png",
            "alt_text": "Alt text",
        }
        assert result == expected

    def test_image_url_validation(self):
        """Test image URL validation."""
        long_url = "https://example.com/" + "x" * 3000
        with pytest.raises(ValueError, match="URL length 3020 exceeds maximum of 3000"):
            Image.create(long_url, "Alt text")
