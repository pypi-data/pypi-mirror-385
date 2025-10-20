from __future__ import annotations
import json
import typer
from typing import Optional, Any, List
from rich import print
from ddoc.core.plugins import get_plugin_manager

# 플러그인 매니저 인스턴스를 가져옵니다. 
# ddoc/core/plugins.py에서 이 인스턴스가 .hook 속성을 가지도록 보장합니다.
pmgr = get_plugin_manager()

# MLOps Core commands를 위한 서브 Typer 앱 생성
data_app = typer.Typer(help="Data management commands (add, list, checkout)")
exp_app = typer.Typer(help="Experiment management commands (run, show, compare)")

# --- JSON Pretty Print 헬퍼 함수 ---
def _pretty(x: Any) -> str:
    """JSON 또는 객체를 보기 좋게 출력합니다."""
    try:
        # ensure_ascii=False를 사용하여 한글 깨짐 방지
        return json.dumps(x, indent=2, ensure_ascii=False)
    except Exception:
        return str(x)

# ------------------------------------
# A. MLOps Core Commands (data, exp)
# ------------------------------------

@data_app.command("add")
def data_add_command(
    name: str = typer.Argument(..., help="Dataset name (e.g., d1, d2)"),
    config: str = typer.Option(..., help="YOLO config YAML file name (e.g., yolo_d1.yaml)"),
):
    """
    DVC/Git에 새 데이터셋을 등록하고 브랜치를 생성합니다.
    """
    print(f"[bold cyan]Running data add for dataset: {name}[/bold cyan]")
    res = pmgr.hook.data_add(name=name, config=config)
    print(_pretty(res))


