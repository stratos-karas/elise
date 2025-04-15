import dash_bootstrap_components as dbc

def action_item(name: str):
    formatted_name = "-".join(name.lower().split())
    check_id = "action-" + formatted_name + "-check"
    btn_id = "action-" + formatted_name + "-btn"

    return dbc.ButtonGroup([
        dbc.Checkbox(id=check_id),
        dbc.Button(name, id=btn_id, color="secondary", outline=True, size="sm", style={"flex": 1, "border": "none", "textAlign": "left", "margin": 0})
    ], style={"paddingLeft": "10%"})

action_item_get_workloads = action_item("Get workloads")
action_item_get_gantt_diagrams = action_item("Get gantt diagrams")
action_item_get_waiting_queue_diagram = action_item("Get waiting queue diagram")
action_item_get_jobs_throughput_diagram = action_item("Get jobs throughput diagram")
action_item_get_unused_cores_diagram = action_item("Get unsued cores diagram")


action_items = [
    action_item_get_workloads,
    action_item_get_gantt_diagrams,
    action_item_get_waiting_queue_diagram,
    action_item_get_jobs_throughput_diagram,
    action_item_get_unused_cores_diagram
]

action_items_ctn = dbc.Stack(action_items)