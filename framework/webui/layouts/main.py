from dash import html
from dash import callback, callback_context, Output, Input, State
from dash.exceptions import PreventUpdate
# import dash_blueprint_components as dpc
import dash_bootstrap_components as dbc
import dash_core_components as dcc

def create_schem_component(name: str, description: str = "", items: list[dbc.ListGroupItem] = list()):
    """Create an element for each schematic component
    + name: name of the component
    + description: description of the component
    + items: items of the component
    """
    title = html.H3(name)
    title_div = html.Div([title], id=f"tooltip-{name.lower()}-target")
    
    if description:
        title_div.children.append(dbc.Tooltip(description, target=f"tooltip-{name.lower()}-target"))
    
    btn_label = "Add " + name
    btn_id = "add-" + name.lower()
    items.append(
        dbc.ListGroupItem(
            dbc.Button(btn_label, id=btn_id, style=dict(margin=0, padding=0, width="100%")),
            style=dict(margin=0, padding=0))
        )

    component_id = "component-" + name.lower()
    
    # TODO: Add a button in the title div element and make the listgroup collapsable
    return dbc.ListGroupItem([title_div, dbc.ListGroup(items)], id=component_id, action=True)
    
def create_workload_item(name, id):
    pass

def create_scheduler_item():
    pass

tools = [
    create_schem_component(name="Workloads", description="Add workloads: source, heatmap, generator, cluster", items=[]),
    create_schem_component(name="Schedulers", description="Add schedulers: known or custom", items=[]),
    create_schem_component(name="Actions", description="Add actions: preprocessing and postprocessing", items=[])
]
tools_ctn = dbc.ListGroup(children=tools, id="tools-container", key="tools-container", style=dict(width="100%"))

main_layout = dbc.Container([
    dbc.Row([
        dbc.Col(tools_ctn, width=2, style={"background-color": "gray", "height": "100%"}),
        dbc.Col(width=10, style={"height": "100%"})
    ], align="stretch")
], fluid=True, style={"height": "100%"})



component_names = ["Workloads", "Schedulers", "Actions"]
component_ouput = [Output("component-"+name.lower(), "children") for name in component_names]
component_ouput.append(Output("app-sim-schematic", "data"))

component_input = [Input("add-"+name.lower(), "n_clicks") for name in component_names]

component_state = [State("component-"+name.lower(), "children") for name in component_names]
component_state.append(State("app-sim-schematic", "data"))

@callback(
    component_ouput,
    component_input,
    component_state
)
def modify_component_list(btn_workloads, btn_schedulers, btn_actions, children_workloads, children_schedulers, children_actions, app_schematic_data):
    print(callback_context.triggered_id)
    match callback_context.triggered_id:
        case "add-workloads":
            workloads_len = len(app_schematic_data["workloads"].keys())
            workload_id = f"workload-{workloads_len - 1}"

            new_items = children_workloads[:-1]
            new_items.append(dbc.ListGroupItem(workload_id, id=workload_id))
            new_items.append(children_workloads[-1])
            
            app_schematic_data["workloads"].update({workload_id: None})

            return new_items, children_schedulers, children_actions, app_schematic_data
        case "add-schedulers":
            schedulers_len = len(app_schematic_data["schedulers"].keys())
            scheduler_id = f"workload-{schedulers_len- 1}"

            new_items = children_schedulers[:-1]
            new_items.append(dbc.ListGroupItem("scheduler"))
            new_items.append(children_schedulers[-1])
            
            app_schematic_data["schedulers"].update({scheduler_id: None})

            return children_workloads, new_items, children_actions, app_schematic_data
        case "add-actions":
            actions_len = len(app_schematic_data["actions"].keys())
            action_id = f"workload-{actions_len- 1}"

            new_items = children_actions[:-1]
            new_items.append(dbc.ListGroupItem("action"))
            new_items.append(children_actions[-1])

            app_schematic_data["actions"].update({action_id: None})

            return children_workloads, children_schedulers, new_items, app_schematic_data
        case _:
            raise PreventUpdate