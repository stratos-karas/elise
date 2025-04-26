# Python dependencies
import os
from time import sleep
import sys
from yaml import safe_dump, safe_load

# Dash dependencies
from dash import dcc, html, ALL
from dash import callback, callback_context, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# WebUI dependencies
from utils.common_utils import get_session_dir



def transform_socket_conf(socket_conf_str: str) -> list[int]:
    socket_conf_str = socket_conf_str.strip("[]").replace(',', '')
    socket_conf = [int(cores) for cores in socket_conf_str.split()]
    return socket_conf

def transform_input(data):
    batch_input = dict()
    batch_input["loads-machine"] = ""
    batch_input["loads-suite"] = ""
    match data["logs-source"]:
        case "Database":
            batch_input["db"] = data["logs-value"]
            batch_input["loads-machine"] = data["logs-machine"] # loads to logs
            batch_input["loads-suite"] = data["logs-suite"] # loads to logs
        case "JSON":
            batch_input["json"] = data["logs-value"]
        case _:
            batch_input["load-manager"] = data["logs-value"]
    
    if data["custom-heatmap-enabled"]:
        batch_input["heatmap"] = data["custom-heatmap-value"]
    
    batch_input["generator"] = dict()
    batch_input["generator"]["type"] = data["generator"] + " Generator" # change how we do this (for example add aliases)
    batch_input["generator"]["arg"] = data["generator-value"]
    
    if data["distribution-enabled"]:
        batch_input["generator"]["distribution"] = dict()
        batch_input["generator"]["distribution"]["type"] = data["distribution"]
        batch_input["generator"]["distribution"]["arg"] = data["distribution-value"]
    
    batch_input["cluster"] = dict()
    batch_input["cluster"]["nodes"] = data["cluster-nodes"]
    batch_input["cluster"]["socket-conf"] = transform_socket_conf(data["cluster-socket-conf"])
    
    return batch_input
    
def transform_inputs(inputs):
    return [transform_input(value) for value in inputs.values()]

def transform_schedulers(schedulers):
    batch_schedulers = dict()
    batch_schedulers["default"] = ""
    batch_schedulers["others"] = []
    batch_schedulers["global_options"] = {"backfill_enabled": True, "compact_fallback": True}

    for val in schedulers.values():
        if 1 in val["options"]:
            batch_schedulers["default"] = val["value"]
        else:
            batch_schedulers["others"].append(val["value"])
    
    return batch_schedulers


def transform_actions(actions, session_data):
    batch_actions = dict()
    for action_name, action_args in actions.items():
        batch_actions[action_name] = dict()
        for arg_name, arg_value in action_args.items():
            # Decrease the index by 1 (WebUI checklist starts counting from 1)
            new_values = [x-1 for x in arg_value]
            batch_actions[action_name].update({arg_name: new_values})
        # Add results directory for each action
        # This will be usefull to export and import results
        batch_actions[action_name].update(dict(dir=f"{get_session_dir(session_data)}/results"))
    return batch_actions

def export_schematic(schematic_data, session_data):
    batch_data = dict(
        name=schematic_data["name"],
        description=schematic_data["description"],
        inputs=transform_inputs(schematic_data["inputs"]),
        schedulers=transform_schedulers(schematic_data["schedulers"]),
        actions=transform_actions(schematic_data["actions"], session_data)
    )
    
    session_dir = get_session_dir(session_data)
    if not os.path.isdir(session_dir):
        os.makedirs(session_dir, exist_ok=True)

    filename = f"{session_dir}/project.yaml"
    with open(filename, "w") as fd:
        fd.write(safe_dump(batch_data))
    
    return filename
