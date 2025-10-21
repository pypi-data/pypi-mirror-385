"""A Mattermost integration Plugin"""

from collections.abc import Sequence
from typing import Any

import requests
from cmem_plugin_base.dataintegration.context import (
    ExecutionContext,
    ExecutionReport,
    PluginContext,
)
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import Entities, EntityPath, EntitySchema
from cmem_plugin_base.dataintegration.parameter.multiline import (
    MultilineStringParameterType,
)
from cmem_plugin_base.dataintegration.parameter.password import Password
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FixedSchemaPort
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType
from requests import Response

DEV_PAGE = "https://developers.mattermost.com"
BOTS_DOCU = f"{DEV_PAGE}/integrate/reference/bot-accounts/"
TOKEN_DOCU = f"{DEV_PAGE}/integrate/reference/personal-access-token/"


def header(access_token: Password) -> dict[str, str]:
    """Request Header"""
    return {
        "Authorization": f"Bearer {access_token.decrypt()}",
        "Content-Type": "application/json",
    }


def get_request_handler(url: str, url_extend: str, access_token: Password) -> Response:
    """Handle get requests"""
    return requests.get(
        f"{url}/api/v4/{url_extend}",
        headers=header(access_token),
        timeout=2,
    )


def get_dataset(
    url: str, url_expand: str, access_token: Password, query_terms: list[str]
) -> list[dict[str, str]]:
    """Create a list of usernames"""
    term = ""
    payload = {
        "term": term.join(query_terms),
    }
    response = requests.post(
        f"{url}/api/v4/{url_expand}/search",
        headers=header(access_token),
        json=payload,
        timeout=2,
    )
    return response.json()  # type: ignore[no-any-return]


class MattermostSearch(StringParameterType):
    """Mattermost Search Type"""

    def __init__(
        self,
        url_expand: str,
        display_name: str,
    ) -> None:
        self.url_expand = url_expand
        self.display_name = display_name

    autocompletion_depends_on_parameters: list[str] = ["url", "access_token"]  # noqa: RUF012

    # auto complete for values
    allow_only_autocompleted_values: bool = True
    # auto complete for labels
    autocomplete_value_with_labels: bool = True

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Get list of completions for query terms"""
        _ = context
        if not depend_on_parameter_values:
            raise ValueError("Input url and access token first.")
        result = []
        if len(query_terms) != 0:
            datasets = get_dataset(
                depend_on_parameter_values[0],
                self.url_expand,
                depend_on_parameter_values[1],
                query_terms,
            )

            result = [
                Autocompletion(
                    value=f"{object_name[self.display_name]}",
                    label=f"{object_name[self.display_name]}",
                )
                for object_name in datasets
            ]

            result.sort(key=lambda x: x.label)
            return result
        if len(query_terms) == 0:
            label = f"Enter a letter to get a list of {self.url_expand}."
            result.append(Autocompletion(value="", label=f"{label}"))
        result.sort(key=lambda x: x.label)
        return result


@Plugin(
    label="Send Mattermost messages",
    plugin_id="cmem_plugin_mattermost",
    icon=Icon(file_name="mattermost.svg", package=__package__),
    description="Send messages to Mattermost channels and/or users.",
    documentation=f"""This task sends messages to Mattermost channels and users.

You need a bot account in order to connect to Mattermost.
Learn more on bot accounts at
[developers.mattermost.com]({DEV_PAGE}):

- [Using bot accounts]({BOTS_DOCU})
- [Personal access tokens]({TOKEN_DOCU})

The task has two working modes.

# Single Message

You can send a single static message to a pre-configured channel or user.
Just configure the User and/or Channel and Message parameters to do so.

# Multiple Messages

You can send multiple messages to different channels or users by piping data into
the task. For each entity, a message is send. For dynamic messages the following
input paths are recognized:

- user
- channel
- message
""",
    parameters=[
        PluginParameter(
            name="url",
            label="URL",
            description="The base URL of your Mattermost deployment. "
            "Example: https://mattermost.example.org",
        ),
        PluginParameter(
            name="bot_name",
            label="Bot name",
            description="The name or display name of the bot you want to use to connect.",
        ),
        PluginParameter(
            name="access_token",
            label="Access Token",
            description="The Personal Access Token of the bot account.",
        ),
        PluginParameter(
            name="user",
            label="User",
            description="""The user account which will receive the message.

You can search for users if the connection was successful (Base URl, bot + token).""",
            param_type=MattermostSearch("users", "username"),
            default_value="",
        ),
        PluginParameter(
            name="channel",
            label="Channel",
            description="""The channel which will receive the message.

