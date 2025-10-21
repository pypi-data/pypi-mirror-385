from .settings_loader import load_settings


# Load config when `mizuhara` is imported
try:
    settings = load_settings()

# add exception handler to avoid exception during creating project or app
except FileNotFoundError:
    pass