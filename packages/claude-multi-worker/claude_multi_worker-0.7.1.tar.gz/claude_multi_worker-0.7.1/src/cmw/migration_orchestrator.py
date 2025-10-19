"""
Migration Orchestration Module

マイグレーション全体を調整するオーケストレーター
Terraform apply + Kubernetes Rolloutを参考に5フェーズで実行
"""

from typing import List, Optional, Dict
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import json
import shutil

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm

from .models import Task, TaskStatus
from .state_reconciler import StateReconciler, StateDiff, DiffAction, DiffActionType
from .dependency_validator import DependencyValidator
from .coordinator import Coordinator
from .task_migrator import TaskMigrator


@dataclass
class ValidationResult:
    """検証結果"""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        """エラーがあるか"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """警告があるか"""
        return len(self.warnings) > 0

    def add_error(self, message: str) -> None:
        """エラー追加"""
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """警告追加"""
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        """情報追加"""
        self.info.append(message)


@dataclass
class MigrationResult:
    """マイグレーション結果"""
    success: bool = False
    cancelled: bool = False
    no_changes: bool = False

    # 統計
    tasks_added: int = 0
    tasks_migrated: int = 0
    tasks_updated: int = 0
    tasks_deprecated: int = 0

    # エラー情報
    error: Optional[str] = None
    backup_id: Optional[str] = None
    restored_from: Optional[str] = None


class MigrationOrchestrator:
    """
    マイグレーション全体を調整するクラス

    5フェーズ実行:
    1. Parse: requirements.mdをパース
    2. Match: 既存タスクとマッチング
    3. Plan: マイグレーション計画作成（差分計算）
    4. Validate: 検証（循環依存、整合性）
    5. Apply: 適用（バックアップ + 更新 + ロールバック）
    """

    def __init__(self, project_path: Path, console: Optional[Console] = None):
        """
        初期化

        Args:
            project_path: プロジェクトのルートパス
            console: Rich Console（Noneの場合は新規作成）
        """
        self.project_path = project_path
        self.console = console or Console()

        self.reconciler = StateReconciler(project_path)
        self.coordinator = Coordinator(project_path)
        self.migrator = TaskMigrator(project_path)
        self.validator = DependencyValidator()

        self.backup_dir = project_path / ".cmw" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def execute_migration(
        self,
        requirements_path: Optional[Path] = None,
        interactive: bool = False,
        auto_approve: bool = False,
        dry_run: bool = False
    ) -> MigrationResult:
        """
        マイグレーションを実行

        Args:
            requirements_path: requirements.mdのパス
            interactive: 対話モード
            auto_approve: 確認なしで適用
            dry_run: 実際には適用しない（plan のみ）

        Returns:
            MigrationResult: マイグレーション結果
        """
        try:
            # === Phase 3: Plan ===
            self.console.print("\n[bold]Phase 1/3:[/bold] マイグレーション計画を作成中...")
            diff = self.reconciler.compute_diff(requirements_path)

            if not diff.has_changes():
                self.console.print("[green]✅ 変更はありません[/green]")
                return MigrationResult(success=True, no_changes=True)

            self._display_diff(diff)

            # === Phase 4: Validate ===
            self.console.print("\n[bold]Phase 2/3:[/bold] 検証中...")
            validation_result = self._validate_diff(diff)
            self._display_validation_result(validation_result)

            if validation_result.has_errors():
                self.console.print("[red]❌ 検証エラー: マイグレーションを中止します[/red]")
                return MigrationResult(success=False, error="Validation failed")

            # Dry-runモード
            if dry_run:
                self.console.print("\n[yellow]--dry-run モード: 実際には適用されません[/yellow]")
                self.console.print("\n適用するには以下のコマンドを実行:")
                self.console.print("  [cyan]cmw task apply[/cyan]")
                return MigrationResult(success=True, no_changes=True)

            # === Phase 5: Apply ===
            if not auto_approve and not interactive:
                if not Confirm.ask("\n[bold]このマイグレーションを適用しますか？[/bold]"):
                    return MigrationResult(success=False, cancelled=True)

            self.console.print("\n[bold]Phase 3/3:[/bold] マイグレーションを適用中...")
            result = self._apply_migration(diff)

            if result.success:
                self.console.print("\n[bold green]✅ マイグレーション完了[/bold green]")
                self._display_migration_summary(result)
            else:
                self.console.print(f"\n[bold red]❌ マイグレーション失敗: {result.error}[/bold red]")

            return result

        except Exception as e:
            self.console.print(f"\n[red]予期しないエラー: {str(e)}[/red]")
            return MigrationResult(success=False, error=str(e))

    def _display_diff(self, diff: StateDiff) -> None:
        """差分を表示（Terraform plan風）"""
        self.console.print()
        self.console.print(Panel(
            diff.summary(),
            title="📋 Reconciliation Plan",
            border_style="cyan"
        ))

        # 追加
        additions = diff.get_additions()
        if additions:
            self.console.print("\n[bold green]Additions (+):[/bold green]")
            for action in additions:
                self.console.print(f"  [green]+[/green] {action.new_task.id}  {action.new_task.title}")

        # マイグレーション
        migrations = diff.get_migrations()
        if migrations:
            self.console.print("\n[bold blue]Migrations (→):[/bold blue]")
            for action in migrations:
                similarity_pct = f"{action.similarity*100:.0f}%"
                self.console.print(
                    f"  [blue]→[/blue] {action.new_task.id}  {action.old_task.title} "
                    f"(similarity: {similarity_pct})"
                )

        # 更新
        updates = diff.get_updates()
        if updates:
            self.console.print("\n[bold yellow]Updates (~):[/bold yellow]")
            for action in updates:
                self.console.print(f"  [yellow]~[/yellow] {action.new_task.id}  {action.reason}")

        # 非推奨化
        deprecations = diff.get_deprecations()
        if deprecations:
            self.console.print("\n[bold red]Deprecations (-):[/bold red]")
            for action in deprecations:
                status_info = f"[{action.old_task.status.value}]"
                self.console.print(
                    f"  [red]-[/red] {action.old_task.id}  {action.old_task.title} {status_info}"
                )

    def _validate_diff(self, diff: StateDiff) -> ValidationResult:
        """
        差分を検証

        検証項目:
        1. 循環依存がないか
        2. 完了済みタスクの依存が変更されていないか
        3. タスクIDの重複がないか
        4. 削除タスクへの依存がないか
        """
        result = ValidationResult()

        # 全タスクリストを構築
        all_tasks = []
        for action in diff.actions:
            if action.action_type in [DiffActionType.MIGRATE, DiffActionType.ADD, DiffActionType.UPDATE]:
                # 新しいタスクを追加
                task = action.new_task

                # マイグレーションの場合、状態を引き継ぐ
                if action.action_type == DiffActionType.MIGRATE and action.old_task:
                    task.status = action.old_task.status
                    task.artifacts = action.old_task.artifacts
                    task.completed_at = action.old_task.completed_at

                all_tasks.append(task)

        # 1. 循環依存チェック
        cycles = self.validator.detect_cycles(all_tasks)
        if cycles:
            for cycle in cycles[:3]:  # 最初の3つのみ表示
                cycle_path = " → ".join([edge[0] for edge in cycle] + [cycle[0][0]])
                result.add_error(f"循環依存が検出されました: {cycle_path}")

        # 2. 完了済みタスクの依存変更チェック
        for action in diff.actions:
            if action.action_type in [DiffActionType.MIGRATE, DiffActionType.UPDATE]:
                old = action.old_task
                new = action.new_task

                if old.status == TaskStatus.COMPLETED:
                    if set(old.dependencies) != set(new.dependencies):
                        result.add_warning(
                            f"{new.id} は完了済みですが、依存関係が変更されます: "
                            f"{old.dependencies} → {new.dependencies}"
                        )

        # 3. タスクID重複チェック
        task_ids = [t.id for t in all_tasks]
        duplicates = [tid for tid in task_ids if task_ids.count(tid) > 1]
        if duplicates:
            result.add_error(f"タスクIDが重複しています: {set(duplicates)}")

        # 4. 削除タスクへの依存チェック
        deprecated_ids = [
            action.old_task.id for action in diff.actions
            if action.action_type == DiffActionType.DEPRECATE
        ]
        for task in all_tasks:
            for dep_id in task.dependencies:
                if dep_id in deprecated_ids:
                    result.add_error(
                        f"{task.id} は削除予定の {dep_id} に依存しています"
                    )

        # 5. 新規タスク→完了済みタスクへの依存（情報のみ）
        for action in diff.actions:
            if action.action_type == DiffActionType.ADD:
                new_task = action.new_task
                for dep_id in new_task.dependencies:
                    dep_task = next((t for t in all_tasks if t.id == dep_id), None)
                    if dep_task and dep_task.status == TaskStatus.COMPLETED:
                        result.add_info(
                            f"{new_task.id} は完了済みの {dep_id} に依存します（正常）"
                        )

        return result

    def _display_validation_result(self, result: ValidationResult) -> None:
        """検証結果を表示"""
        if result.has_errors():
            self.console.print("\n[bold red]❌ エラー:[/bold red]")
            for error in result.errors:
                self.console.print(f"  • {error}")

        if result.has_warnings():
            self.console.print("\n[bold yellow]⚠️  警告:[/bold yellow]")
            for warning in result.warnings:
                self.console.print(f"  • {warning}")

        if result.info:
            self.console.print("\n[bold cyan]ℹ️  情報:[/bold cyan]")
            for info in result.info:
                self.console.print(f"  • {info}")

        if not result.has_errors() and not result.has_warnings():
            self.console.print("[green]✅ 検証に成功しました[/green]")

    def _apply_migration(self, diff: StateDiff) -> MigrationResult:
        """
        マイグレーションを適用

        手順:
        1. バックアップ作成
        2. tasks.json更新
        3. progress.json更新
        4. エラー時ロールバック
        """
        result = MigrationResult()

        # 1. バックアップ作成
        backup_id = self._create_backup()
        result.backup_id = backup_id

        try:
            # 2. tasks.jsonを更新
            new_tasks = []
            for action in diff.actions:
                if action.action_type in [DiffActionType.MIGRATE, DiffActionType.ADD, DiffActionType.UPDATE]:
                    new_tasks.append(action.new_task)

            self._write_tasks_json(new_tasks)

            # 3. progress.jsonを更新
            for action in diff.actions:
                if action.action_type == DiffActionType.MIGRATE:
                    # 状態を引き継ぎ
                    self._update_progress(
                        task_id=action.new_task.id,
                        old_task=action.old_task
                    )
                    result.tasks_migrated += 1

                elif action.action_type == DiffActionType.ADD:
                    # 新規タスクのprogress追加
                    self._create_progress_entry(action.new_task)
                    result.tasks_added += 1

                elif action.action_type == DiffActionType.UPDATE:
                    # 更新（状態も引き継ぎ）
                    self._update_progress(
                        task_id=action.new_task.id,
                        old_task=action.old_task
                    )
                    result.tasks_updated += 1

                elif action.action_type == DiffActionType.DEPRECATE:
                    # deprecated状態に変更
                    self._mark_as_deprecated(action.old_task.id)
                    result.tasks_deprecated += 1

            result.success = True

        except Exception as e:
            # ロールバック
            self.console.print(f"[red]エラー発生: {e}[/red]")
            self.console.print("[yellow]バックアップから復元中...[/yellow]")
            self._restore_from_backup(backup_id)
            result.success = False
            result.error = str(e)
            result.restored_from = backup_id

        return result

    def _create_backup(self) -> str:
        """
        バックアップを作成

        Returns:
            str: バックアップID（タイムスタンプ）
        """
        backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(parents=True, exist_ok=True)

        # tasks.jsonとprogress.jsonをコピー
        tasks_file = self.project_path / "shared" / "coordination" / "tasks.json"
        progress_file = self.project_path / "shared" / "coordination" / "progress.json"

        if tasks_file.exists():
            shutil.copy2(tasks_file, backup_path / "tasks.json")
        if progress_file.exists():
            shutil.copy2(progress_file, backup_path / "progress.json")

        return backup_id

    def _restore_from_backup(self, backup_id: str) -> None:
        """バックアップから復元"""
        backup_path = self.backup_dir / backup_id

        tasks_backup = backup_path / "tasks.json"
        progress_backup = backup_path / "progress.json"

        tasks_file = self.project_path / "shared" / "coordination" / "tasks.json"
        progress_file = self.project_path / "shared" / "coordination" / "progress.json"

        if tasks_backup.exists():
            shutil.copy2(tasks_backup, tasks_file)
        if progress_backup.exists():
            shutil.copy2(progress_backup, progress_file)

    def _write_tasks_json(self, tasks: List[Task]) -> None:
        """tasks.jsonを書き込み"""
        tasks_file = self.project_path / "shared" / "coordination" / "tasks.json"
        tasks_file.parent.mkdir(parents=True, exist_ok=True)

        tasks_data = {
            "tasks": [t.to_dict() for t in tasks],
            "workers": []
        }

        tasks_file.write_text(
            json.dumps(tasks_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def _update_progress(self, task_id: str, old_task: Task) -> None:
        """progress.jsonを更新（状態引き継ぎ）"""
        progress_file = self.project_path / "shared" / "coordination" / "progress.json"

        if not progress_file.exists():
            progress_data = {"tasks": []}
        else:
            progress_data = json.loads(progress_file.read_text(encoding="utf-8"))

        # 既存のprogressを探す
        task_progress = None
        for t in progress_data.get("tasks", []):
            if t["id"] == old_task.id or t["id"] == task_id:
                task_progress = t
                break

        if task_progress:
            # 更新
            task_progress["id"] = task_id
            task_progress["status"] = old_task.status.value
            task_progress["artifacts"] = old_task.artifacts
            if old_task.completed_at:
                task_progress["completed_at"] = old_task.completed_at.isoformat()
            if old_task.started_at:
                task_progress["started_at"] = old_task.started_at.isoformat()
        else:
            # 新規追加（状態コピー）
            task_dict = old_task.to_dict()
            task_dict["id"] = task_id
            progress_data.setdefault("tasks", []).append(task_dict)

        progress_file.write_text(
            json.dumps(progress_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def _create_progress_entry(self, task: Task) -> None:
        """新規タスクのprogressエントリ作成"""
        progress_file = self.project_path / "shared" / "coordination" / "progress.json"

        if not progress_file.exists():
            progress_data = {"tasks": []}
        else:
            progress_data = json.loads(progress_file.read_text(encoding="utf-8"))

        progress_data.setdefault("tasks", []).append(task.to_dict())

        progress_file.write_text(
            json.dumps(progress_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def _mark_as_deprecated(self, task_id: str) -> None:
        """タスクをdeprecatedにマーク"""
        # 現時点では単純に削除（将来的にはDEPRECATEDステータスを追加）
        pass

    def _display_migration_summary(self, result: MigrationResult) -> None:
        """マイグレーション結果のサマリーを表示"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("項目", style="cyan")
        table.add_column("数", justify="right")

        table.add_row("追加されたタスク", str(result.tasks_added))
        table.add_row("マイグレーションされたタスク", str(result.tasks_migrated))
        table.add_row("更新されたタスク", str(result.tasks_updated))
        table.add_row("非推奨化されたタスク", str(result.tasks_deprecated))

        if result.backup_id:
            table.add_row("バックアップID", result.backup_id)

        self.console.print(table)
