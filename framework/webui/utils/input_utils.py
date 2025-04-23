from dash import dcc, html, ALL
from dash import callback, callback_context, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

import base64
from utils.common_utils import create_twinfile, get_session_dir

"""
app-sim-schematic::workloads

    keyword (str): workload-{id}
    value:
        logs source (str): database, load-manager, json, path
        machine (str): optional, only with database and path
        suite (str): optional, only with database and path
        custom heatmap (bool)
        heatmap path (str): optional json file
        generator (str)
        distribution
        cluster-nodes
        cluster-socket-conf
"""

def display(val: bool):
    return "block" if val else "none"

def display_flex(val: bool):
    return "flex" if val else "none"

def safe_value_import(data, keyword, default_value):
    try:
        if not data[keyword]:
            return default_value
        return data[keyword]
    except:
        return default_value

def logs_config_elem(data=None):
    
    logs_sources = ["Database", "Load Manager", "JSON", "Path"]
    default_source = logs_sources[0]

    logs_source = safe_value_import(data, "logs-source", default_source)
    logs_source_input = safe_value_import(data, "logs-value", "")
    machine = safe_value_import(data, "logs-machine", "")
    suite = safe_value_import(data, "logs-suite", "")
        
    database_input = False
    machinesuite_input = False
    match logs_source:
        case "Database":
            database_input = True
            machinesuite_input = True
        case "Path":
            machinesuite_input = True
        case _:
            pass

    logs_sources_elem = dbc.InputGroup([
        dbc.InputGroupText("Source", style={"width": "30%"}),
        dbc.Select(logs_sources, logs_source, id="input-item-select-logs-source"),
    ])
    
    sources_input_elem = dbc.InputGroup([
        dbc.InputGroupText("Source Input", style={"width": "30%"}),
        dbc.Input(id="input-item-logs-database-input", value=logs_source_input, style={"display": display(database_input)}, className="database-input", type="text"),
        dcc.Upload(dbc.Button("Upload File", style=dict(width="100%")), id="input-item-logs-file-input", style=dict(display=display(not database_input)))
    ])
    
    logs_machine_elem = dbc.InputGroup([
        dbc.InputGroupText("Machine", style={"width": "30%"}),
        dbc.Input(id='input-item-logs-machine-input', value=machine)
    ], id="input-item-logs-machine", style=dict(display=display_flex(machinesuite_input)))

    logs_suite_elem = dbc.InputGroup([
        dbc.InputGroupText("Suite", style={"width": "30%"}), 
        dbc.Input(id='input-item-logs-suite-input', value=suite)
    ], id="input-item-logs-suite", style=dict(display=display_flex(machinesuite_input)))
    
    div = html.Div([
        html.H5("Logs configuration"),
        logs_sources_elem,
        sources_input_elem,
        logs_machine_elem,
        logs_suite_elem
    ])
    
    return div

@callback(
    Output("input-item-logs-database-input", "style"),
    Output("input-item-logs-file-input", "style"),
    Output("input-item-logs-machine", "style"),
    Output("input-item-logs-suite", "style"),
    Input("input-item-select-logs-source", "value")
)
def cb_logs_config(logs_source):

    database_input = False
    machinesuite_input = False
    match logs_source:
        case "Database":
            database_input = True
            machinesuite_input = True
        case "Path":
            machinesuite_input = True
        case _:
            pass
    
    res = [database_input, not database_input, machinesuite_input, machinesuite_input]

    return [dict(display=display_flex(val)) for val in res]
    

def heatmap_config_elem(data=None):
    custom_heatmap_enabled = safe_value_import(data, "custom-heatmap-enabled", False)
    heatmap_checkbox = dbc.Checkbox(label="Custom Heatmap", value=custom_heatmap_enabled, id="input-item-custom-heatmap-switch")
    heatmap_button = dcc.Upload(dbc.Button("Upload file", style=dict(width="100%")), id='input-item-custom-heatmap', disabled=(not custom_heatmap_enabled))
    
    div = html.Div([
        html.H5("Heatmap configuration"),
        heatmap_checkbox,
        heatmap_button 
    ])
    
    return div

@callback(
    Output("input-item-custom-heatmap", "disabled"),
    Input("input-item-custom-heatmap-switch", "value")
)
def cb_heatmap_config(custom_heatmap_enabled):
    return not custom_heatmap_enabled


