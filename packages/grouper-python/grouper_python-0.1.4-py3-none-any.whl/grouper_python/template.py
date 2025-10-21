"""grouper-python.template - functions to interact with template execution.

These are "helper" functions that most likely will not be called directly.
Instead, a GrouperClient class should be created, then from there use that
GrouperClient's methods to find and create objects, and use those objects' methods.
These helper functions are used by those objects, but can be called
directly if needed.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .objects.client import GrouperClient
    from .objects.subject import Subject


def execute_template(
    config_id: str,
    client: GrouperClient,
    owner_stem_name: str | None = None,
    owner_type: str = "stem",
    inputs: list[dict[str, str]] | None = None,
    ws_input: dict[str, Any] | None = None,
    act_as_subject: Subject | None = None,
) -> list[str]:
    """Execute a Grouper template with the given parameters.

    :param config_id: The template identifier/config ID to execute
    :type config_id: str
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param owner_stem_name: The stem name that owns the template, defaults to None
    :type owner_stem_name: str | None, optional
    :param owner_type: The type of owner object, defaults to "stem"
    :type owner_type: str, optional
    :param inputs: List of input parameters with name/value pairs, defaults to None
    :type inputs: list[dict[str, str]] | None, optional
    :param ws_input: Optional arbitrary input object, defaults to None
    :type ws_input: dict[str, Any] | None, optional
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :return: List of output lines from the template execution
    :rtype: list[str]
    """
    body = {
        "WsRestGshTemplateExecRequest": {
            "configId": config_id,
            "ownerType": owner_type,
        }
    }

    if owner_stem_name:
        body["WsRestGshTemplateExecRequest"]["ownerStemLookup"] = {
            "stemName": owner_stem_name
        }

    if inputs:
        body["WsRestGshTemplateExecRequest"]["inputs"] = inputs

    if ws_input:
        body["WsRestGshTemplateExecRequest"]["wsInput"] = ws_input

    r = client._call_grouper(
        "/gshTemplateExec",
        body,
        act_as_subject=act_as_subject,
    )

    if "gshOutputLines" in r["WsGshTemplateExecResults"]:
        return r["WsGshTemplateExecResults"]["gshOutputLines"]
    else:
        return []