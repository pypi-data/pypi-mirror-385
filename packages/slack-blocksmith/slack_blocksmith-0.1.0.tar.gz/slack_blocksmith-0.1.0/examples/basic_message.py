"""Basic message example using slack-block-kit-builder."""

from slack_block_kit_builder import Button, Message


def create_basic_message():
    """Create a basic Slack message with text and button."""
    message = (
        Message.create()
        .add_section("Hello World! 👋")
        .add_divider()
        .add_section(
            text="This is a *markdown* message with a button:",
            accessory=Button.create("Click Me!", "btn_click"),
        )
        .add_context(["Built with slack-block-kit-builder"])
    )

    return message.build()


def create_interactive_message():
    """Create an interactive message with multiple buttons."""
    message = (
        Message.create()
        .add_header("Interactive Message")
        .add_section("Choose an action:")
        .add_actions(
            [
                Button.create("Approve", "btn_approve").style("primary"),
                Button.create("Reject", "btn_reject").style("danger"),
                Button.create("More Info", "btn_info"),
            ]
        )
        .add_context(["Use the buttons above to interact with this message"])
    )

    return message.build()


def create_form_message():
    """Create a message with form elements."""
    from slack_block_kit_builder.elements import (
        Checkboxes,
        DatePicker,
        Option,
        PlainTextInput,
        StaticSelect,
    )

    message = (
        Message.create()
        .add_section("Please fill out this form:")
        .add_input(
            "Name", PlainTextInput.create("name_input").placeholder("Enter your name")
        )
        .add_input("Date", DatePicker.create("date_input").placeholder("Select date"))
        .add_input(
            "Priority",
            StaticSelect.create(
                "priority_select",
                "Choose priority",
                [
                    Option.create("High", "high"),
                    Option.create("Medium", "medium"),
                    Option.create("Low", "low"),
                ],
            ),
        )
        .add_input(
            "Skills",
            Checkboxes.create(
                "skills_checkboxes",
                [
                    Option.create("Python", "python"),
                    Option.create("JavaScript", "javascript"),
                    Option.create("Go", "go"),
                ],
            ),
        )
    )

    return message.build()


if __name__ == "__main__":
    print("=== Basic Message ===")
    print(create_basic_message())
    print("\n=== Interactive Message ===")
    print(create_interactive_message())
    print("\n=== Form Message ===")
    print(create_form_message())
