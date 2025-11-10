import uvicorn
import os
import sys

project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiki.settings')

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=7000,
        reload=True
    )

    