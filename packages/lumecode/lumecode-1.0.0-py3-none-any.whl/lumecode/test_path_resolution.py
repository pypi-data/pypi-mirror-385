from pathlib import Path
import os

# Check the path resolution
router_path = os.path.join('backend', 'api', 'routers', 'cli.py')
project_root = str(Path(router_path).parent.parent.parent)
print(f"Project root from script: {project_root}")

# Check absolute path for the docs file
test_path = 'backend/docs/generator.py'
absolute_path = os.path.join(project_root, test_path)
print(f"Absolute path for docs file: {absolute_path}")
print(f"Path exists: {os.path.exists(absolute_path)}")