# mypy: allow_untyped_defs
from __future__ import annotations
from grouper_python.template import execute_template
from . import data
import pytest
import respx
from httpx import Response


template_exec_result_success = {
    "WsGshTemplateExecResults": {
        "resultMetadata": {
            "resultCode": "SUCCESS",
            "resultMessage": "Template executed successfully",
        },
        "gshOutputLines": [
            "Template execution started",
            "Processing parameters...",
            "Operation completed successfully",
            "Results: 3 items processed"
        ],
        "responseMetadata": {
            "millis": "150",
            "serverVersion": "2.5.43",
        }
    }
}

template_exec_result_empty = {
    "WsGshTemplateExecResults": {
        "resultMetadata": {
            "resultCode": "SUCCESS",
            "resultMessage": "Template executed successfully",
        },
        "responseMetadata": {
            "millis": "50",
            "serverVersion": "2.5.43",
        }
    }
}


@respx.mock
def test_execute_template_basic(grouper_client):
    respx.post(url=data.URI_BASE + "/gshTemplateExec").mock(
        return_value=Response(200, json=template_exec_result_success)
    )

    result = execute_template("test_template", grouper_client)
    assert len(result) == 4
    assert result[0] == "Template execution started"
    assert result[3] == "Results: 3 items processed"


@respx.mock
def test_execute_template_with_owner_stem(grouper_client):
    respx.post(url=data.URI_BASE + "/gshTemplateExec").mock(
        return_value=Response(200, json=template_exec_result_success)
    )

    result = execute_template(
        "test_template",
        grouper_client,
        owner_stem_name="test:stem"
    )
    assert len(result) == 4


@respx.mock
def test_execute_template_with_inputs(grouper_client):
    respx.post(url=data.URI_BASE + "/gshTemplateExec").mock(
        return_value=Response(200, json=template_exec_result_success)
    )

    inputs = [
        {"name": "param1", "value": "value1"},
        {"name": "param2", "value": "value2"}
    ]

    result = execute_template(
        "test_template",
        grouper_client,
        inputs=inputs
    )
    assert len(result) == 4


@respx.mock
def test_execute_template_with_ws_input(grouper_client):
    respx.post(url=data.URI_BASE + "/gshTemplateExec").mock(
        return_value=Response(200, json=template_exec_result_success)
    )

    ws_input = {"custom_data": "test_value", "options": {"debug": True}}

    result = execute_template(
        "test_template",
        grouper_client,
        ws_input=ws_input
    )
    assert len(result) == 4


@respx.mock
def test_execute_template_full_params(grouper_client):
    respx.post(url=data.URI_BASE + "/gshTemplateExec").mock(
        return_value=Response(200, json=template_exec_result_success)
    )

    inputs = [{"name": "param1", "value": "value1"}]
    ws_input = {"custom_data": "test_value"}

    result = execute_template(
        "test_template",
        grouper_client,
        owner_stem_name="test:stem",
        owner_type="stem",
        inputs=inputs,
        ws_input=ws_input
    )
    assert len(result) == 4


@respx.mock
def test_execute_template_empty_result(grouper_client):
    respx.post(url=data.URI_BASE + "/gshTemplateExec").mock(
        return_value=Response(200, json=template_exec_result_empty)
    )

    result = execute_template("test_template", grouper_client)
    assert len(result) == 0


@respx.mock
def test_client_execute_template(grouper_client):
    respx.post(url=data.URI_BASE + "/gshTemplateExec").mock(
        return_value=Response(200, json=template_exec_result_success)
    )

    result = grouper_client.execute_template("test_template")
    assert len(result) == 4
    assert result[0] == "Template execution started"


@respx.mock
def test_client_execute_template_with_params(grouper_client):
    respx.post(url=data.URI_BASE + "/gshTemplateExec").mock(
        return_value=Response(200, json=template_exec_result_success)
    )

    inputs = [{"name": "test_param", "value": "test_value"}]

    result = grouper_client.execute_template(
        "test_template",
        owner_stem_name="test:stem",
        inputs=inputs
    )
    assert len(result) == 4