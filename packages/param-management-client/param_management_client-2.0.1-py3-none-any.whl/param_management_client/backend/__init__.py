"""
内置后端包入口。
提供便捷启动函数 run_embedded_server 以在客户端包内直接启动后端。
"""

from .main import app as backend_app

def run_embedded_server(host: str = "0.0.0.0", port: int = 8000):
    """在进程内启动内置后端 FastAPI 服务器（Uvicorn）。"""
    import uvicorn
    uvicorn.run(backend_app, host=host, port=port)

__all__ = ["backend_app", "run_embedded_server"]


