"""
Provenance Tracking and Inspection Example for Herrkunft Library

This example demonstrates:
- Accessing and inspecting provenance information
- Provenance history tracking through modifications
- Extracting provenance trees
- Cleaning provenance for export
"""

from herrkunft import (
    load_yaml,
    dump_yaml,
    extract_provenance_tree,
    clean_provenance,
    DictWithProvenance,
)
import tempfile
from pathlib import Path
import json


def main():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create a sample configuration
        config_file = tmpdir / "app_config.yaml"
        config_file.write_text("""
application:
  name: MyApp
  version: 1.0.0

database:
  host: localhost
  port: 5432
  credentials:
    username: dbuser
    password: secret

servers:
  - name: server1
    host: 192.168.1.10
    port: 8080
  - name: server2
    host: 192.168.1.11
    port: 8081
""")

        print("=" * 60)
        print("PROVENANCE TRACKING AND INSPECTION EXAMPLE")
        print("=" * 60)

        # 1. Load configuration
        print("\n1. Loading configuration with provenance...")
        config = load_yaml(str(config_file), category="application", subcategory="main")

        # 2. Inspect individual value provenance
        print("\n2. Inspecting provenance of individual values...")

        app_name = config["application"]["name"]
        print(f"\n   Value: application.name = '{app_name}'")

        prov = app_name.provenance
        print(f"   Provenance history length: {len(prov)}")

        for i, step in enumerate(prov):
            print(f"\n   Step {i}:")
            print(f"     Source file: {Path(step.yaml_file).name if step.yaml_file else 'N/A'}")
            print(f"     Line: {step.line}, Column: {step.col}")
            print(f"     Category: {step.category}")
            print(f"     Subcategory: {step.subcategory}")
            if step.modified_by:
                print(f"     Modified by: {step.modified_by}")
            if step.choose_history:
                print(f"     Choose history: {step.choose_history}")

        # 3. Modify values and track history
        print("\n3. Modifying values and tracking provenance history...")

        original_host = config["database"]["host"]
        print(f"\n   Original database host: {original_host}")
        print(f"   Original provenance steps: {len(original_host.provenance)}")

        # Make several modifications
        config["database"]["host"] = "staging.db.example.com"
        print(f"   After 1st modification: {config['database']['host']}")
        print(f"   Provenance steps: {len(config['database']['host'].provenance)}")

        config["database"]["host"] = "production.db.example.com"
        print(f"   After 2nd modification: {config['database']['host']}")
        print(f"   Provenance steps: {len(config['database']['host'].provenance)}")

        # Inspect the full history
        print("\n   Full provenance history:")
        for i, step in enumerate(config["database"]["host"].provenance):
            print(f"     [{i}] {Path(step.yaml_file).name if step.yaml_file else 'runtime'} "
                  f"(category: {step.category})")

        # 4. Extract full provenance tree
        print("\n4. Extracting complete provenance tree...")

        prov_tree = extract_provenance_tree(config)

        print("\n   Provenance tree structure:")
        print(f"   Keys: {list(prov_tree.keys())}")

        # Show database credentials provenance
        db_prov = prov_tree["database"]
        print(f"\n   Database provenance:")
        print(f"     host: line {db_prov['host']['line']}, category: {db_prov['host']['category']}")
        print(f"     port: line {db_prov['port']['line']}, category: {db_prov['port']['category']}")
        print(f"     username: line {db_prov['credentials']['username']['line']}, "
              f"category: {db_prov['credentials']['username']['category']}")

        # 5. Export provenance as JSON
        print("\n5. Exporting provenance tree as JSON...")

        prov_json_file = tmpdir / "provenance_tree.json"
        with open(prov_json_file, "w") as f:
            json.dump(prov_tree, f, indent=2, default=str)

        print(f"   Saved to: {prov_json_file.name}")
        print(f"   File size: {prov_json_file.stat().st_size} bytes")

        # Show a snippet
        print("\n   Sample provenance tree JSON:")
        tree_json = json.dumps(prov_tree["application"], indent=2, default=str)
        for line in tree_json.split("\n")[:10]:
            print(f"   {line}")
        print("   ...")

        # 6. Clean provenance for export
        print("\n6. Cleaning provenance from configuration...")

        cleaned_config = clean_provenance(config)

        print(f"   Original type: {type(config).__name__}")
        print(f"   Cleaned type: {type(cleaned_config).__name__}")
        print(f"   Original has provenance: {isinstance(config, DictWithProvenance)}")
        print(f"   Cleaned has provenance: {isinstance(cleaned_config, DictWithProvenance)}")

        # Verify cleaned config is plain Python types
        print(f"\n   Cleaned config types:")
        print(f"     config: {type(cleaned_config)}")
        print(f"     config['database']: {type(cleaned_config['database'])}")
        print(f"     config['database']['host']: {type(cleaned_config['database']['host'])}")
        print(f"     config['servers']: {type(cleaned_config['servers'])}")

        # Export cleaned config
        clean_export_file = tmpdir / "clean_config.yaml"
        dump_yaml(cleaned_config, str(clean_export_file), include_provenance=False, clean=True)

        print(f"\n   Exported clean config to: {clean_export_file.name}")

        # 7. Get provenance at specific history index
        print("\n7. Accessing provenance at specific points in history...")

        host_value = config["database"]["host"]
        print(f"   Current host: {host_value}")
        print(f"   Total history steps: {len(host_value.provenance)}")

        # Get provenance at different points
        if len(host_value.provenance) > 1:
            prov_0 = extract_provenance_tree(config, index=0)
            prov_current = extract_provenance_tree(config, index=-1)

            print(f"\n   Provenance at step 0 (original):")
            print(f"     Category: {prov_0['database']['host']['category']}")
            print(f"     File: {Path(prov_0['database']['host']['yaml_file']).name}")

            print(f"\n   Provenance at current step:")
            print(f"     Category: {prov_current['database']['host']['category']}")
            if prov_current['database']['host']['modified_by']:
                print(f"     Modified by: {prov_current['database']['host']['modified_by']}")

        # 8. Demonstrate nested structure provenance
        print("\n8. Nested structure provenance tracking...")

        print(f"\n   Server list provenance:")
        for i, server in enumerate(config["servers"]):
            server_name = server["name"]
            server_prov = server_name.provenance.current
            print(f"     Server {i} name: {server_name}")
            print(f"       Line: {server_prov.line}, Category: {server_prov.category}")

        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)


if __name__ == "__main__":
    main()
