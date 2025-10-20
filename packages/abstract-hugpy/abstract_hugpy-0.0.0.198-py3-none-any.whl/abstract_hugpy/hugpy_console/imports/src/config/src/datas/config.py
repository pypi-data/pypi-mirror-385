from ..imports import *
logger = get_logFile(__name__)
DATA_DIR = get_caller_dir()
MODULES_JSON_PATH = os.path.join(DATA_DIR,'modules.json')
MODULE_DEFAULTS = safe_load_from_json(MODULES_JSON_PATH)
input(MODULE_DEFAULTS)
DEFAULT_PATHS = {
    "whisper": MODULE_DEFAULTS.get("whisper").get('path'),
    "keybert": MODULE_DEFAULTS.get("keybert").get('path'),
    "summarizer": MODULE_DEFAULTS.get("summarizer").get('path'),
    "flan": MODULE_DEFAULTS.get("flan").get('path'),
    "bigbird": MODULE_DEFAULTS.get("bigbird").get('path'),
    "deepcoder": MODULE_DEFAULTS.get("deepcoder").get('path'),
    "huggingface": MODULE_DEFAULTS.get("huggingface").get('path'),
    "zerosearch": MODULE_DEFAULTS.get("zerosearch").get('path')
}
def resolve_model_path(entry):
    """Return a valid model path or HF repo id from DEFAULT_PATHS entry."""
    if entry is None:
        logger.error("{entry}: DEFAULT_PATHS entry missing.")
        return None
    if isinstance(entry,str) and entry in MODULE_DEFAULTS:
       return MODULE_DEFAULTS.get(entry)

    if isinstance(entry, dict):
        local_path = entry.get("path")
        repo_id = entry.get("id")
        name = entry.get("name")

        if local_path and os.path.exists(local_path):
            logger.info(f"{name} resolved local model path: {local_path}")
            return local_path

        if repo_id:
            logger.info(f"{name} resolved remote repo id: {repo_id}")
            return repo_id

        logger.error(f"{name}: malformed entry: {entry}")
        return None

    if isinstance(entry, str):
        logger.info(f"{name} using direct model string: {entry}")
        return entry

    logger.error(f"{name}: invalid model path type: {type(entry)}")
    return None
