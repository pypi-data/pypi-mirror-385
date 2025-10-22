"""
Hierarchical Configuration Example for Herrkunft Library

This example demonstrates:
- Loading multiple configuration files with different priorities
- Hierarchical conflict resolution (higher categories override lower)
- Category-based provenance tracking
- Merging configurations while preserving provenance history
"""

from herrkunft import load_yaml, ProvenanceLoader, HierarchyManager
import tempfile
from pathlib import Path


def main():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create multiple configuration files representing different hierarchy levels
        print("=" * 60)
        print("HIERARCHICAL CONFIGURATION EXAMPLE")
        print("=" * 60)

        # Level 1: Default configuration (lowest priority)
        defaults_file = tmpdir / "defaults.yaml"
        defaults_file.write_text("""
database:
  host: localhost
  port: 5432
  pool_size: 5
  timeout: 30

logging:
  level: INFO
  format: standard

features:
  caching: true
  analytics: false
""")

        # Level 2: Machine-specific configuration (medium priority)
        machine_file = tmpdir / "machine_hpc.yaml"
        machine_file.write_text("""
database:
  host: hpc-db.cluster.local
  pool_size: 20

logging:
  level: WARNING
""")

        # Level 3: Environment configuration (high priority)
        production_file = tmpdir / "production.yaml"
        production_file.write_text("""
database:
  host: prod.db.example.com
  port: 5433

logging:
  level: ERROR

features:
  analytics: true
""")

        print("\n1. Loading configuration files in hierarchy order...")
        print("   Level 1 (defaults)  -> defaults.yaml")
        print("   Level 2 (machines)  -> machine_hpc.yaml")
        print("   Level 3 (environment) -> production.yaml")

        # Load all files with appropriate categories
        loader = ProvenanceLoader()

        config_defaults = load_yaml(str(defaults_file), category="defaults")
        config_machine = load_yaml(str(machine_file), category="machines", subcategory="hpc")
        config_prod = load_yaml(str(production_file), category="environment", subcategory="production")

        print("\n2. Merging configurations with hierarchy resolution...")

        # Start with defaults
        final_config = config_defaults

        # Merge machine config (should override defaults)
        print("   Merging machine config into defaults...")
        final_config.update(config_machine)

        # Merge production config (should override both)
        print("   Merging production config into merged config...")
        final_config.update(config_prod)

        print("\n3. Examining final configuration and provenance...")

        # Check database settings
        print("\n   Database settings:")
        print(f"     host: {final_config['database']['host']}")
        host_prov = final_config['database']['host'].provenance.current
        print(f"       -> from {host_prov.category}/{host_prov.subcategory} ({Path(host_prov.yaml_file).name})")

        print(f"     port: {final_config['database']['port']}")
        port_prov = final_config['database']['port'].provenance.current
        print(f"       -> from {port_prov.category}/{port_prov.subcategory} ({Path(port_prov.yaml_file).name})")

        print(f"     pool_size: {final_config['database']['pool_size']}")
        pool_prov = final_config['database']['pool_size'].provenance.current
        print(f"       -> from {pool_prov.category}/{pool_prov.subcategory} ({Path(pool_prov.yaml_file).name})")

        print(f"     timeout: {final_config['database']['timeout']}")
        timeout_prov = final_config['database']['timeout'].provenance.current
        print(f"       -> from {timeout_prov.category} ({Path(timeout_prov.yaml_file).name})")

        # Check logging settings
        print("\n   Logging settings:")
        print(f"     level: {final_config['logging']['level']}")
        level_prov = final_config['logging']['level'].provenance.current
        print(f"       -> from {level_prov.category}/{level_prov.subcategory} ({Path(level_prov.yaml_file).name})")

        print(f"     format: {final_config['logging']['format']}")
        format_prov = final_config['logging']['format'].provenance.current
        print(f"       -> from {format_prov.category} ({Path(format_prov.yaml_file).name})")

        # Check features
        print("\n   Feature flags:")
        print(f"     caching: {final_config['features']['caching']}")
        caching_prov = final_config['features']['caching'].provenance.current
        print(f"       -> from {caching_prov.category} ({Path(caching_prov.yaml_file).name})")

        print(f"     analytics: {final_config['features']['analytics']}")
        analytics_prov = final_config['features']['analytics'].provenance.current
        print(f"       -> from {analytics_prov.category}/{analytics_prov.subcategory} ({Path(analytics_prov.yaml_file).name})")

        print("\n4. Hierarchy rules demonstrated:")
        print("   - database.host: environment (production) > machines (hpc) > defaults")
        print("   - database.port: environment (production) > defaults")
        print("   - database.pool_size: machines (hpc) > defaults")
        print("   - database.timeout: defaults only (not overridden)")
        print("   - logging.level: environment > machines > defaults")
        print("   - features.analytics: environment > defaults")

        print("\n5. Using ProvenanceLoader.load_multiple() for batch loading...")

        # Alternative: Load multiple files at once
        configs = loader.load_multiple([
            (str(defaults_file), "defaults"),
            (str(machine_file), "machines", "hpc"),
            (str(production_file), "environment", "production"),
        ])

        print(f"   Loaded {len(configs)} configuration files")
        print(f"   Types: {[type(c).__name__ for c in configs]}")

        # Manual merging
        merged = configs[0]  # Start with defaults
        for config in configs[1:]:
            merged.update(config)

        print(f"   Final merged config has {len(merged)} top-level keys")

        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)


if __name__ == "__main__":
    main()
