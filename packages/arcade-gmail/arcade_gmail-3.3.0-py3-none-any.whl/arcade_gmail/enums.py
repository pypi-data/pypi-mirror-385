from enum import Enum


class GmailReplyToWhom(str, Enum):
    EVERY_RECIPIENT = "every_recipient"
    ONLY_THE_SENDER = "only_the_sender"


class GmailAction(str, Enum):
    SEND = "send"
    DRAFT = "draft"


class GmailContentType(str, Enum):
    """The content type of the email body."""

    PLAIN = "plain"
    HTML = "html"