You can search for channels if the connection was successful (Base URl, bot + token).
If you want to send your message to multiple channels, separate them with a comma.""",
            param_type=MattermostSearch("channels", "name"),
            default_value="",
        ),
        PluginParameter(
            name="message",
            label="Message",
            description="The message size is limited to a configured maximum"
            " (e.g. 16383 characters).",
            param_type=MultilineStringParameterType(),
            default_value="",
        ),
    ],
)
class MattermostPlugin(WorkflowPlugin):
    """Send messages to Mattermost channels and users."""

    def __init__(  # noqa: PLR0913
        self,
        url: str,
        access_token: Password,
        bot_name: str,
        user: str,
        channel: str,
        message: str,
    ) -> None:
        self.url = url
        self.access_token = access_token
        self.bot_name = bot_name
        self.user = user
        self.channel = channel
        self.message = message

        self.schema = EntitySchema(
            type_uri="urn:x-mattermost:Message",
            paths=[
                EntityPath(path="user"),
                EntityPath(path="channel"),
                EntityPath(path="message"),
            ],
        )

        # Input and output ports
        self.input_ports = FixedNumberOfInputs([FixedSchemaPort(self.schema)])
        self.output_port = None

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> None:
        """Execute the workflow plugin on a given sequence of entities"""
        self.log.info("Mattermost plugin started.")
        # fix message with every start, could be used at creating of the workflow item
        if not self.user and not self.channel and not inputs:
            pass
        if self.user or self.channel:
            self.send_message()
        if inputs:
            entities_counter = 0
            channel_counter = 0
            channels: list = []
            users: list = []
            user_counter = 0
            # Entity/ies
            for item in inputs:
                column_names = [ep.path for ep in item.schema.paths]
                # columns of given Entity
                for entity in item.entities:
                    entities_counter += 1
                    self.user = ""
                    self.channel = ""
                    self.message = ""
                    i = 0
                    # row of given Entity
                    for _ in column_names:
                        param_value = entity.values[i][0] if len(entity.values[i]) > 0 else ""
                        if _ == "user" and param_value != "":
                            self.user = param_value
                            user_counter += 1
                            users.append(self.user)
                        elif _ == "channel" and param_value != "":
                            self.channel = param_value
                            channels.append(self.channel)
                            channel_counter += 1
                        elif _ == "message" and param_value != "":
                            self.message = param_value
                        i += 1  # noqa: SIM113
                    self.send_message()
            users = list(dict.fromkeys(users))
            channels = list(dict.fromkeys(channels))
            context.report.update(
                ExecutionReport(
                    entity_count=entities_counter,
                    operation="write",
                    operation_desc="entities received",
                    summary=[
                        ("No. of messages send:", f"{entities_counter}"),
                        ("No. of direct messages", f"{user_counter}"),
                        ("No. of channel messages", f"{channel_counter}"),
                        ("Channels that received a message", f"{', '.join(channels)}"),
                        ("Users who received a message", f"{', '.join(users)}"),
                    ],
                )
            )

    def post_request_handler(self, url_expand: str, payload: dict | list) -> Response:
        """Handle post requests"""
        return requests.post(
            f"{self.url}/api/v4/{url_expand}",
            headers=header(self.access_token),
            json=payload,
            timeout=2,
        )

    def get_id(self, obj_name: str) -> str:
        """Request to find the ID"""
        if obj_name:
            response = get_dataset(self.url, "users", self.access_token, [obj_name])
            for _ in response:
                if obj_name in (
                    _["username"],
                    _["nickname"],
                    _["email"],
                    f"{_['first_name']} {_['last_name']}",
                ):
                    return _["id"]  # type: ignore[no-any-return]
        raise ValueError(f"ID not found, check {obj_name} parameter.")

    def send_message_to_user(self) -> None:
        """Send messages from bot to one or more users."""
        # payload for json to generate a direct channel with post request
        data = [self.get_id(self.bot_name), self.get_id(self.user)]
        # post request to generate the direct channel
        response = self.post_request_handler("channels/direct", data)
        channel_id = response.json()["id"]
        # payload for the json to generate the message
        payload = {"channel_id": channel_id, "message": self.message}
        # post request to send the message
        self.post_request_handler("posts", payload)

    def get_channel_id(self) -> str:
        """Request to find the channel ID with the bot name"""
        if not self.channel:
            raise ValueError("No channel name was provided.")
        list_channel_data = get_dataset(self.url, "channels", self.access_token, [self.channel])
        for _ in list_channel_data:
            if self.channel in (_["name"], _["display_name"]):
                return _["id"]  # type: ignore[no-any-return]
        raise ValueError(f"Channel {self.channel} do not exist.")

    def send_message_to_channel(self) -> None:
        """Send messages from bot to channel."""
        # payload for the json to generate the message
        payload = {"channel_id": self.get_channel_id(), "message": self.message}
        # Post request for the message
        self.post_request_handler("posts", payload)

    def send_message(self) -> None:
        """Will test if the message is sending to user or channel or both"""
        if self.message:
            if self.user:
                self.send_message_to_user()
            if self.channel:
                self.send_message_to_channel()
        else:
            raise ValueError("No recipient.")