def workload_generation_config_elem(data=None):
    
    bundled_generators = ["Random", "File"]
    default_generator = "Random"
    
    generator = safe_value_import(data, "generator", default_generator)
    generator_value = safe_value_import(data, "generator-value", 1)
    
    generator_value_input = True
    match generator:
        case "File":
            generator_value_input = False
        case _:
            pass
    
    generators_select_elem = dbc.InputGroup([
        dbc.InputGroupText("Generator", style={"width": "30%"}),
        dbc.Select(bundled_generators, generator, id="input-item-select-jobs-generator"),
    ])
    
    generators_inputs_elem = dbc.InputGroup([
        dbc.InputGroupText("Generator Input", style={"width": "30%"}),
        dbc.Input(id="input-item-generator-input-value", type="number", min=1, value=generator_value, style=dict(display=display(generator_value_input))),
        dcc.Upload(dbc.Button("Upload file"), id="input-item-generator-input-file", style=dict(display=display(not generator_value_input)))
    ])
    
    enabled_distribution = safe_value_import(data, "distribution-enabled", False)
    distribution_switch_elem = dbc.Switch(label="Enable distribution", value=enabled_distribution, id="input-item-enable-distribution")

    bundled_distributions = ["Constant", "Random", "File"]
    default_distribution = "Constant"
    
    distribution = safe_value_import(data, "distribution", default_distribution)
    distribution_value = safe_value_import(data, "distribution-value", 1)
    
    distribution_value_input = True
    match distribution:
        case "File":
            distribution_value_input = False
        case _:
            pass
    
    distribution_select_elem = dbc.InputGroup([
        dbc.InputGroupText("Distribution", style={"width": "30%"}),
        dbc.Select(bundled_distributions, distribution, id="input-item-select-jobs-distribution"),
    ])
    
    distributions_inputs_elem = dbc.InputGroup([
        dbc.InputGroupText("Distribution Input", style={"width": "30%"}),
        dbc.Input(id="input-item-distribution-input-value", type="number", min=1, value=distribution_value, style=dict(display=display(distribution_value_input))),
        dcc.Upload(dbc.Button("Upload file"), id="input-item-distribution-input-file", style=dict(display=display(not distribution_value_input)))
    ])
    
    distribution_div = html.Div([
        distribution_select_elem,
        distributions_inputs_elem
    ], id="input-item-distribution-div", style=dict(display=display(enabled_distribution)))
    
    div = html.Div([
        html.H5("Workload configuration"),
        generators_select_elem,
        generators_inputs_elem,
        distribution_switch_elem,
        distribution_div
    ])
    
    return div

@callback(
    Output("input-item-generator-input-value", "style"),
    Output("input-item-generator-input-file", "style"),
    Output("input-item-distribution-div", "style"),
    Output("input-item-distribution-input-value", "style"),
    Output("input-item-distribution-input-file", "style"),

    Input("input-item-select-jobs-generator", "value"),
    Input("input-item-enable-distribution", "value"),
    Input("input-item-select-jobs-distribution", "value"),

    State("input-item-generator-input-value", "style"),
    State("input-item-generator-input-file", "style"),
    State("input-item-distribution-div", "style"),
    State("input-item-distribution-input-value", "style"),
    State("input-item-distribution-input-file", "style"),
)
def cb_workload_generation_config(generator, 
                                  enabled_distribution,
                                  distribution, 
                                  
                                  generator_value_style,
                                  generator_file_style,
                                  distribution_div_style,
                                  distribution_value_style,
                                  distribution_file_style
                                  ):

    match callback_context.triggered_id:
        case "input-item-select-jobs-generator":
            print(generator)
            generator_value_input = True
            match generator:
                case "File":
                    generator_value_input = False
                case _:
                    pass
            return [
                dict(display=display(generator_value_input)), 
                dict(display=display(not generator_value_input)),
                distribution_div_style,
                distribution_value_style,
                distribution_file_style
            ]
                
        case "input-item-enable-distribution":
            print(enabled_distribution)
            return [
                generator_value_style,
                generator_file_style,
                dict(display=display(enabled_distribution)), 
                distribution_value_style,
                distribution_file_style
            ]

        case "input-item-select-jobs-distribution":

            distribution_value_input = True
            match distribution:
                case "File":
                    distribution_value_input = False
                case _:
                    pass

            return [
                generator_value_style,
                generator_file_style,
                distribution_div_style,
                dict(display=display(distribution_value_input)), 
                dict(display=display(not distribution_value_input)),
            ]
            
        case _:
            raise PreventUpdate


def cluster_config_elem(data=None):

    default_nodes = 1
    nodes = safe_value_import(data, "cluster-nodes", default_nodes)

    default_socket_conf = [2, 2]
    socket_conf = safe_value_import(data, "cluster-socket-conf", default_socket_conf)
    
    cluster_nodes_elem = dbc.InputGroup([
        dbc.InputGroupText("Nodes", style={"width": "30%"}),
        dbc.Input(id="input-item-cluster-nodes", min=default_nodes, value=nodes, type="number"),
    ])

    cluster_socket_conf_elem = dbc.InputGroup([
        dbc.InputGroupText("Socket configuration", style={"width": "30%"}),
        dbc.Input(id="input-item-cluster-socket-config", value=str(socket_conf), type="text")
    ])
    
    div = html.Div([
        html.H5("Cluster"),
        cluster_nodes_elem,
        cluster_socket_conf_elem
    ])
    
    return div


