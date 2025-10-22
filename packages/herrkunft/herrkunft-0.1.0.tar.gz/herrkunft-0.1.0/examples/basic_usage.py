"""
Basic Usage Example for Herrkunft Library

This example demonstrates the fundamental operations:
- Loading YAML files with provenance tracking
- Accessing provenance information
- Modifying configuration values
- Saving configurations with provenance
"""

from herrkunft import load_yaml, dump_yaml
import tempfile
from pathlib import Path


def main():
    # Create a sample YAML file
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.yaml"
        config_file.write_text("""
database:
  host: localhost
  port: 5432
  name: myapp_db

server:
  host: 0.0.0.0
  port: 8080
  workers: 4
""")

        print("=" * 60)
        print("BASIC USAGE EXAMPLE")
        print("=" * 60)

        # 1. Load YAML with provenance tracking
        print("\n1. Loading YAML file with provenance tracking...")
        config = load_yaml(str(config_file), category="defaults")

        # Verify it's a DictWithProvenance
        from herrkunft import DictWithProvenance
        assert isinstance(config, DictWithProvenance)
        print(f"   Loaded config type: {type(config).__name__}")
        print(f"   Config keys: {list(config.keys())}")

        # 2. Access values (they behave like normal values)
        print("\n2. Accessing configuration values...")
        db_host = config["database"]["host"]
        print(f"   Database host: {db_host}")
        print(f"   Database port: {config['database']['port']}")
        print(f"   Server workers: {config['server']['workers']}")

        # 3. Access provenance information
        print("\n3. Inspecting provenance information...")
        prov = db_host.provenance
        print(f"   Value has provenance: {prov is not None}")
        print(f"   Provenance history length: {len(prov)}")

        current_step = prov.current
        print(f"   Source file: {Path(current_step.yaml_file).name}")
        print(f"   Line number: {current_step.line}")
        print(f"   Column number: {current_step.col}")
        print(f"   Category: {current_step.category}")

        # 4. Modify configuration values
        print("\n4. Modifying configuration values...")
        config["database"]["host"] = "production.db.example.com"
        config["database"]["port"] = 5433
        config["new_setting"] = "added_at_runtime"

        print(f"   Updated host: {config['database']['host']}")
        print(f"   Updated port: {config['database']['port']}")
        print(f"   New setting: {config['new_setting']}")

        # Check provenance was extended
        updated_prov = config["database"]["host"].provenance
        print(f"   Provenance history now: {len(updated_prov)} steps")

        # 5. Save configuration with provenance
        output_file = Path(tmpdir) / "output.yaml"
        print(f"\n5. Saving configuration with provenance to: {output_file.name}")
        dump_yaml(config, str(output_file), include_provenance=True)

        # Show the output
        print("\n   Generated YAML with provenance comments:")
        print("   " + "-" * 56)
        for line in output_file.read_text().split("\n")[:15]:
            print(f"   {line}")
        print("   " + "-" * 56)

        # 6. Save clean version (without provenance)
        clean_file = Path(tmpdir) / "clean.yaml"
        print(f"\n6. Saving clean version (no provenance) to: {clean_file.name}")
        dump_yaml(config, str(clean_file), include_provenance=False, clean=True)

        print("\n   Generated clean YAML:")
        print("   " + "-" * 56)
        for line in clean_file.read_text().split("\n")[:10]:
            print(f"   {line}")
        print("   " + "-" * 56)

        # 7. Reload and verify
        print("\n7. Reloading saved configuration...")
        reloaded = load_yaml(str(output_file), category="reloaded")
        print(f"   Reloaded host: {reloaded['database']['host']}")
        print(f"   Reloaded port: {reloaded['database']['port']}")
        print(f"   Has new_setting: {'new_setting' in reloaded}")

        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)


if __name__ == "__main__":
    main()
