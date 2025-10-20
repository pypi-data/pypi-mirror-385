import subprocess
from typing import Any, Dict, Optional
import os
import json 

from rich import print
from ddoc.plugins.hookspecs import hookimpl
from ddoc.utils import read_yaml_file, write_yaml_file, get_dvc_status


class CoreOpsPlugin:
    """
    ddoc의 핵심 MLOps 명령을 구현하는 플러그인입니다.
    DVC 및 Git을 사용하여 데이터셋 등록 및 실험 실행을 관리합니다.
    """
    def __init__(self):
        # 예시로 사용할 앱 ID 설정
        self.app_id = "ddoc" 
        # 작업 디렉토리 설정
        self.data_dir = "data"

    # =========================================================================
    # 명령어 래퍼 함수 
    # =========================================================================
    
    def _run_cmd(self, cmd: list[str], log_msg: str) -> Dict[str, Any]:
        """쉘 명령어를 실행하는 헬퍼 함수."""
        print(f"[bold cyan]⚙️ {log_msg}:[/bold cyan] {' '.join(cmd)}")
        try:
            # check=True: 명령 실행 실패 시 CalledProcessError 발생
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
            return {"ok": True, "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.strip() or e.stdout.strip()
            # 오류 메시지를 포함하여 다시 예외를 발생시켜 호출자에게 전달
            raise Exception(f"{log_msg} 실패: {error_output}")
        except FileNotFoundError:
            raise Exception(f"필요한 명령어({cmd[0]})를 찾을 수 없습니다. (Git 또는 DVC 설치 확인)")

    def _run_git_command(self, args: list[str], description: str) -> Dict[str, Any]:
        """Git 명령어 실행 래퍼"""
        return self._run_cmd(["git"] + args, description)

    def _run_dvc_command(self, args: list[str], description: str) -> Dict[str, Any]:
        """DVC 명령어 실행 래퍼"""
        return self._run_cmd(["dvc"] + args, description)

    # =========================================================================
    # 헬퍼 함수
    # =========================================================================

    def _update_and_stage_params(self, params: str) -> Optional[Dict[str, Any]]:
        """params.yaml을 업데이트하고 Git에 스테이징하는 공통 로직."""
        try:
            updates = json.loads(params) 
        except json.JSONDecodeError:
            return {"error": "파라미터 업데이트 실패: 'params' 인자가 유효한 JSON 형식이 아닙니다."}
        
        # 🌟 핵심 수정: write_yaml_file 호출을 주석 해제하여 실제로 파일을 업데이트합니다.
        # read_yaml_file로 기존 내용을 읽고 업데이트한 후 저장하는 로직이 필요합니다.
        try:
            # 1. params.yaml 로드 (없으면 빈 딕셔너리로 시작)
            current_params = read_yaml_file("params.yaml") if os.path.exists("params.yaml") else {}
            # 2. 업데이트 병합
            current_params.update(updates)
            # 3. 저장
            write_yaml_file("params.yaml", current_params)
            print(f"[bold green]✔️ Config Update:[/bold green] params.yaml updated with {updates}")
        except Exception as e:
            return {"error": f"params.yaml 파일 쓰기 실패: {e}"}

        # 🌟 Git 스테이징 시 오류 처리 추가
        try:
            self._run_git_command(["add", "params.yaml"], "Git 스테이징: params.yaml")
        except Exception as e:
             # Git 명령 실패 시 오류를 반환
            return {"error": f"params.yaml Git 스테이징 실패: {e}"}
        
        return {"success": True}

    # =========================================================================
    # Hook Implementations
    # =========================================================================

    @hookimpl
    def data_add(self, name: str, config: str) -> Optional[Dict[str, Any]]:
        """Registers a new dataset version (dvc add, git branch/commit, params update)."""
        data_path = f"data/{name}"
        yolo_config_path = f"{data_path}/data.yaml"
        branch_name = f"feature/dataset_{name}"

        if not os.path.exists(data_path):
             return {"error": f"데이터셋 경로 '{data_path}'를 찾을 수 없습니다. 경로를 확인해주세요."}

        
        # 1. 새 브랜치 생성 및 체크아웃 (멱등성 확보 로직 추가)
        try:
            # 1-a. 새 브랜치 생성 및 체크아웃 시도
            self._run_cmd(
                ["git", "checkout", "-b", branch_name],
                f"Git 브랜치 {branch_name} 생성"
            )
            print(f"[bold green]✅ 새 브랜치 '{branch_name}' 생성 및 체크아웃 완료.[/bold green]")
        except Exception as e:
            # 브랜치 이미 존재 오류 처리 (Git 에러 메시지에 'already exists' 포함)
            if "already exists" in str(e):
                # 1-b. 브랜치가 이미 존재하는 경우, 체크아웃만 수행
                self._run_cmd(
                    ["git", "checkout", branch_name],
                    f"Git 브랜치 {branch_name} 체크아웃 (이미 존재)"
                )
                print(f"[bold yellow]⚠️ 브랜치 '{branch_name}'이(가) 이미 존재합니다. 체크아웃만 수행합니다.[/bold yellow]")
            else:
                # 예상치 못한 Git 오류 발생 시, 재발생
                return {"error": f"Git 브랜치 처리 중 오류: {e}"}
            
        # 2. params.yaml 업데이트
        param_updates = {
            "dataset": {
                "name": name,
                "path": data_path,
                "config": config,
                "yolo_config": yolo_config_path
            }
        }
        
        write_yaml_file("params.yaml", param_updates)
        print(f"[bold green]✅ params.yaml 업데이트 완료. dataset: {name}[/bold green]")
        
        # 3. DVC 추적 및 Git 커밋
        try:
            # DVC로 데이터 폴더 추적 (data/{name} 폴더)
            self._run_dvc_command(
                ["add", data_path],
                f"DVC add {data_path}"
            )

            # ⚙️ Git 스테이징: git add params.yaml data/d2.dvc .gitignore
            # data/.gitignore는 DVC add가 실행된 디렉토리 내부에 생성될 수 있으므로,
            # os.path.exists()를 사용하지 않고 포함합니다. 실패 시 Git이 에러 처리합니다.
            
            # NOTE: 이전 피드백에 따라, 존재하지 않는 파일에 대한 fatal 오류를 방지하기 위해 
            # '.gitignore' 및 'data/.gitignore' 파일이 실제로 존재하는 경우에만 스테이징에 포함하는 것이 좋습니다.
            files_to_stage = ["params.yaml", f"{data_path}.dvc"]

            if os.path.exists(".gitignore"):
                 files_to_stage.append(".gitignore")
            
            nested_gitignore_path = os.path.join("data", ".gitignore")
            if os.path.exists(nested_gitignore_path):
                 files_to_stage.append(nested_gitignore_path)

            self._run_git_command(
                ["add"] + files_to_stage,
                "Git staging"
            )
            
            # Git 커밋
            self._run_git_command(
                ["commit", "-m", f"ddoc: Add dataset {name} v1 (config: {config})"],
                "Git commit"
            )

            # DVC Push (원격 저장소에 데이터 업로드)
            self._run_dvc_command(
                ["push", "-R", data_path],
                f"DVC 데이터셋 {name} 푸시"
            )

            return {
                "success": True, 
                "message": f"데이터셋 '{name}'이(가) 브랜치 '{branch_name}'에 성공적으로 등록되었습니다.",
                "branch": branch_name
            }

        except Exception as e:
            return {"error": f"DVC/Git 작업 중 중단됨: {e}"}


    @hookimpl
    def exp_run(self, name: str, params: str, dry_run: bool) -> Optional[Dict[str, Any]]:
        """Updates params.yaml and executes dvc exp run immediately (no queue)."""
        
        prep_result = self._update_and_stage_params(params)
        if "error" in prep_result:
            return prep_result
        
        try:
            cmd_args = ["exp", "run"]
            
            if name:
                cmd_args.extend(["--name", name])
            if dry_run:
                cmd_args.append("--dry")
                action_msg = "DVC 실험 Dry Run 실행"
                print("[bold yellow]⚠️ Dry Run 모드로 실행합니다. 실제 실험은 실행되지 않습니다.[/bold yellow]")
            else:
                action_msg = "DVC 실험 즉시 실행"
                print("[bold green]✅ 실험이 즉시 실행됩니다.[/bold green]")
            
            run_result = self._run_dvc_command(cmd_args, action_msg)
            
            return {"success": True, "message": f"실험 '{name or '자동'}' 실행 요청 완료.", "output": run_result.get('stdout', '')}

        except Exception as e:
            # _run_dvc_command에서 발생한 예외를 포착
            return {"error": f"DVC 실험 실행 중 오류: {e}"}

    @hookimpl
    def exp_queue(self, name: str, params: str, dry_run: bool) -> Optional[Dict[str, Any]]:
        """Updates params.yaml and executes dvc exp run with --queue."""

        prep_result = self._update_and_stage_params(params)
        if "error" in prep_result:
            return prep_result
        
        try:
            cmd_args = ["exp", "run", "--queue"]
            
            if name:
                cmd_args.extend(["--name", name])
            
            if dry_run:
                 cmd_args.append("--dry")
                 print("[bold yellow]⚠️ 큐 추가 시 Dry Run은 DVC에 의해 무시될 수 있습니다.[/bold yellow]")

            action_msg = "DVC 실험 큐에 추가"
            print("[bold green]✅ 실험이 DVC 실험 큐에 추가되었습니다.[/bold green]")
            
            run_result = self._run_dvc_command(cmd_args, action_msg)
            
            return {"success": True, "message": f"실험 '{name or '자동'}'이(가) DVC 실험 큐에 성공적으로 추가되었습니다.", "output": run_result.get('stdout', '')}

        except Exception as e:
            # _run_dvc_command에서 발생한 예외를 포착
            return {"error": f"DVC 실험 큐 추가 중 오류: {e}"}

    @hookimpl
    def exp_run_queued(self, **kwargs) -> Optional[Dict[str, Any]]:
        """DVC 큐에 있는 모든 실험을 실행합니다. (dvc queue start)"""
        
        try:
            print("[bold magenta]🚀 DVC 큐 실행 시작:[/bold magenta] 큐에 있는 모든 실험을 순차적으로 실행합니다.")
            
            # dvc queue start 명령 실행
            run_result = self._run_dvc_command(["queue", "start"], "DVC 큐 실행 시작")
            
            return {
                "success": True,
                "message": "DVC 큐에 있는 실험들의 실행이 시작되었습니다.",
                "output": run_result.get('stdout', '')
            }

        except Exception as e:
            return {"error": f"DVC 큐 실행 중 오류: {e}"}

    
    @hookimpl
    def exp_show(self, name: Optional[str], baseline: Optional[str]) -> Optional[Dict[str, Any]]:
        """Shows DVC experiment results, optionally comparing two versions."""

        print('::: exp_show :::')

        try:
            if baseline:
                # baseline이 제공되면 dvc exp diff로 두 버전을 비교합니다.
                diff_args = ["exp", "diff"]
                target1 = name or "HEAD"
                target2 = baseline
                diff_args.extend([target1, target2])
                print(f"[bold magenta]🔬 DVC 실험 비교:[/bold magenta] {target1} vs {target2}")
                show_result = self._run_dvc_command(diff_args, f"DVC 실험 비교 ({target1} vs {target2})")
                
                return {
                    "success": True,
                    "message": f"'{target1}'과(와) '{target2}' 실험 비교 결과입니다.",
                    "output": show_result.get("stdout")
                }

            else:
                # baseline이 없으면 dvc exp show로 전체 결과를 보여줍니다.
                show_args = ["exp", "show", "--no-pager"]
                print("[bold magenta]🔬 DVC 실험 결과:[/bold magenta] 전체 실험 목록 및 메트릭")
                show_result = self._run_dvc_command(show_args, "DVC 실험 결과 보기")

                return {
                    "success": True,
                    "message": "DVC 실험 결과 목록입니다.",
                    "output": show_result.get("stdout")
                }

        except Exception as e:
            return {"error": f"DVC 실험 결과 보기 중 오류: {e}"}