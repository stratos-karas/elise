from dash import html
from dash import callback, callback_context, Output, Input, State
from dash.exceptions import PreventUpdate
# import dash_blueprint_components as dpc
import dash_bootstrap_components as dbc
import dash_core_components as dcc

from utils.scheduler_utils import schedulers_modal

def create_schem_component(name: str, description: str = "", items: list[dbc.ListGroupItem] = list()):
    """Create an element for each schematic component
    + name: name of the component
    + description: description of the component
    + items: items of the component
    """
    title = html.H3(name)
    title_div = html.Div([title], id=f"tooltip-{name.lower()}-target")
    
    if description:
        title_div.children.append(dbc.Tooltip(description, delay=dict(show=1000, hide=0), target=f"tooltip-{name.lower()}-target"))
    
    btn_label = "Add " + name
    btn_id = "add-" + name.lower()
    items.append(
        dbc.ListGroupItem(
            dbc.Button(btn_label, id=btn_id, style=dict(margin=0, padding=0, width="100%")),
            style=dict(margin=0, padding=0))
        )

    component_id = "component-" + name.lower()
    component_items_id = "component-" + name.lower() + "-items"
    
    # TODO: Add a button in the title div element and make the listgroup collapsable
    return dbc.ListGroupItem([title_div, dbc.ListGroup(items, id=component_items_id)], id=component_id, action=True)
    
def workload_item_modal_body(data=None):
    pass
        

tools = [
    create_schem_component(name="Workloads", description="Add workloads: source, heatmap, generator, cluster", items=[]),
    create_schem_component(name="Schedulers", description="Add schedulers: known or custom", items=[]),
    create_schem_component(name="Actions", description="Add actions: preprocessing and postprocessing", items=[]),
    schedulers_modal
]
tools_ctn = dbc.ListGroup(children=tools, id="tools-container", key="tools-container", style=dict(width="100%"))

main_layout = dbc.Container([
    dbc.Row([
        dbc.Col(tools_ctn, width=2, style={"background-color": "gray", "height": "100%"}),
        dbc.Col(width=10, style={"height": "100%"})
    ], align="stretch")
], fluid=True, style={"height": "100%"})



component_names = ["Workloads", "Schedulers", "Actions"]
component_ouput = [Output("component-"+name.lower()+"-items", "children") for name in component_names]

component_input = [Input("add-"+name.lower(), "n_clicks") for name in component_names]

component_state = [State("component-"+name.lower()+"-items", "children") for name in component_names]

@callback(
    component_ouput,
    Input("app-sim-schematic", "data"),
    component_state
)
def modify_component_items(data, workloads_children, schedulers_children, actions_children):
    print(data)
    new_workloads_children = [dbc.ListGroupItem(f"workload-{idx}") for idx, _ in enumerate(data["workloads"].keys())]
    new_workloads_children.append(workloads_children[-1])
    new_schedulers_children = [dbc.ListGroupItem(f"scheduler-{idx}") for idx, _ in enumerate(data["schedulers"].keys())]
    new_schedulers_children.append(schedulers_children[-1])
    new_actions_children = [dbc.ListGroupItem(f"action-{idx}") for idx, _ in enumerate(data["actions"].keys())]
    new_actions_children.append(actions_children[-1])
    
    return new_workloads_children, new_schedulers_children, new_actions_children



# @callback(
#     component_ouput,
#     component_input,
#     component_state
# )
# def modify_component_list(btn_workloads, btn_schedulers, btn_actions, children_workloads, children_schedulers, children_actions, app_schematic_data):
#     print(callback_context.triggered_id)
#     match callback_context.triggered_id:
#         case "add-workloads":
#             workloads_len = len(app_schematic_data["workloads"].keys())
#             workload_id = f"workload-{workloads_len - 1}"

#             new_items = children_workloads[:-1]
#             new_items.append(dbc.ListGroupItem(workload_id, id=workload_id))
#             new_items.append(children_workloads[-1])
            
#             app_schematic_data["workloads"].update({workload_id: None})

#             return new_items, children_schedulers, children_actions, app_schematic_data
#         case "add-schedulers":
#             schedulers_len = len(app_schematic_data["schedulers"].keys())
#             scheduler_id = f"workload-{schedulers_len- 1}"

#             new_items = children_schedulers[:-1]
#             new_items.append(dbc.ListGroupItem("scheduler"))
#             new_items.append(children_schedulers[-1])
            
#             app_schematic_data["schedulers"].update({scheduler_id: None})

#             return children_workloads, new_items, children_actions, app_schematic_data
#         case "add-actions":
#             actions_len = len(app_schematic_data["actions"].keys())
#             action_id = f"workload-{actions_len- 1}"

#             new_items = children_actions[:-1]
#             new_items.append(dbc.ListGroupItem("action"))
#             new_items.append(children_actions[-1])

#             app_schematic_data["actions"].update({action_id: None})

#             return children_workloads, children_schedulers, new_items, app_schematic_data
#         case _:
#             raise PreventUpdate