import dash_bootstrap_components as dbc
from dash_extensions.enrich import State, Input, Output, dcc, html, callback, ALL, callback_context, MATCH
from dash.exceptions import PreventUpdate

def display(val: bool):
    return "block" if val else "none"

def action_item_name(name: str):
    return "-".join(name.lower().split())

def action_item(name: str):
    formatted_name = action_item_name(name)
    check_id = {"check-item": "action", "index": formatted_name}
    btn_id = {"edit-item": "action", "index": formatted_name}

    return dbc.ButtonGroup([
        dbc.Checkbox(id=check_id, value=False, persistence_type="session", persistence=True),
        dbc.Button(name, id=btn_id, color="secondary", outline=True, size="sm", style={"flex": 1, "border": "none", "textAlign": "left", "margin": 0})
    ], style={"paddingLeft": "10%"})

action_items_names = [
    "Get workloads",
    "Get gantt diagrams",
    "Get waiting queue diagrams",
    "Get jobs throughput diagrams",
    "Get unused cores diagrams",
    "Get animated clusters"
]

action_items = [action_item(name) for name in action_items_names]
action_items_ctn = dbc.Stack(action_items)


def action_modal_get_content(name, data, index):
    title = html.H5(name, style={"flex": 1})
    # select_all = dbc.Switch(id={"action": "select-all", "index": index, "type": f"{name.lower()}"}, style={"flex": 0})
    select_all = dbc.Switch(id={"action-type": index, "check-input": f"{name.lower()}", "type": "select-all"}, style={"flex": 0})
    header = dbc.Row([title, select_all])
    #checklist_id = f"action-{index}-{name.lower()}-checklist"
    checklist_id = {"action-type": index, "check-input": f"{name.lower()}", "type": "checklist"}
    checklist = dbc.Checklist(
        options=[{"label": f"{name.lower()}-{i}", "value": i+1} for i in range(len(data[name.lower()]))],
        value=data["actions"][index][name.lower()],
        inline=True,
        id=checklist_id
    )
    return html.Div([header, checklist])

def action_modal_for_index(data, index, visible):
    print(index, visible)
    return dbc.Stack([
        action_modal_get_content("Inputs", data, index),
        action_modal_get_content("Schedulers", data, index),
        dbc.Button("Modify Action", id={"modify-item": "action", "index": index}, style={"width": "100%"})
    ], gap=3, style=dict(display=display(visible), width="100%"))

def actions_modal_body(data, index):
    # Get all the inputs and schedulers and present them as checkboxes
    # Add a default checkbox called "all" to select all checkboxes or a button that checks them all
    unavailable_data = not data["inputs"] or not data["schedulers"]
    
    paragraph = html.Div(html.P("The schematic hasn't been fully configured to define specific actions"), style=dict(display=display(unavailable_data)))
    
    # print(index)
    
    # For every possible index
    children = [paragraph]
    for _index in action_items_names:
        children.append(action_modal_for_index(data, action_item_name(_index), action_item_name(_index) == index and not unavailable_data))

    div = html.Div(children)
    return div

actions_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle(id="actions-modal-title")),
    dbc.ModalBody(id="actions-modal-body")
], id="actions-modal", is_open=False, size="lg", centered=True)


def action_modal_title(id: str):
    title = id.replace("-", "\n")
    return title.title()

@callback(
    Output("actions-modal", "is_open"),
    Output("actions-modal-title", "children"),
    Output("actions-modal-body", "children"),
    Input({"edit-item": "action", "index": ALL}, "n_clicks"),
    State("app-sim-schematic", "data"),
    prevent_initial_call=True
)
def actions_modal_open(n_clicks, schematic_data):
    
    if not any(n_clicks):
        raise PreventUpdate

    triggered_id = callback_context.triggered_id
    index = triggered_id["index"]
    match index:
        case "get-workloads":
            return True, action_modal_title(index), actions_modal_body(schematic_data, "get-workloads")
        case "get-gantt-diagrams":
            return True, action_modal_title(index), actions_modal_body(schematic_data, "get-gantt-diagrams")
        case "get-waiting-queue-diagrams":
            return True, action_modal_title(index), actions_modal_body(schematic_data, "get-waiting-queue-diagrams")
        case "get-jobs-throughput-diagrams":
            return True, action_modal_title(index), actions_modal_body(schematic_data, "get-jobs-throughput-diagrams")
        case "get-unused-cores-diagrams":
            return True, action_modal_title(index), actions_modal_body(schematic_data, "get-unused-cores-diagrams")
        case "get-animated-clusters":
            return True, action_modal_title(index), actions_modal_body(schematic_data, "get-animated-clusters")
        case _:
            raise PreventUpdate

    
