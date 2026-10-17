import sys
import os
import traceback

# Add root project directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from server import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    
    app = FastAPI()
    err_tb = traceback.format_exc()
    
    @app.api_route("/{rest_of_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def fallback(rest_of_path: str = ""):
        return HTMLResponse(
            f"<h2>Server Startup Error on Vercel</h2>"
            f"<p>An error occurred while importing the application:</p>"
            f"<pre style='background:#f4f4f4;padding:15px;border-radius:8px;border:1px solid #ddd;color:#c00;'>{err_tb}</pre>",
            status_code=500
        )