def input_item_modal_body(data=None, index=None):

    if data is None:

        div = html.Div([
            
            logs_config_elem(),
            
            heatmap_config_elem(),
            
            workload_generation_config_elem(),

            cluster_config_elem(),

            dbc.Button("Save Input", id="input-item-save-btn", style=dict(width="100%", display=display(True))),
            # dbc.Button("Modify Input", id={"modify-item": "input", "index": index}, style=dict(width="100%", display=display(False)))

        ])
    
    else:
        
        div = html.Div([
            
            logs_config_elem(data),
            
            heatmap_config_elem(data),
            
            workload_generation_config_elem(data),

            cluster_config_elem(data),

            dbc.Button("Save Input", id="input-item-save-btn", style=dict(width="100%", display=display(False))),
            dbc.Button("Modify Input", id={"modify-item": "input", "index": index}, style=dict(width="100%", display=display(True)))

        ])
    
    return div

inputs_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Inputs")),
    dbc.ModalBody(input_item_modal_body(), id="inputs-modal-body")
], id="inputs-modal", is_open=False, size="lg", centered=True)

@callback(
   Output("inputs-modal", "is_open"),
   Output("inputs-modal-body", "children"),
   Output("add-inputs", "n_clicks"),
   Output({"item": "input", "index": ALL}, "n_clicks"),
   Input("add-inputs", "n_clicks"),
   Input({"item": "input", "index": ALL}, "n_clicks"),
   State("app-sim-schematic", "data"),
   prevent_initial_call=True,
)
def inputs_modal_open(add_inputs_clicks, m_clicks, data):
    
    if not add_inputs_clicks and not any(m_clicks):
        raise PreventUpdate

    trigger_id = callback_context.triggered_id
    print(trigger_id)
    if trigger_id == "add-inputs":
        return True, input_item_modal_body(), None, [None] * len(m_clicks)
    else:
        idx = int(trigger_id["index"])
        return True, input_item_modal_body(data["inputs"][f"input-{idx}"], idx), None, [None] * len(m_clicks)