@callback(
    Output("app-sim-schematic", "data", allow_duplicate=True),
    Output("actions-modal", "is_open", allow_duplicate=True),

    Input({"modify-item": "action", "index": ALL}, "n_clicks"),

    State({"action-type": "get-workloads", "check-input": "inputs", "type": "checklist"}, "value"),
    State({"action-type": "get-workloads", "check-input": "schedulers", "type":  "checklist"}, "value"),

    State({"action-type": "get-gantt-diagrams", "check-input": "inputs", "type": "checklist"}, "value"),
    State({"action-type": "get-gantt-diagrams", "check-input": "schedulers", "type": "checklist"}, "value"),

    State({"action-type": "get-waiting-queue-diagrams", "check-input": "inputs", "type": "checklist"}, "value"),
    State({"action-type": "get-waiting-queue-diagrams", "check-input": "schedulers", "type": "checklist"}, "value"),

    State({"action-type": "get-jobs-throughput-diagrams", "check-input": "inputs", "type": "checklist"}, "value"),
    State({"action-type": "get-jobs-throughput-diagrams", "check-input": "schedulers", "type": "checklist"}, "value"),

    State({"action-type": "get-unused-cores-diagrams", "check-input": "inputs", "type": "checklist"}, "value"),
    State({"action-type": "get-unused-cores-diagrams", "check-input": "schedulers", "type": "checklist"}, "value"),

    State({"action-type": "get-animated-clusters", "check-input": "inputs", "type": "checklist"}, "value"),
    State({"action-type": "get-animated-clusters", "check-input": "schedulers", "type": "checklist"}, "value"),
    
    State("app-sim-schematic", "data"),

    prevent_initial_call=True
)
def cb_modify_action(n_clicks,

                     get_workloads_inputs,
                     get_workloads_schedulers,

                     get_gantt_diagrams_inputs,
                     get_gantt_diagrams_schedulers,

                     get_waiting_queue_inputs,
                     get_waiting_queue_schedulers,

                     get_jobs_throughput_inputs,
                     get_jobs_throughput_schedulers,

                     get_unused_cores_inputs,
                     get_unused_cores_schedulers,
                     
                     get_animated_clusters_inputs,
                     get_animated_clusters_schedulers,
                     
                     schematic_data):
    if not any(n_clicks):
        raise PreventUpdate
    
    triggered_id = callback_context.triggered_id
    index = triggered_id["index"]
    
    match index:
        case "get-workloads":
            schematic_data["actions"][index]["inputs"] = get_workloads_inputs
            schematic_data["actions"][index]["schedulers"] = get_workloads_schedulers
        case "get-gantt-diagrams":
            schematic_data["actions"][index]["inputs"] = get_gantt_diagrams_inputs
            schematic_data["actions"][index]["schedulers"] = get_gantt_diagrams_schedulers
        case "get-waiting-queue-diagrams":
            schematic_data["actions"][index]["inputs"] = get_waiting_queue_inputs
            schematic_data["actions"][index]["schedulers"] = get_waiting_queue_schedulers
        case "get-jobs-throughput-diagrams":
            schematic_data["actions"][index]["inputs"] = get_jobs_throughput_inputs
            schematic_data["actions"][index]["schedulers"] = get_jobs_throughput_schedulers
        case "get-unused-cores-diagrams":
            schematic_data["actions"][index]["inputs"] = get_unused_cores_inputs
            schematic_data["actions"][index]["schedulers"] = get_unused_cores_schedulers
        case "get-animated-clusters":
            schematic_data["actions"][index]["inputs"] = get_animated_clusters_inputs
            schematic_data["actions"][index]["schedulers"] = get_animated_clusters_schedulers
        case _:
            raise PreventUpdate
    
    return schematic_data, False

@callback(
    Output({"action-type": MATCH, "check-input": MATCH, "type": "checklist"}, "value"),
    Input({"action-type": MATCH, "check-input": MATCH, "type": "select-all"}, "value"),
    State({"action-type": MATCH, "check-input": MATCH, "type": "checklist"}, "options"),
    prevent_initial_call=True
)
def cb_select_all_checkboxes(value, options):
    print("Inside action switch")
    triggered_id = callback_context.triggered_id
    check_input = triggered_id["check-input"]
    # raise PreventUpdate
    if value:
        return [x+1 for x in range(len(options))]
    return []
    
# @callback(
#     Output("app-sim-schematic", "data", allow_duplicate=True),
#     Input({"check-item": "action", "index": ALL}, "value"),
#     State("app-sim-schematic", "data"),
#     prevent_initial_call=True
# )
# def cb_action_item_check_toggled(values, schematic_data):
#     if not any(values):
#         raise PreventUpdate
    
#     triggered_id = callback_context.triggered_id
#     index = triggered_id["index"]
#     action_indices_names = [action_item_name(name) for name in action_items_names]
#     pos = action_indices_names.index(index)

#     # schematic_data["actions"][index]["enabled"] = not schematic_data["actions"][index]["enabled"]
#     schematic_data["actions"][index]["enabled"] = values[pos]
    
#     return schematic_data