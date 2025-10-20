# ddoc/cli/main.py
from __future__ import annotations
import typer
from ddoc.cli import commands as core_commands
from ddoc.cli.plugins import app as app_plugins
from ddoc.core.plugins import get_plugin_manager

app = typer.Typer(help="ddoc: data drift doctor")

@app.callback()
def _bootstrap():
    # Initialize plugin manager (builtins + entry points)
    get_plugin_manager()

# ✅ 루트에 core 명령들 병합
core_commands.register(app)

# plugin 관리 서브커맨드는 하위 그룹으로 마운트
app.add_typer(app_plugins, name="plugin")

if __name__ == "__main__":
    app()