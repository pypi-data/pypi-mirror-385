from . import data, global_config, load_config, randomize_conditions

# Wrap the main import in try, so that the other modules can be imported without
# dependency on pylsl (e.g. when using global_config during preprocessing).
try:
    from . import main
except Exception as e:
    print(f"Failed to import nubrain main module: {e}")
