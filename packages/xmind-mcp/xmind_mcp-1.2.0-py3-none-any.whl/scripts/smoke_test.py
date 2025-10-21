import os
import json
from pathlib import Path

# Import server functions
from xmind_mcp_server import (
    config_manager,
    create_mind_map,
    convert_to_xmind,
    list_xmind_files,
    read_xmind_file,
)

# Ensure config is loaded so default_output_dir is available
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "configs", "xmind_mcp_config.json")
config_manager.load_config(os.path.abspath(CONFIG_PATH))
DEFAULT_OUT = config_manager.get_default_output_dir()
print("Default output dir:", DEFAULT_OUT)

# Prepare sample input directories
sample_dir = Path(os.path.join(os.path.dirname(__file__), "..", "sample")).resolve()
sample_dir.mkdir(parents=True, exist_ok=True)

# 1) Create mind map using alias fields (topics/subtopics)
print("\n=== create_mind_map ===")
mm_title = "Smoke Test Mind Map"
mm_topics = [
    {
        "title": "Root",
        "topics": [
            {"title": "Child A", "subtopics": [{"title": "A1"}, {"title": "A2"}]},
            {"title": "Child B", "nodes": [{"title": "B1"}]},
        ],
    }
]
res_create = create_mind_map(None, mm_title, json.dumps(mm_topics))
print(res_create)
try:
    res_create_obj = json.loads(res_create)
    created_path = res_create_obj.get("absolute_path") or res_create_obj.get("output_path")
except Exception:
    created_path = None

# 2) Convert markdown to xmind
print("\n=== convert_to_xmind ===")
md_path = sample_dir / "demo.md"
md_path.write_text("# Demo\n\n- Item 1\n- Item 2\n\n## Sub\n- A\n- B\n", encoding="utf-8")
res_convert = convert_to_xmind(None, source_filepath=str(md_path))
print(res_convert)

# 3) List xmind files
print("\n=== list_xmind_files ===")
res_list = list_xmind_files(None, DEFAULT_OUT, True)
print(res_list)

# 4) Read created xmind file (if available)
if created_path and os.path.exists(created_path):
    print("\n=== read_xmind_file ===")
    print(read_xmind_file(None, created_path))
else:
    print("\n=== read_xmind_file skipped (no file) ===")