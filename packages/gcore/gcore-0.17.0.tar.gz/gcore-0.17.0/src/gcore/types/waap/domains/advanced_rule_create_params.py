# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["AdvancedRuleCreateParams", "Action", "ActionBlock", "ActionTag"]


class AdvancedRuleCreateParams(TypedDict, total=False):
    action: Required[Action]
    """The action that the rule takes when triggered.

    Only one action can be set per rule.
    """

    enabled: Required[bool]
    """Whether or not the rule is enabled"""

    name: Required[str]
    """The name assigned to the rule"""

    source: Required[str]
    """A CEL syntax expression that contains the rule's conditions.

    Allowed objects are: request, whois, session, response, tags,
    `user_defined_tags`, `user_agent`, `client_data`.

    More info can be found here:
    https://gcore.com/docs/waap/waap-rules/advanced-rules
    """

    description: str
    """The description assigned to the rule"""

    phase: Optional[Literal["access", "header_filter", "body_filter"]]
    """The WAAP request/response phase for applying the rule. Default is "access".

    The "access" phase is responsible for modifying the request before it is sent to
    the origin server.

    The "`header_filter`" phase is responsible for modifying the HTTP headers of a
    response before they are sent back to the client.

    The "`body_filter`" phase is responsible for modifying the body of a response
    before it is sent back to the client.
    """


class ActionBlock(TypedDict, total=False):
    action_duration: str
    """How long a rule's block action will apply to subsequent requests.

    Can be specified in seconds or by using a numeral followed by 's', 'm', 'h', or
    'd' to represent time format (seconds, minutes, hours, or days). Empty time
    intervals are not allowed.
    """

    status_code: Literal[403, 405, 418, 429]
    """A custom HTTP status code that the WAAP returns if a rule blocks a request"""


class ActionTag(TypedDict, total=False):
    tags: Required[SequenceNotStr[str]]
    """The list of user defined tags to tag the request with"""


class Action(TypedDict, total=False):
    allow: object
    """The WAAP allowed the request"""

    block: ActionBlock
    """
    WAAP block action behavior could be configured with response status code and
    action duration.
    """

    captcha: object
    """The WAAP presented the user with a captcha"""

    handshake: object
    """The WAAP performed automatic browser validation"""

    monitor: object
    """The WAAP monitored the request but took no action"""

    tag: ActionTag
    """WAAP tag action gets a list of tags to tag the request scope with"""