@exp_app.command("run")
def exp_run_command(
    name: str = typer.Argument(..., help="Experiment name (e.g., baseline, test-run-1)"),
    params: str = typer.Option("{}", "-p", "--params", help="JSON string of params.yaml updates (e.g., '{\"epochs\": 10, \"batch_size\": 32}')"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run: only show changes without actual DVC run."),
):
    """
    params.yaml을 업데이트하고 DVC 실험을 즉시 실행합니다 (dvc exp run).
    """
    print(f"[bold cyan]Running experiment: {name}[/bold cyan]")
    res = pmgr.hook.exp_run(name=name, params=params, dry_run=dry_run)
    print(_pretty(res))


@exp_app.command("queue")
def exp_queue_command(
    name: str = typer.Argument(..., help="Experiment name (e.g., baseline, test-run-1)"),
    params: str = typer.Option("{}", "-p", "--params", help="JSON string of params.yaml updates (e.g., '{\"epochs\": 10, \"batch_size\": 32}')"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run: only show changes without actual DVC run."),
):
    """
    params.yaml을 업데이트하고 DVC 실험을 큐에 추가합니다 (dvc exp run --queue).
    """
    print(f"[bold cyan]Queueing experiment: {name}[/bold cyan]")
    res = pmgr.hook.exp_queue(name=name, params=params, dry_run=dry_run)
    print(_pretty(res))


@exp_app.command("run-queued")
def exp_run_queued_command():
    """
    DVC 큐에 있는 모든 실험을 실행합니다 (dvc queue start).
    """
    print("[bold cyan]Starting DVC queue execution[/bold cyan]")
    # **kwargs로 빈 딕셔너리를 전달하거나 아무것도 전달하지 않아도 됩니다.
    # ddoc/ops/core_ops.py의 exp_run_queued는 **kwargs를 받습니다.
    res = pmgr.hook.exp_run_queued()
    print(_pretty(res))


@exp_app.command("show")
def exp_show_command(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Specific experiment name/ID to show."),
    baseline: Optional[str] = typer.Option(None, "--baseline", "-b", help="Baseline experiment name/ID for comparison."),
):
    """
    DVC 실험 결과를 조회합니다 (dvc exp show).
    """
    print("Fetching experiment results...")
    try:
        # NOTE: ddoc/core/ops.py is simplified to show all, but we pass args for future use
        print(':::::')
        res = pmgr.hook.exp_show(name=name, baseline=baseline)
        print(_pretty(res))
    except Exception as e:
        print(f"[bold red]❌ Error showing experiments:[/bold red] {e}")


# ------------------------------------
# B. Analytical Commands (via pluggy)
# ------------------------------------

# --- [기존 Analytical Commands 생략] ---
# ... (기존 eda, transform, drift, reconstruct, retrain, monitor 함수 유지)

def eda(
    input: str,
    modality: str = "table",
    out: str = "report.json",
    provider: Optional[str] = None,
):
    """Run EDA via plugins (optionally pick a provider by name)."""
    res = pmgr.hook.eda_run(input_path=input, modality=modality, output_path=out, provider=provider)
    print(_pretty(res))

def transform(
    input: str,
    transform: str,
    args: Optional[str] = None,
    out: str = "out.txt",
    provider: Optional[str] = None,
):
    """Apply transform via plugins."""
    _args = json.loads(args) if args else {}
    res = pmgr.hook.transform_apply(input_path=input, transform=transform, args=_args, output_path=out, provider=provider)
    print(_pretty(res))

def drift(
    ref: str,
    cur: str,
    detector: str = "ks",
    cfg: Optional[str] = None,
    out: str = "drift.json",
    provider: Optional[str] = None,
):
    """Detect drift via plugins."""
    _cfg = json.loads(cfg) if cfg else None
    res = pmgr.hook.drift_detect(ref_path=ref, cur_path=cur, detector=detector, cfg=_cfg, output_path=out, provider=provider)
    print(_pretty(res))

def reconstruct(
    input: str,
    method: str = "drop-empty",
    args: Optional[str] = None,
    out: str = "recon.txt",
    provider: Optional[str] = None,
):
    """Reconstruct data via plugins."""
    _args = json.loads(args) if args else {}
    res = pmgr.hook.reconstruct_apply(input_path=input, method=method, args=_args, output_path=out, provider=provider)
    print(_pretty(res))

def retrain(
    train: str,
    trainer: str = "sklearn",
    params: Optional[str] = None,
    model_out: str = "model.json",
    provider: Optional[str] = None,
):
    """Retrain a model via plugins."""
    _params = json.loads(params) if params else {}
    res = pmgr.hook.retrain_run(train_path=train, trainer=trainer, params=_params, model_out=model_out, provider=provider)
    print(_pretty(res))

def monitor(
    source: str,
    mode: str = "offline",
    schedule: Optional[str] = None,
    provider: Optional[str] = None,
):
    """Run monitors via plugins."""
    res = pmgr.hook.monitor_run(source=source, mode=mode, schedule=schedule, provider=provider)
    print(_pretty(res))

# ------------------------------------
# D. New Plugin Info Command
# ------------------------------------
# Note: typer.command는 Typer 인스턴스에서 가져와야 하므로, 
# Typer 모듈 자체의 .command를 사용하는 대신, register 함수에서 연결합니다.
def plugins_info_command():
    """
    모든 로드된 플러그인의 상세 메타데이터를 (ddoc_get_metadata 훅을 통해) 조회합니다.
    """
    print("[bold magenta]Fetching metadata from all loaded plugins...[/bold magenta]")
    
    # pmgr.hook.ddoc_get_metadata()는 해당 훅을 구현한 모든 플러그인의 결과를 List[Dict]로 반환합니다.
    metadata_list = pmgr.hook.ddoc_get_metadata()
    
    # 결과가 None이거나 비어있으면 처리할 것이 없음
    if not metadata_list:
        print({"status": "No plugins provided metadata via ddoc_get_metadata hook."})
        return
        
    print({"plugins_metadata": metadata_list})

# ------------------------------------
# D. New Plugin Info Command
# ------------------------------------
# Note: typer.command는 Typer 인스턴스에서 가져와야 하므로, 
# Typer 모듈 자체의 .command를 사용하는 대신, register 함수에서 연결합니다.
def plugins_info_command2():
    """
    모든 로드된 플러그인의 상세 메타데이터를 (ddoc_get_metadata2 훅을 통해) 조회합니다.
    """
    print("[bold magenta]Fetching metadata from all loaded plugins...[/bold magenta]")
    
    # pmgr.hook.ddoc_get_metadata()는 해당 훅을 구현한 모든 플러그인의 결과를 List[Dict]로 반환합니다.
    metadata_list = pmgr.hook.ddoc_get_metadata2()
    
    # 결과가 None이거나 비어있으면 처리할 것이 없음
    if not metadata_list:
        print({"status": "No plugins provided metadata via ddoc_get_metadata hook."})
        return
        
    print({"plugins_metadata": metadata_list})
    
# ------------------------------------
# E. Register Function (메인 앱 연결)
# ------------------------------------
def register(app: typer.Typer) -> None:
    """Attach all commands (Core and Analytical) to the given Typer app."""
    
    # 1. MLOps Core commands를 서브 앱으로 마운트 (data, exp)
    app.add_typer(data_app, name="data")
    app.add_typer(exp_app, name="exp")

    # 2. Analytical commands를 루트 명령어로 마운트
    app.command()(eda)
    app.command()(transform)
    app.command()(drift)
    app.command()(reconstruct)
    app.command()(retrain)
    app.command()(monitor)
    
    # 3. 플러그인 메타데이터 정보 명령어 추가 (plugins-info_command 함수를 루트 앱에 연결)
    # add_command 대신 app.command()를 사용하여 연결해야 합니다.
    app.command("plugins-info")(plugins_info_command) 
    app.command("plugins-info2")(plugins_info_command2) 