@callback(
    Output("app-sim-schematic", "data", allow_duplicate=True),
    Output("inputs-modal", "is_open", allow_duplicate=True),

    Input("input-item-save-btn", "n_clicks"),
    Input({"modify-item": "input", "index": ALL}, "n_clicks"),

    # Logs configuration
    State("input-item-select-logs-source", "value"),

    State("input-item-logs-database-input", "value"),
    State("input-item-logs-file-input", "filename"),
    State("input-item-logs-file-input", "contents"),

    State("input-item-logs-machine-input", "value"),
    State("input-item-logs-suite-input", "value"),
    
    # Heatmap configuration
    State("input-item-custom-heatmap-switch", "value"),
    State("input-item-custom-heatmap", "filename"),
    State("input-item-custom-heatmap", "contents"),
    
    # Workload configuration
    State("input-item-select-jobs-generator", "value"),
    
    State("input-item-generator-input-value", "value"),
    State("input-item-generator-input-file", "filename"),
    State("input-item-generator-input-file", "contents"),
    
    State("input-item-enable-distribution", "value"),
    State("input-item-select-jobs-distribution", "value"),
    State("input-item-distribution-input-value", "value"),
    State("input-item-distribution-input-file", "filename"),
    State("input-item-distribution-input-file", "contents"),

    State("input-item-cluster-nodes", "value"),
    State("input-item-cluster-socket-config", "value"),

    State("app-sim-schematic", "data"),
    State("app-session-store", "data"),
    
    prevent_initial_call=True
)
def save_input_item(input_save_clicks, 
                    input_modifiers_clicks,
                    
                    logs_source,
                    logs_database_value,
                    logs_file_name,
                    logs_file_contents,
                    logs_machine,
                    logs_suite,

                    custom_heatmap_enabled,
                    custom_heatmap_filename,
                    custom_heatmap_contents,

                    generator,
                    generator_value,
                    generator_file_name,
                    generator_file_contents,
                    distribution_enabled,
                    distribution,
                    distribution_value,
                    distribution_file_name,
                    distribution_file_contents,

                    cluster_nodes,
                    cluster_socket_conf,

                    schematic_data,
                    session_data
                    
                    ):
    if not input_save_clicks and not any(input_modifiers_clicks):
        raise PreventUpdate
    
    # Get the session's working directory
    session_dir = get_session_dir(session_data)
    
    triggered_id = callback_context.triggered_id
    print(triggered_id)
    
    modal_remains_open = True
    
    # Create the input item's data
    data = dict()
    
    # Logs configuration handling
    data["logs-source"] = logs_source
    if logs_source == "Database":
        if not logs_database_value:
            raise PreventUpdate
        data["logs-value"] = logs_database_value
    else:
        if triggered_id == "input-item-save-btn":
            if logs_source == "JSON":
                content_type = "json"
            else:
                content_type = "data"
            filename = create_twinfile(session_dir, logs_file_name, logs_file_contents, content_type)
            data["logs-value"] = filename
        else:
            index = triggered_id["index"]
            data["logs-value"] = schematic_data["inputs"][f"input-{index}"]["logs-value"]
        
    if not logs_machine:
        logs_machine = ""
    if not logs_suite:
        logs_suite = ""
    
    data["logs-machine"] = logs_machine
    data["logs-suite"] = logs_suite
    
    # Custom heatmap configuration handling
    data["custom-heatmap-enabled"] = custom_heatmap_enabled
    data["custom-heatmap-value"] = ""
    
    if custom_heatmap_enabled:
        if triggered_id == "input-item-save-btn":
            filename = create_twinfile(session_dir, custom_heatmap_filename, custom_heatmap_contents, "json")
            data["custom-heatmap-value"] = filename
        else:
            index = triggered_id["index"]
            data["custom-heatmap-value"] = schematic_data["inputs"][f"input-{index}"]["custom-heatmap-value"]
    
    # Workload configuration handling
    data["generator"] = generator
    if generator == "Random":
        data["generator-value"] = generator_value
    else:
        if triggered_id == "input-item-save-btn":
            filename = create_twinfile(session_dir, generator_file_name, generator_file_contents, "data")
            data["generator-value"] = filename
        else:
            index = triggered_id["index"]
            data["generator-value"] = schematic_data["inputs"][f"input-{index}"]["generator-value"]
    
    data["distribution-enabled"] = distribution_enabled
    data["distribution"] = distribution
    if distribution == "File":
        if triggered_id == "input-item-save-btn":
            filename = create_twinfile(session_dir, distribution_file_name, distribution_file_contents, "data")
            data["distribution-value"] = filename
        else:
            index = triggered_id["index"]
            data["distribution-value"] = schematic_data["inputs"][f"input-{index}"]["distribution-value"]
    else:
        data["distribution-value"] = distribution_value
    
    data["cluster-nodes"] = cluster_nodes
    data["cluster-socket-conf"] = cluster_socket_conf

    if triggered_id == "input-item-save-btn":
        # Find the new scheduler's id based on the already existing ids
        stored_input_ids = set(
            [int(keyval.split('-')[1]) for keyval in schematic_data["inputs"].keys()]
        )
        max_val = -1
        if stored_input_ids:
            max_val = max(stored_input_ids)
            possible_input_ids = set(range(0, max_val+1))
            diff = possible_input_ids - stored_input_ids
            # If there are unused ids inside the range of the current 0 and max then use them
            if diff:
                input_id = diff.pop()
            else:
                input_id = max_val + 1
        else:
            input_id = max_val + 1

    
        data["name"] = f"Input {input_id}"
        
        schematic_data["inputs"].update({f"input-{input_id}": data})
    
    else:
        
        index = triggered_id["index"]
        data["name"] = f"Input {index}"
        schematic_data["inputs"][f"input-{index}"] = data
        modal_remains_open = False
    
    return schematic_data, modal_remains_open


@callback(
    Output("app-sim-schematic", "data", allow_duplicate=True),
    Input({"delete-item": "input", "index": ALL}, "n_clicks"),
    State("app-sim-schematic", "data"),
    prevent_initial_call=True,
)
def remove_input_item(n_clicks, schematic_data):
    if not any(n_clicks):
        raise PreventUpdate
    
    triggered_id = callback_context.triggered_id
    index = triggered_id["index"]

    # Find the index of the input's id and return the option value (= inputId + 1)
    value = list(schematic_data["inputs"].keys()).index(f"input-{index}") + 1

    # For each action remove the option and update the larger options
    for action_val in schematic_data["actions"].values():
        new_inputs_options = []
        for opt_val in action_val["inputs"]:
            if opt_val < value:
                new_inputs_options.append(opt_val)
            elif opt_val > value:
                new_inputs_options.append(opt_val - 1)
            else:
                continue
        action_val["inputs"] = new_inputs_options

    schematic_data["inputs"].pop(f"input-{index}")
    
    return schematic_data

