from graphxr_database_proxy import DatabaseProxy
from pathlib import Path
proxy = DatabaseProxy()

    ## force use the ./examples/service-account.json file for demo purpose
service_account_json_path = Path("./examples/service-account.json")
if service_account_json_path.exists():
    with open(service_account_json_path, 'r', encoding='utf-8') as f:
        service_account_json = f.read()


project_id = proxy.add_project(
    project_name="test_spanner",   
    database_type="spanner",
    project_id="kineviz-spanner",
    instance_id="demo",
    database_id="paysim",
    credentials=service_account_json,
    graph_name="graph_view"  # Optional
)

proxy.start(
    host="0.0.0.0",     
    port=9080,          
    show_apis=True     
)