"""
コマンドラインインターフェース (CLI)

cmw コマンドの実装
"""

import json
import click
from pathlib import Path
from typing import Optional, Dict

from . import __version__
from .models import TaskStatus, Task, Priority
from .coordinator import Coordinator
from .requirements_parser import RequirementsParser
from .conflict_detector import ConflictDetector
from .progress_tracker import ProgressTracker
from .dashboard import Dashboard
from .dependency_validator import DependencyValidator
from .task_filter import TaskFilter
from .git_integration import GitIntegration


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    f"""Claude Multi-Worker Framework - マルチワーカー開発フレームワーク v{__version__}"""
    pass


@cli.command()
@click.argument("name", required=False)
def init(name: Optional[str]) -> None:
    """新しいプロジェクトを初期化

    NAME: プロジェクト名（省略時はカレントディレクトリ名を使用）

    例:
      cmw init my-project  # my-project/ディレクトリを作成して初期化
      cmw init             # カレントディレクトリで初期化
    """
    # nameが指定されていない場合、カレントディレクトリを使用
    if name is None:
        project_path = Path.cwd()
        name = project_path.name

        # カレントディレクトリが既にcmwプロジェクトか確認
        if (project_path / "shared" / "coordination").exists():
            click.echo("❌ エラー: このディレクトリは既にcmwプロジェクトです", err=True)
            return

        # カレントディレクトリが空でない場合は警告
        if list(project_path.iterdir()):
            if not click.confirm("⚠️  カレントディレクトリは空ではありません。続けますか？"):
                return
    else:
        # nameが指定された場合、サブディレクトリを作成
        project_path = Path.cwd() / name

        if project_path.exists():
            click.echo(f"❌ エラー: ディレクトリ {name} は既に存在します", err=True)
            return

    # ディレクトリ構造を作成
    dirs = [
        "shared/docs",
        "shared/coordination",
        "shared/artifacts/backend/core",
        "shared/artifacts/frontend",
        "shared/artifacts/tests",
    ]

    for dir_path in dirs:
        (project_path / dir_path).mkdir(parents=True, exist_ok=True)

    # サンプルファイルを作成
    requirements_file = project_path / "shared" / "docs" / "requirements.md"
    requirements_file.write_text(
        """# プロジェクト要件書

## 概要
このプロジェクトの概要を記載してください。

## 機能要件
### 機能1:
### 機能2:

## 非機能要件
- パフォーマンス:
- セキュリティ:
""",
        encoding="utf-8",
    )

    click.echo(f"✅ プロジェクト '{name}' を初期化しました")
    click.echo("\n次のステップ:")
    if name != project_path.name:
        click.echo(f"  1. cd {name}")
        click.echo("  2. shared/docs/requirements.md を編集")
    else:
        click.echo("  1. shared/docs/requirements.md を編集")
    click.echo("  3. cmw task generate でタスク自動生成")
    click.echo("  4. cmw status でプロジェクト状況を確認")


@cli.group(name="task")
def task() -> None:
    """タスク管理コマンド"""
    pass


# 後方互換性のため tasks も残す（非推奨）
@cli.group(name="tasks", hidden=True)
def tasks() -> None:
    """[非推奨] 'cmw task' を使用してください"""
    pass


@task.command("generate")
@click.option(
    "--requirements", "-r", default="shared/docs/requirements.md", help="requirements.mdのパス"
)
@click.option(
    "--output", "-o", default="shared/coordination/tasks.json", help="出力先のtasks.jsonパス"
)
@click.option("--force", "-f", is_flag=True, help="既存のtasks.jsonを上書き")
@click.option("--migrate", is_flag=True, help="既存タスクの状態を新タスクにマイグレーション")
def generate_tasks(requirements: str, output: str, force: bool, migrate: bool) -> None:
    """requirements.mdからタスクを自動生成

    examples:
        cmw task generate
        cmw task generate -r docs/requirements.md
        cmw task generate --force
        cmw task generate --migrate  # 既存タスクの状態を引き継ぐ (推奨: cmw task apply を使用)

    注意:
        --migrateオプションは後方互換性のために残されています。
        新しいプロジェクトでは `cmw task plan` と `cmw task apply` の使用を推奨します。
    """
    from rich.console import Console

    project_path = Path.cwd()
    requirements_path = project_path / requirements
    output_path = project_path / output

    if not _validate_requirements_exists(requirements_path):
        return

    console = Console()

    # マイグレーションモードの場合は新しいMigrationOrchestratorを使用
    if migrate and output_path.exists():
        console.print("\n[yellow]ℹ️  --migrateオプションは非推奨です。代わりに以下を使用してください:[/yellow]")
        console.print("  1. [cyan]cmw task plan[/cyan]  - 変更内容をプレビュー")
        console.print("  2. [cyan]cmw task apply[/cyan] - 変更を適用\n")

        from .migration_orchestrator import MigrationOrchestrator

        orchestrator = MigrationOrchestrator(project_path, console=console)

        try:
            result = orchestrator.execute_migration(
                requirements_path=requirements_path,
                auto_approve=True  # generateコマンドは確認なしで実行
            )

            if not result.success and not result.cancelled and not result.no_changes:
                import sys
                sys.exit(1)

        except Exception as e:
            console.print(f"\n[red]❌ エラー: {str(e)}[/red]")
            import traceback
            traceback.print_exc()
            import sys
            sys.exit(1)

        return

    # マイグレーションなしの場合は従来通り
    elif not migrate and output_path.exists() and not force:
        if not _confirm_overwrite(output_path, output, force):
            return

    try:
        tasks = _parse_requirements(requirements_path, requirements)
        _save_tasks_to_file(tasks, output_path, output)
        _print_task_summary(tasks)
    except FileNotFoundError as e:
        click.echo(f"❌ エラー: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"❌ タスク生成エラー: {str(e)}", err=True)
        import traceback

        traceback.print_exc()


def _validate_requirements_exists(requirements_path: Path) -> bool:
    """requirements.mdの存在確認"""
    if requirements_path.exists():
        return True

    click.echo(f"❌ エラー: requirements.md が見つかりません: {requirements_path}", err=True)
    click.echo("\n次のステップ:")
    click.echo(f"  1. {requirements_path} を作成")
    click.echo("  2. プロジェクト要件を記載")
    click.echo("  3. cmw task generate を再実行")
    return False


def _confirm_overwrite(output_path: Path, output: str, force: bool) -> bool:
    """出力先の上書き確認"""
    if not output_path.exists() or force:
        return True

    click.echo(f"⚠️  {output} は既に存在します")
    if click.confirm("上書きしますか?"):
        return True

    click.echo("キャンセルしました")
    return False


def _parse_requirements(requirements_path: Path, requirements: str) -> list:
    """requirements.mdを解析してタスクを生成"""
    click.echo(f"\n📄 {requirements} を解析中...")
    parser = RequirementsParser()
    tasks = parser.parse(requirements_path)
    click.echo(f"✅ {len(tasks)} 個のタスクを生成しました\n")
    return tasks


def _save_tasks_to_file(tasks: list, output_path: Path, output: str) -> None:
    """タスクをJSONファイルに保存"""
    tasks_data = {
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "assigned_to": task.assigned_to,
                "dependencies": task.dependencies,
                "target_files": task.target_files,
                "acceptance_criteria": task.acceptance_criteria,
                "priority": task.priority,
            }
            for task in tasks
        ],
        "workers": [],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(tasks_data, ensure_ascii=False, indent=2), encoding="utf-8")
    click.echo(f"💾 {output} に保存しました")


def _print_task_summary(tasks: list) -> None:
    """タスクサマリーを表示"""
    click.echo(f"\n{'=' * 80}")
    click.echo("生成されたタスクのサマリー")
    click.echo(f"{'=' * 80}\n")

    _print_priority_summary(tasks)
    _print_assignment_summary(tasks)
    _print_next_steps()


def _print_priority_summary(tasks: list) -> None:
    """優先度別サマリーを表示"""
    priority_counts = {"high": 0, "medium": 0, "low": 0}
    for task in tasks:
        priority_counts[task.priority] = priority_counts.get(task.priority, 0) + 1

    click.echo(f"総タスク数: {len(tasks)}")
    click.echo(f"  🔴 高優先度: {priority_counts['high']}")
    click.echo(f"  🟡 中優先度: {priority_counts['medium']}")
    click.echo(f"  🟢 低優先度: {priority_counts['low']}")


def _print_assignment_summary(tasks: list) -> None:
    """担当別サマリーを表示"""
    assigned_to_counts: Dict[str, int] = {}
    for task in tasks:
        assigned_to_counts[task.assigned_to] = assigned_to_counts.get(task.assigned_to, 0) + 1

    click.echo("\n担当別:")
    for assigned_to, count in sorted(assigned_to_counts.items()):
        click.echo(f"  {assigned_to}: {count}タスク")


def _print_next_steps() -> None:
    """次のステップを表示"""
    click.echo("\n次のステップ:")
    click.echo("  1. タスク一覧を確認: cmw task list")
    click.echo("  2. プロジェクト状況を確認: cmw status")


@task.command("list")
@click.option(
    "--status",
    type=click.Choice(["pending", "in_progress", "completed", "failed", "blocked"]),
    help="ステータスでフィルタ",
)
def list_tasks(status: Optional[str]) -> None:
    """タスク一覧を表示"""
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    if not coordinator.tasks:
        click.echo("タスクが見つかりません。'cmw task generate' を実行してください。")
        return

    # フィルタリング
    from typing import Iterable

    tasks_to_show: Iterable = coordinator.tasks.values()
    if status:
        tasks_to_show = [t for t in tasks_to_show if t.status.value == status]

    click.echo(f"\n{'=' * 80}")
    click.echo(f"タスク一覧 ({len(list(tasks_to_show))} 件)")
    click.echo(f"{'=' * 80}\n")

    for task in tasks_to_show:
        status_emoji = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.BLOCKED: "🚫",
        }

        emoji = status_emoji.get(task.status, "❓")
        click.echo(f"{emoji} {task.id}: {task.title}")
        click.echo(f"   ステータス: {task.status.value}")
        click.echo(f"   担当: {task.assigned_to}")
        if task.dependencies:
            click.echo(f"   依存: {', '.join(task.dependencies)}")
        click.echo()


@task.command("show")
@click.argument("task_id")
def show_task(task_id: str) -> None:
    """タスクの詳細を表示"""
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    task = coordinator.get_task(task_id)
    if not task:
        click.echo(f"❌ タスク {task_id} が見つかりません", err=True)
        return

    click.echo(f"\n{'=' * 80}")
    click.echo(f"タスク詳細: {task.id}")
    click.echo(f"{'=' * 80}\n")

    click.echo(f"タイトル: {task.title}")
    click.echo(f"説明: {task.description}")
    click.echo(f"ステータス: {task.status.value}")
    click.echo(f"優先度: {task.priority.value}")
    click.echo(f"担当ワーカー: {task.assigned_to}")

    if task.dependencies:
        click.echo(f"依存タスク: {', '.join(task.dependencies)}")

    if task.artifacts:
        click.echo("\n生成されたファイル:")
        for artifact in task.artifacts:
            click.echo(f"  - {artifact}")

    if task.error_message:
        click.echo(f"\nエラー: {task.error_message}")


@task.command("analyze")
@click.option("--show-order", is_flag=True, help="推奨実行順序も表示")
def analyze_conflicts(show_order: bool) -> None:
    """タスク間のファイル競合を分析

    examples:
        cmw task analyze
        cmw task analyze --show-order
    """
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    if not coordinator.tasks:
        click.echo("タスクが見つかりません。'cmw task generate' を実行してください。")
        return

    # ConflictDetectorで分析
    detector = ConflictDetector()
    tasks_list = list(coordinator.tasks.values())

    # 競合レポートを生成
    report = detector.get_conflict_report(tasks_list)
    click.echo(report)

    # ファイル使用状況
    click.echo(f"\n{'=' * 80}")
    click.echo("ファイル使用状況")
    click.echo(f"{'=' * 80}\n")

    file_usage = detector.analyze_file_usage(tasks_list)

    # リスクレベル順にソート
    risk_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    sorted_files = sorted(
        file_usage.items(),
        key=lambda x: (risk_order.get(x[1]["risk_level"], 0), len(x[1]["tasks"])),
        reverse=True,
    )

    for file, usage in sorted_files:
        risk_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        icon = risk_icon.get(usage["risk_level"], "⚪")

        click.echo(f"{icon} {file}")
        click.echo(f"   リスクレベル: {usage['risk_level']}")
        click.echo(f"   関連タスク ({len(usage['tasks'])}件): {', '.join(usage['tasks'])}")
        click.echo()


@task.command("validate")
@click.option("--fix", is_flag=True, help="検出された問題を自動修正")
@click.option(
    "--tasks-file", default="shared/coordination/tasks.json", help="検証するtasks.jsonのパス"
)
def validate_tasks(fix: bool, tasks_file: str) -> None:
    """タスクの品質を検証

    循環依存、非タスク項目、依存関係の妥当性をチェックします。

    examples:
        cmw task validate
        cmw task validate --fix
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    project_path = Path.cwd()
    tasks_path = project_path / tasks_file

    if not tasks_path.exists():
        console.print(f"[red]❌ エラー: {tasks_file} が見つかりません[/red]")
        console.print("\n次のステップ:")
        console.print("  1. cmw task generate でタスクを生成")
        console.print("  2. cmw task validate で検証")
        return

    # タスクを読み込み
    tasks_data = json.loads(tasks_path.read_text(encoding="utf-8"))
    tasks_list = []

    for task_data in tasks_data.get("tasks", []):
        from .models import Task, Priority

        task = Task(
            id=task_data["id"],
            title=task_data["title"],
            description=task_data.get("description", ""),
            assigned_to=task_data.get("assigned_to", "unknown"),
            dependencies=task_data.get("dependencies", []),
            target_files=task_data.get("target_files", []),
            acceptance_criteria=task_data.get("acceptance_criteria", []),
            priority=Priority(task_data.get("priority", "medium")),
        )
        tasks_list.append(task)

    # 検証を実行
    validator = DependencyValidator()
    task_filter = TaskFilter()

    console.print(Panel.fit("🔍 タスクの品質を検証中...", border_style="blue"))

    # 1. 循環依存チェック
    console.print("\n[bold cyan]1. 循環依存チェック[/bold cyan]")
    cycles = validator.detect_cycles(tasks_list)

    if cycles:
        console.print(f"[yellow]⚠️  {len(cycles)}件の循環依存を検出しました:[/yellow]\n")

        for i, cycle in enumerate(cycles, 1):
            # cycleはエッジのリスト [(from, to), ...]
            # 表示用にノードのリストに変換
            cycle_nodes = [edge[0] for edge in cycle]
            cycle_str = " → ".join(cycle_nodes) + f" → {cycle_nodes[0]}"
            console.print(f"  {i}. {cycle_str}")

        if fix:
            console.print("\n[blue]🔧 自動修正を適用中...[/blue]")
            suggestions = validator.suggest_fixes(cycles, tasks_list)

            # 修正提案を表示
            removed_deps = []
            for suggestion in suggestions:
                # suggestion['cycle']はエッジのリスト
                cycle_edges = suggestion['cycle']
                cycle_nodes = [edge[0] for edge in cycle_edges]
                console.print(f"\n循環: {' ↔ '.join(cycle_nodes)}")
                for fix_suggestion in suggestion["suggestions"][:1]:  # 最も信頼度の高い提案のみ
                    console.print(
                        f"  ✓ {fix_suggestion['from_task']} → {fix_suggestion['to_task']} を削除"
                    )
                    console.print(f"    理由: {fix_suggestion['reason']}")
                    console.print(f"    信頼度: {fix_suggestion['confidence'] * 100:.0f}%")
                    removed_deps.append(
                        (fix_suggestion['from_task'], fix_suggestion['to_task'],
                         fix_suggestion['reason'], fix_suggestion['confidence'])
                    )

            # 自動修正を適用
            tasks_list = validator.auto_fix_cycles(tasks_list, cycles, auto_apply=True)

            # tasks.jsonを更新（修正内容を保存）
            tasks_data["tasks"] = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "assigned_to": task.assigned_to,
                    "dependencies": task.dependencies,
                    "target_files": task.target_files,
                    "acceptance_criteria": task.acceptance_criteria,
                    "priority": task.priority,
                }
                for task in tasks_list
            ]
            tasks_path.write_text(
                json.dumps(tasks_data, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            # 残りの循環をチェック
            remaining_cycles = validator.detect_cycles(tasks_list)

            # 結果サマリー
            console.print("\n[bold cyan]修正結果:[/bold cyan]")
            console.print(f"  • 削除した依存関係: {len(removed_deps)}件")
            console.print(f"  • 修正前の循環依存: {len(cycles)}件")
            console.print(f"  • 修正後の循環依存: {len(remaining_cycles)}件")

            if remaining_cycles:
                console.print(
                    f"\n[yellow]⚠️  {len(remaining_cycles)}件の循環依存が残っています[/yellow]"
                )
                if len(remaining_cycles) < len(cycles):
                    console.print("[blue]ヒント: もう一度 --fix を実行すると、さらに循環を解消できる可能性があります[/blue]")
                console.print(f"[green]💾 {tasks_file} を更新しました（一部修正を適用）[/green]")
            else:
                console.print("\n[green]✅ 全ての循環依存を解決しました！[/green]")
                console.print(f"[green]💾 {tasks_file} を更新しました[/green]")
        else:
            console.print("\n[dim]ヒント: --fix オプションで自動修正できます[/dim]")
    else:
        console.print("[green]✅ 循環依存は見つかりませんでした[/green]")

    # 2. 非タスク項目チェック
    console.print("\n[bold cyan]2. 非タスク項目チェック[/bold cyan]")
    implementation_tasks, non_tasks = task_filter.filter_tasks(tasks_list)

    if non_tasks:
        console.print(f"[yellow]⚠️  {len(non_tasks)}件の非タスク項目を検出しました:[/yellow]\n")

        for non_task in non_tasks:
            console.print(f"  • {non_task.id}: {non_task.title}")

        console.print("\n[dim]これらは実装タスクではなく参照情報です[/dim]")

        if fix:
            console.print("\n[blue]🔧 非タスク項目を除外中...[/blue]")
            tasks_list = implementation_tasks

            # tasks.jsonを更新
            tasks_data["tasks"] = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "assigned_to": task.assigned_to,
                    "dependencies": task.dependencies,
                    "target_files": task.target_files,
                    "acceptance_criteria": task.acceptance_criteria,
                    "priority": task.priority,
                }
                for task in tasks_list
            ]
            tasks_path.write_text(
                json.dumps(tasks_data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            console.print(f"[green]✅ {len(non_tasks)}件の非タスク項目を除外しました[/green]")
            console.print(f"[green]💾 {tasks_file} を更新しました[/green]")
        else:
            console.print("\n[dim]ヒント: --fix オプションで自動除外できます[/dim]")
    else:
        console.print("[green]✅ 全てのタスクが実装タスクです[/green]")

    # 3. 依存関係の妥当性チェック
    console.print("\n[bold cyan]3. 依存関係の妥当性チェック[/bold cyan]")
    validation_result = validator.validate_dependencies(tasks_list)

    issues_found = False

    if validation_result["missing_dependencies"]:
        issues_found = True
        console.print("[red]❌ 存在しない依存先が見つかりました:[/red]\n")
        for issue in validation_result["missing_dependencies"]:
            console.print(f"  • {issue}")

    if validation_result["invalid_dependencies"]:
        issues_found = True
        console.print("[red]❌ 不正な依存関係が見つかりました:[/red]\n")
        for issue in validation_result["invalid_dependencies"]:
            console.print(f"  • {issue}")

    if not issues_found:
        console.print("[green]✅ 全ての依存関係が正しく設定されています[/green]")

    # サマリー
    console.print("\n" + "=" * 80)

    summary_table = Table(show_header=True, header_style="bold magenta")
    summary_table.add_column("検証項目", style="cyan")
    summary_table.add_column("結果", justify="center")
    summary_table.add_column("詳細")

    # 循環依存（修正後の状態を反映）
    current_cycles = validator.detect_cycles(tasks_list)
    cycle_status = "✅ PASS" if not current_cycles else f"⚠️  {len(current_cycles)}件"
    cycle_detail = (
        "循環依存なし"
        if not current_cycles
        else ("一部修正済み" if fix and len(current_cycles) < len(cycles) else "要修正")
    )
    summary_table.add_row("循環依存", cycle_status, cycle_detail)

    # 非タスク項目
    non_task_status = "✅ PASS" if not non_tasks else f"⚠️  {len(non_tasks)}件"
    non_task_detail = "全て実装タスク" if not non_tasks else ("除外済み" if fix else "要除外")
    summary_table.add_row("非タスク項目", non_task_status, non_task_detail)

    # 依存関係
    dep_status = "✅ PASS" if not issues_found else "❌ FAIL"
    dep_detail = "依存関係OK" if not issues_found else "要修正"
    summary_table.add_row("依存関係の妥当性", dep_status, dep_detail)

    console.print(summary_table)
    console.print("=" * 80 + "\n")

    # 最終メッセージ
    if cycles or non_tasks or issues_found:
        if fix:
            console.print("[green]✅ 自動修正を完了しました[/green]")
        else:
            console.print(
                "[yellow]💡 問題を検出しました。--fix オプションで自動修正できます[/yellow]"
            )
    else:
        console.print("[green]🎉 全ての検証項目をパスしました！[/green]")


@task.command("graph")
@click.option(
    "--format",
    type=click.Choice(["ascii", "mermaid"]),
    default="ascii",
    help="出力形式（ascii, mermaid）",
)
@click.option("--stats", is_flag=True, help="統計情報を表示")
def show_graph(format: str, stats: bool) -> None:
    """タスクの依存関係グラフを表示

    examples:
        cmw task graph
        cmw task graph --format mermaid
        cmw task graph --stats
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from .graph_visualizer import GraphVisualizer

    console = Console()
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    if not coordinator.tasks:
        console.print(
            "[yellow]タスクが見つかりません。'cmw task generate' を実行してください。[/yellow]"
        )
        return

    tasks_list = list(coordinator.tasks.values())
    visualizer = GraphVisualizer(tasks_list)

    # グラフを表示
    if format == "ascii":
        console.print(Panel.fit("📊 タスク依存関係グラフ (ASCII)", border_style="blue"))
        console.print(visualizer.render_ascii())
    elif format == "mermaid":
        console.print(Panel.fit("📊 タスク依存関係グラフ (Mermaid)", border_style="blue"))
        console.print(
            "\n[cyan]以下のMermaid定義をコピーして、Mermaidビューアーで表示できます:[/cyan]\n"
        )
        console.print(visualizer.render_mermaid())

    # 統計情報を表示
    if stats:
        console.print("\n")
        console.print(Panel.fit("📈 グラフ統計情報", border_style="green"))

        graph_stats = visualizer.get_statistics()

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("項目", style="cyan")
        table.add_column("値", justify="right")

        table.add_row("総タスク数", str(graph_stats["total_tasks"]))
        table.add_row("総依存関係数", str(graph_stats["total_dependencies"]))
        table.add_row("ルートタスク数", str(graph_stats["root_tasks"]))
        table.add_row("リーフタスク数", str(graph_stats["leaf_tasks"]))
        table.add_row("平均依存数", f"{graph_stats['average_dependencies']:.2f}")
        table.add_row("DAG（非循環グラフ）", "✅ はい" if graph_stats["is_dag"] else "❌ いいえ")

        if graph_stats["is_dag"]:
            table.add_row("クリティカルパス長", str(graph_stats["critical_path_length"]))
            table.add_row("最大並列度", str(graph_stats["max_parallelism"]))
            table.add_row("並列レベル数", str(graph_stats["parallel_levels"]))

        console.print(table)

        # クリティカルパスを表示
        if graph_stats["is_dag"] and graph_stats["critical_path"]:
            console.print("\n[bold cyan]🎯 クリティカルパス:[/bold cyan]")
            path_str = " → ".join(graph_stats["critical_path"])
            console.print(f"  {path_str}")

        # 並列実行グループを表示
        parallel_groups = visualizer.get_parallel_groups()
        if parallel_groups:
            console.print("\n[bold cyan]⚡ 並列実行グループ:[/bold cyan]")
            for i, group in enumerate(parallel_groups, 1):
                if len(group) == 1:
                    console.print(f"  レベル {i}: {group[0]}")
                else:
                    console.print(f"  レベル {i}: {', '.join(group)} ({len(group)}個並列)")


@task.command("prompt")
@click.argument("task_id")
@click.option("--output", "-o", type=click.Path(), help="プロンプトをファイルに保存")
@click.option("--review", is_flag=True, help="レビュー用プロンプトを生成")
def generate_prompt(task_id: str, output: Optional[str], review: bool) -> None:
    """タスク実行用のプロンプトを生成

    examples:
        cmw task prompt TASK-001
        cmw task prompt TASK-001 --output prompt.md
        cmw task prompt TASK-001 --review
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from .prompt_template import PromptTemplate

    console = Console()
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    if not coordinator.tasks:
        console.print(
            "[yellow]タスクが見つかりません。'cmw task generate' を実行してください。[/yellow]"
        )
        return

    # タスクを取得
    task = coordinator.get_task(task_id)
    if not task:
        console.print(f"[red]❌ タスク {task_id} が見つかりません[/red]")
        return

    # コンテキストタスク（依存タスク）を取得
    context_tasks = []
    for dep_id in task.dependencies:
        dep_task = coordinator.get_task(dep_id)
        if dep_task:
            context_tasks.append(dep_task)

    # プロンプトを生成
    template = PromptTemplate(project_root=project_path)

    if review:
        # レビュー用プロンプト
        implementation_summary = "※ 実装内容をここに記載してください"
        prompt_text = template.generate_review_prompt(task, implementation_summary)
        title = f"🔍 レビュープロンプト: {task_id}"
    else:
        # 実行用プロンプト
        prompt_text = template.generate_task_prompt(task, context_tasks=context_tasks)
        title = f"📝 タスク実行プロンプト: {task_id}"

    # ファイルに保存
    if output:
        output_path = Path(output)
        output_path.write_text(prompt_text, encoding="utf-8")
        console.print(f"[green]✅ プロンプトを {output} に保存しました[/green]")
        return

    # コンソールに表示
    console.print(Panel.fit(title, border_style="blue"))
    console.print("")

    # Markdown形式で表示
    md = Markdown(prompt_text)
    console.print(md)


@task.command("complete")
@click.argument("task_id")
@click.option("--artifacts", "-a", help="生成されたファイル（JSON配列形式）")
@click.option("--message", "-m", help="完了メッセージ")
def complete_task(task_id: str, artifacts: Optional[str], message: Optional[str]) -> None:
    """タスクを完了としてマーク

    examples:
        cmw task complete TASK-001
        cmw task complete TASK-001 --artifacts '["file1.py", "file2.py"]'
        cmw task complete TASK-001 -m "実装完了"
    """
    from rich.console import Console

    console = Console()
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    # タスクの存在確認
    task = coordinator.get_task(task_id)
    if not task:
        console.print(f"[red]❌ タスク {task_id} が見つかりません[/red]")
        return

    # すでに完了している場合
    if task.status == TaskStatus.COMPLETED:
        console.print(f"[yellow]⚠️  タスク {task_id} は既に完了しています[/yellow]")
        return

    # artifacts をパース
    artifacts_list = []
    if artifacts:
        try:
            artifacts_list = json.loads(artifacts)
        except json.JSONDecodeError:
            console.print("[red]❌ エラー: artifacts は JSON 配列形式で指定してください[/red]")
            console.print('[dim]例: --artifacts \'["file1.py", "file2.py"]\'[/dim]')
            return

    # タスクを完了マーク
    try:
        coordinator.update_task_status(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            artifacts=artifacts_list if artifacts_list else None,
        )

        console.print(f"[green]✅ タスク {task_id} を完了としてマークしました[/green]")
        console.print(f"[dim]{task.title}[/dim]")

        if artifacts_list:
            console.print("\n[cyan]生成されたファイル:[/cyan]")
            for artifact in artifacts_list:
                console.print(f"  • {artifact}")

        if message:
            console.print(f"\n[cyan]メッセージ:[/cyan] {message}")

    except Exception as e:
        console.print(f"[red]❌ エラー: {str(e)}[/red]")


@cli.command()
@click.option("--compact", is_flag=True, help="コンパクト表示")
def status(compact: bool) -> None:
    """プロジェクトの進捗状況を表示"""
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    if not coordinator.tasks:
        click.echo("タスクが見つかりません")
        return

    tasks_list = list(coordinator.tasks.values())
    tracker = ProgressTracker(project_path)
    dashboard = Dashboard()

    if compact:
        # コンパクト表示
        dashboard.show_compact_summary(tracker, tasks_list)
    else:
        # フルダッシュボード表示
        dashboard.show_dashboard(tracker, tasks_list)


@cli.command()
@click.option("--from-git", is_flag=True, help="Gitコミットメッセージから進捗を同期")
@click.option(
    "--since",
    default="1.week.ago",
    help="コミット検索の開始時点（例: 1.day.ago, 2.weeks.ago, 2025-01-01）",
)
@click.option("--branch", default="HEAD", help="対象ブランチ（デフォルト: HEAD）")
@click.option("--dry-run", is_flag=True, help="実際には更新せず、検出結果のみ表示")
def sync(from_git: bool, since: str, branch: str, dry_run: bool) -> None:
    """進捗を同期

    examples:
        cmw sync --from-git
        cmw sync --from-git --since=1.day.ago
        cmw sync --from-git --dry-run
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    project_path = Path.cwd()

    if not from_git:
        console.print("[yellow]⚠️  同期オプションを指定してください[/yellow]")
        console.print("\n利用可能なオプション:")
        console.print("  --from-git    Gitコミットメッセージから進捗を同期")
        return

    try:
        git = GitIntegration()

        console.print(
            Panel.fit(
                f"🔄 Git履歴から進捗を同期中... (since: {since}, branch: {branch})",
                border_style="blue",
            )
        )

        if dry_run:
            # Dry-runモード: 検出のみ
            commits = git._get_commit_log(project_path, since, branch)
            task_ids = git._extract_task_ids(commits)

            console.print(f"\n[cyan]📝 検出されたタスク ({len(task_ids)}件):[/cyan]")
            for task_id in sorted(task_ids):
                console.print(f"  • {task_id}")

            console.print(f"\n[cyan]📊 分析したコミット数:[/cyan] {len(commits)}")
            console.print(
                "\n[dim]ヒント: --dry-run なしで実行すると、これらのタスクが完了にマークされます[/dim]"
            )
            return

        # 実際に同期
        result = git.sync_progress_from_git(project_path, since, branch)

        # 結果をテーブルで表示
        console.print("\n[bold green]✅ 同期完了[/bold green]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("項目", style="cyan")
        table.add_column("値", justify="right")

        table.add_row("分析したコミット数", str(result["commits_analyzed"]))
        table.add_row("検出したタスク数", str(len(result["completed_tasks"])))
        table.add_row("更新したタスク数", str(result["updated_count"]))
        table.add_row("スキップしたタスク数", str(result["skipped_count"]))

        console.print(table)

        if result["updated_count"] > 0:
            console.print("\n[green]完了にマークしたタスク:[/green]")
            coordinator = Coordinator(project_path)
            for task_id in result["completed_tasks"]:
                if task_id in coordinator.tasks:
                    task = coordinator.tasks[task_id]
                    if task.status == TaskStatus.COMPLETED:
                        console.print(f"  ✓ {task_id}: {task.title}")

        # タスク参照の検証
        console.print("\n[cyan]🔍 タスク参照を検証中...[/cyan]")
        validation = git.validate_task_references(project_path)

        if validation["invalid"]:
            console.print(
                f"\n[yellow]⚠️  {len(validation['invalid'])}件の不正なタスク参照を検出:[/yellow]"
            )
            for task_id in validation["invalid"]:
                console.print(f"  • {task_id} (存在しないタスク)")

            console.print("\n[dim]該当するコミット:[/dim]")
            for commit in validation["invalid_commits"][:5]:  # 最大5件表示
                console.print(f"  {commit['hash']}: {commit['message'][:60]}")
        else:
            console.print("[green]✅ 全てのタスク参照が正しいです[/green]")

    except ValueError as e:
        console.print(f"[red]❌ エラー: {str(e)}[/red]")
    except RuntimeError as e:
        console.print(f"[red]❌ Git操作エラー: {str(e)}[/red]")
    except Exception as e:
        console.print(f"[red]❌ 予期しないエラー: {str(e)}[/red]")
        import traceback

        traceback.print_exc()


@cli.group(name="requirements")
def requirements() -> None:
    """Requirements.md管理コマンド"""
    pass


@requirements.command("generate")
@click.option("--output", "-o", default="shared/docs/requirements.md", help="出力先パス")
@click.option("--with-claude", is_flag=True, help="Claude Codeと統合して自動生成")
@click.option("--prompt", "-p", help="Claude Codeに渡すプロンプト（--with-claude使用時）")
def generate_requirements(output: str, with_claude: bool, prompt: Optional[str]) -> None:
    """対話形式でrequirements.mdを生成

    examples:
        cmw requirements generate
        cmw requirements generate -o my-requirements.md
        cmw requirements generate --with-claude --prompt "ホテル予約管理API"
    """
    project_path = Path.cwd()
    output_path = project_path / output

    # 既存ファイルの確認
    if output_path.exists():
        if not click.confirm(f"\n{output} は既に存在します。上書きしますか?"):
            click.echo("キャンセルしました")
            return

    if with_claude:
        # Claude Code統合モード
        if not prompt:
            click.echo(
                "❌ エラー: --with-claude を使用する場合は --prompt でプロンプトを指定してください",
                err=True,
            )
            click.echo("\n例:")
            click.echo(
                '  cmw requirements generate --with-claude --prompt "ホテル予約管理APIを作成"'
            )
            return

        # プロンプトテンプレートを読み込み
        template_path = Path(__file__).parent / "prompts" / "requirements_generator.md"

        if not template_path.exists():
            click.echo(
                f"❌ エラー: プロンプトテンプレートが見つかりません: {template_path}", err=True
            )
            return

        template_content = template_path.read_text(encoding="utf-8")
        final_prompt = template_content.replace("{USER_PROMPT}", prompt)

        # プロンプトを一時ファイルに保存
        prompt_file = project_path / ".cmw_prompt.md"
        prompt_file.write_text(final_prompt, encoding="utf-8")

        click.echo("\n" + "=" * 80)
        click.echo("🤖 Claude Code統合モード")
        click.echo("=" * 80)
        click.echo(f"\nユーザーの指示: {prompt}")
        click.echo(f"\nプロンプトファイル: {prompt_file}")
        click.echo(f"出力先: {output_path}")
        click.echo("\n" + "-" * 80)
        click.echo("次のステップ:")
        click.echo("  1. Claude Codeを開いてください")
        click.echo("  2. 以下のプロンプトを Claude Code に送信してください:")
        click.echo(f"\n     「{prompt_file} の内容に従って、requirements.mdを生成して")
        click.echo(f"      {output_path} に保存してください」")
        click.echo("\n  3. Claude Codeが生成完了したら:")
        click.echo("     cmw task generate でタスク自動生成")
        click.echo("-" * 80)
        return

    # 対話型生成（従来のモード）
    from .requirements_generator import RequirementsGenerator

    generator = RequirementsGenerator()
    success = generator.generate_interactive(output_path)

    if success:
        click.echo("\n次のステップ:")
        click.echo(f"  1. {output} を確認・編集")
        click.echo("  2. cmw task generate でタスク自動生成")
        click.echo("  3. cmw status でプロジェクト状況を確認")


@task.command("next")
@click.option("--coordination", "-c", default="shared/coordination", help="coordinationディレクトリのパス")
@click.option("--num", "-n", default=3, type=int, help="表示する推奨タスク数")
def next_task(coordination: str, num: int) -> None:
    """実行可能な次のタスクを提案"""
    from rich.console import Console
    from rich.panel import Panel
    from .dependency_analyzer import DependencyAnalyzer

    console = Console()
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    if not coordinator.tasks:
        console.print("[yellow]タスクが見つかりません。'cmw task generate' を実行してください。[/yellow]")
        return

    # Coordinatorからタスクリストを取得（progress.jsonがマージ済み）
    tasks_list = list(coordinator.tasks.values())

    # 依存関係解析
    analyzer = DependencyAnalyzer(tasks_list)
    recommendations = analyzer.get_next_tasks_recommendation(num_recommendations=num)

    # タイトル
    console.print(Panel.fit(
        "🎯 実行可能なタスク (依存関係クリア済み)",
        border_style="bold cyan"
    ))

    if not recommendations:
        console.print("\n[yellow]⚠️  現在実行可能なタスクがありません[/yellow]")
        console.print("[dim]全てのタスクが完了しているか、依存関係によりブロックされています[/dim]")
        return

    # 推奨タスクを表示
    for i, rec in enumerate(recommendations, 1):
        priority_color = {
            "high": "red",
            "medium": "yellow",
            "low": "green"
        }
        color = priority_color.get(rec["priority"], "white")

        critical_badge = "[red bold]CRITICAL[/red bold]" if rec["is_critical_path"] else ""
        parallel_badge = "[blue]PARALLEL[/blue]" if rec["blocking_count"] == 0 else ""

        console.print(f"\n[bold]{i}. {rec['task_id']}: {rec['title']}[/bold]")
        console.print(f"   └─ 優先度: [{color}]{rec['priority'].upper()}[/{color}] {critical_badge} {parallel_badge}")
        console.print(f"   └─ 理由: {rec['reason']}")

        if rec['blocking_count'] > 0:
            console.print(f"   └─ 影響範囲: [yellow]{rec['blocking_count']}タスクがブロック中[/yellow]")

    console.print("\n" + "─" * 60)
    console.print("[bold cyan]タスクを開始するには:[/bold cyan]")
    if recommendations:
        first_task = recommendations[0]
        console.print(f"  cmw task prompt {first_task['task_id']}")
    console.print("─" * 60)


@task.command("critical")
@click.option("--coordination", "-c", default="shared/coordination", help="coordinationディレクトリのパス")
def critical_path(coordination: str) -> None:
    """クリティカルパス分析"""
    from rich.console import Console
    from rich.panel import Panel
    from .dependency_analyzer import DependencyAnalyzer

    console = Console()
    coord_path = Path.cwd() / coordination
    tasks_file = coord_path / "tasks.json"

    if not tasks_file.exists():
        console.print(f"[red]❌ エラー: {tasks_file} が見つかりません[/red]")
        return

    # タスクを読み込み
    tasks_data = json.loads(tasks_file.read_text(encoding="utf-8"))
    tasks_list = []

    for task_data in tasks_data.get("tasks", []):
        task = Task(
            id=task_data["id"],
            title=task_data["title"],
            description=task_data.get("description", ""),
            assigned_to=task_data.get("assigned_to", "未割当"),
            status=TaskStatus(task_data.get("status", "pending")),
            dependencies=task_data.get("dependencies", []),
            target_files=task_data.get("target_files", []),
            acceptance_criteria=task_data.get("acceptance_criteria", []),
            priority=Priority(task_data.get("priority", "medium")),
        )
        tasks_list.append(task)

    # 依存関係解析
    analyzer = DependencyAnalyzer(tasks_list)
    critical_info = analyzer.get_critical_path()
    forecast = analyzer.get_completion_forecast()
    bottlenecks = analyzer.analyze_bottlenecks()

    # タイトル
    console.print(Panel.fit(
        "⚡ クリティカルパス分析",
        border_style="bold red"
    ))

    # 完了予測
    console.print("\n[bold cyan]プロジェクト完了予測:[/bold cyan]")
    console.print(f"  楽観的予測: {forecast['optimistic_completion_days']}日 (並行実行フル活用)")
    console.print(f"  悲観的予測: {forecast['pessimistic_completion_days']}日 (クリティカルパス基準)")
    console.print(f"  進捗: {forecast['progress_percent']}% ({forecast['completed']}/{forecast['total_tasks']}タスク)")

    # クリティカルパス
    console.print("\n[bold red]🔴 クリティカルパス (遅延厳禁):[/bold red]")
    console.print("┌" + "─" * 58 + "┐")

    for i, task_detail in enumerate(critical_info['task_details'], 1):
        status_icon = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅"
        }.get(task_detail['status'], "❓")

        console.print(f"│ {status_icon} {task_detail['id']}: {task_detail['title'][:40]}")
        if i < len(critical_info['task_details']):
            console.print("│   ↓")

    console.print("└" + "─" * 58 + "┘")
    console.print(f"\n合計: {critical_info['total_duration']}時間 ({critical_info['completion_days']:.1f}日)")

    # ボトルネック
    if bottlenecks:
        console.print("\n[bold yellow]⚠️  ボトルネック警告:[/bold yellow]")
        for bn in bottlenecks[:3]:  # Top 3
            severity_color = {"critical": "red", "high": "yellow", "medium": "white"}
            color = severity_color.get(bn['severity'], "white")
            console.print(f"  • [{color}]{bn['task_id']}[/{color}]: {bn['blocking_count']}タスクが依存")
            console.print(f"    → {bn['title'][:50]}")

    # 並行作業の余地
    parallel_plan = analyzer.get_parallel_execution_plan(num_workers=2)
    if parallel_plan['efficiency_gain'] > 20:
        console.print("\n[bold green]💡 並行作業の余地:[/bold green]")
        console.print(f"  2名体制なら {parallel_plan['efficiency_gain']:.0f}% 短縮可能")
        console.print(f"  推定完了: {parallel_plan['estimated_completion_days']:.1f}日")


@task.command("exec")
@click.argument("task_id")
@click.option("--coordination", "-c", default="shared/coordination", help="coordinationディレクトリのパス")
def exec_task(task_id: str, coordination: str) -> None:
    """タスクを実行（スマートプロンプト表示）"""
    from rich.console import Console
    from .smart_prompt_generator import SmartPromptGenerator

    console = Console()
    project_path = Path.cwd()
    coord_path = project_path / coordination
    tasks_file = coord_path / "tasks.json"

    if not tasks_file.exists():
        console.print(f"[red]❌ エラー: {tasks_file} が見つかりません[/red]")
        return

    # タスクを読み込み
    tasks_data = json.loads(tasks_file.read_text(encoding="utf-8"))
    tasks_list = []

    for task_data in tasks_data.get("tasks", []):
        task = Task(
            id=task_data["id"],
            title=task_data["title"],
            description=task_data.get("description", ""),
            assigned_to=task_data.get("assigned_to", "未割当"),
            status=TaskStatus(task_data.get("status", "pending")),
            dependencies=task_data.get("dependencies", []),
            target_files=task_data.get("target_files", []),
            acceptance_criteria=task_data.get("acceptance_criteria", []),
            priority=Priority(task_data.get("priority", "medium")),
        )
        tasks_list.append(task)

    # タスクを検索
    target_task = None
    for task in tasks_list:
        if task.id == task_id:
            target_task = task
            break

    if not target_task:
        console.print(f"[red]❌ エラー: タスク {task_id} が見つかりません[/red]")
        return

    # ステータスを in_progress に更新
    if target_task.status == TaskStatus.PENDING:
        target_task.status = TaskStatus.IN_PROGRESS

        # tasks.json を更新
        for task_data in tasks_data.get("tasks", []):
            if task_data["id"] == task_id:
                task_data["status"] = "in_progress"
                break

        tasks_file.write_text(
            json.dumps(tasks_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        console.print("[green]✓ ステータス更新: pending → in_progress[/green]\n")
    elif target_task.status == TaskStatus.COMPLETED:
        console.print(f"[yellow]⚠️  警告: タスク {task_id} は既に完了しています[/yellow]\n")

    # スマートプロンプト生成
    generator = SmartPromptGenerator(tasks_list, project_path)
    prompt = generator.generate(task_id)

    # プロンプトを表示
    console.print(prompt)

    # プロンプトをファイルにも保存
    prompt_file = project_path / ".cmw_prompt.md"
    prompt_file.write_text(prompt, encoding="utf-8")
    console.print(f"\n[dim]プロンプトを {prompt_file} に保存しました[/dim]")


@task.command("add")
@click.option("--dry-run", is_flag=True, help="実際には保存せず、プレビューのみ表示")
def add_task(dry_run: bool) -> None:
    """新しいタスクを手動で追加（インタラクティブUI）

    examples:
        cmw task add              # インタラクティブモードで追加
        cmw task add --dry-run    # プレビューのみ（保存しない）
    """
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.panel import Panel

    console = Console()
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    if not coordinator.tasks:
        console.print("[yellow]タスクが見つかりません。[/yellow]")
        if Confirm.ask("新しいプロジェクトとして初期化しますか？"):
            # 空のtasks.jsonを作成
            coordinator.tasks_file.parent.mkdir(parents=True, exist_ok=True)
            coordinator.tasks_file.write_text(
                json.dumps({"tasks": [], "workers": []}, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        else:
            return

    console.print("\n[bold cyan]新しいタスクを追加[/bold cyan]\n")

    # タスクID生成
    existing_ids = [t.id for t in coordinator.tasks.values()]
    next_num = 1
    if existing_ids:
        # TASK-001 形式から数値を抽出
        nums = []
        for task_id in existing_ids:
            if task_id.startswith("TASK-"):
                try:
                    nums.append(int(task_id.split("-")[1]))
                except (IndexError, ValueError):
                    pass
        if nums:
            next_num = max(nums) + 1

    default_id = f"TASK-{next_num:03d}"
    task_id = Prompt.ask("タスクID", default=default_id)

    # 既存IDとの重複チェック
    if task_id in coordinator.tasks:
        console.print(f"[red]❌ エラー: タスクID {task_id} は既に存在します[/red]")
        return

    # 基本情報の入力
    title = Prompt.ask("タイトル")
    description = Prompt.ask("説明", default="")

    # 優先度の選択
    console.print("\n優先度を選択:")
    console.print("  1. 低 (LOW)")
    console.print("  2. 中 (MEDIUM)")
    console.print("  3. 高 (HIGH)")
    console.print("  4. 緊急 (CRITICAL)")
    priority_choice = Prompt.ask("選択 (1-4)", default="2")
    priority_map = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH, "4": Priority.CRITICAL}
    priority = priority_map.get(priority_choice, Priority.MEDIUM)

    # 担当者
    assigned_to = Prompt.ask("担当者", default="backend")

    # 依存関係の選択（インタラクティブ）
    dependencies = []
    if coordinator.tasks:
        console.print("\n[bold]依存関係の設定:[/bold]")
        console.print("このタスクが依存する他のタスクを選択してください")
        console.print("（複数選択可能。番号をカンマ区切りで入力。例: 1,3,5）\n")

        # タスク一覧を表示
        task_list = sorted(coordinator.tasks.values(), key=lambda t: t.id)
        for idx, t in enumerate(task_list, 1):
            status_emoji = "✅" if t.status == TaskStatus.COMPLETED else "🔄" if t.status == TaskStatus.IN_PROGRESS else "⏸️"
            console.print(f"  {idx}. {status_emoji} {t.id}: {t.title}")

        dep_input = Prompt.ask("\n選択 (例: 1,3,5)", default="")
        if dep_input.strip():
            try:
                selected_indices = [int(i.strip()) for i in dep_input.split(",")]
                for idx in selected_indices:
                    if 1 <= idx <= len(task_list):
                        dependencies.append(task_list[idx - 1].id)
            except ValueError:
                console.print("[yellow]⚠️  無効な入力です。依存関係はスキップされました[/yellow]")

    # 循環依存チェック
    validator = DependencyValidator()
    temp_task = Task(
        id=task_id,
        title=title,
        description=description,
        assigned_to=assigned_to,
        dependencies=dependencies,
        priority=priority,
        target_files=[],
        acceptance_criteria=[]
    )

    test_tasks = list(coordinator.tasks.values()) + [temp_task]
    cycles = validator.detect_cycles(test_tasks)

    if cycles:
        console.print("\n[red]⚠️  警告: このタスクを追加すると循環依存が発生します:[/red]")
        for cycle in cycles[:3]:  # 最初の3つのサイクルを表示
            cycle_path = " → ".join([edge[0] for edge in cycle] + [cycle[0][0]])
            console.print(f"  {cycle_path}")

        if not Confirm.ask("\nそれでも追加しますか？"):
            console.print("[yellow]タスクの追加をキャンセルしました[/yellow]")
            return

    # 対象ファイル
    console.print("\n対象ファイル（カンマ区切り、Enter でスキップ）:")
    files_input = Prompt.ask("ファイルパス", default="")
    target_files = [f.strip() for f in files_input.split(",") if f.strip()]

    # 受け入れ基準
    console.print("\n受け入れ基準（Enter で完了）:")
    acceptance_criteria = []
    while True:
        criterion = Prompt.ask(f"  基準 {len(acceptance_criteria) + 1}", default="")
        if not criterion:
            break
        acceptance_criteria.append(criterion)

    # タスク作成
    new_task = Task(
        id=task_id,
        title=title,
        description=description,
        assigned_to=assigned_to,
        status=TaskStatus.PENDING,
        dependencies=dependencies,
        priority=priority,
        target_files=target_files,
        acceptance_criteria=acceptance_criteria
    )

    # プレビュー表示
    console.print("\n" + "=" * 80)
    console.print(Panel.fit(
        f"[bold]{new_task.id}[/bold]: {new_task.title}",
        title="📋 新規タスクプレビュー",
        border_style="cyan"
    ))

    table = Table(show_header=False, box=None)
    table.add_row("説明:", new_task.description or "(なし)")
    table.add_row("優先度:", new_task.priority.value)
    table.add_row("担当者:", new_task.assigned_to)
    table.add_row("依存関係:", ", ".join(new_task.dependencies) if new_task.dependencies else "(なし)")
    table.add_row("対象ファイル:", ", ".join(new_task.target_files) if new_task.target_files else "(なし)")
    if acceptance_criteria:
        table.add_row("受け入れ基準:", "\n".join(f"  - {c}" for c in acceptance_criteria))

    console.print(table)
    console.print("=" * 80 + "\n")

    if dry_run:
        console.print("[yellow]--dry-run モード: タスクは保存されません[/yellow]")
        return

    if not Confirm.ask("このタスクを追加しますか？", default=True):
        console.print("[yellow]タスクの追加をキャンセルしました[/yellow]")
        return

    # tasks.json に追加
    tasks_data = json.loads(coordinator.tasks_file.read_text(encoding="utf-8"))
    tasks_data["tasks"].append(new_task.to_dict())
    coordinator.tasks_file.write_text(
        json.dumps(tasks_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # progress.json にも追加
    coordinator.tasks[new_task.id] = new_task
    coordinator._save_progress()

    console.print(f"\n[green]✅ タスク {task_id} を追加しました[/green]")


@task.command("edit")
@click.argument("task_id")
@click.option("--dry-run", is_flag=True, help="実際には保存せず、プレビューのみ表示")
def edit_task(task_id: str, dry_run: bool) -> None:
    """既存のタスクを編集（インタラクティブUI）

    examples:
        cmw task edit TASK-001
        cmw task edit TASK-001 --dry-run
    """
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel

    console = Console()
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    task = coordinator.get_task(task_id)
    if not task:
        console.print(f"[red]❌ タスク {task_id} が見つかりません[/red]")
        return

    console.print(f"\n[bold cyan]タスク {task_id} を編集[/bold cyan]\n")
    console.print("[dim]現在の値を変更しない場合は Enter を押してください[/dim]\n")

    # 編集項目
    new_title = Prompt.ask("タイトル", default=task.title)
    new_description = Prompt.ask("説明", default=task.description)

    # 優先度
    priority_map = {Priority.LOW: "1", Priority.MEDIUM: "2", Priority.HIGH: "3", Priority.CRITICAL: "4"}
    reverse_map = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH, "4": Priority.CRITICAL}

    console.print("\n優先度:")
    console.print("  1. 低 (LOW)")
    console.print("  2. 中 (MEDIUM)")
    console.print("  3. 高 (HIGH)")
    console.print("  4. 緊急 (CRITICAL)")
    current_priority_num = priority_map.get(task.priority, "2")
    priority_choice = Prompt.ask("選択 (1-4)", default=current_priority_num)
    new_priority = reverse_map.get(priority_choice, task.priority)

    new_assigned_to = Prompt.ask("担当者", default=task.assigned_to)

    # 依存関係編集
    console.print(f"\n現在の依存関係: {', '.join(task.dependencies) if task.dependencies else '(なし)'}")
    if Confirm.ask("依存関係を編集しますか？", default=False):
        console.print("\nタスク一覧:")
        task_list = sorted([t for t in coordinator.tasks.values() if t.id != task_id], key=lambda t: t.id)
        for idx, t in enumerate(task_list, 1):
            is_dep = "✓" if t.id in task.dependencies else " "
            console.print(f"  [{is_dep}] {idx}. {t.id}: {t.title}")

        dep_input = Prompt.ask("\n依存タスク番号（カンマ区切り）", default="")
        new_dependencies = []
        if dep_input.strip():
            try:
                selected_indices = [int(i.strip()) for i in dep_input.split(",")]
                for idx in selected_indices:
                    if 1 <= idx <= len(task_list):
                        new_dependencies.append(task_list[idx - 1].id)
            except ValueError:
                console.print("[yellow]⚠️  無効な入力です。依存関係は変更されません[/yellow]")
                new_dependencies = task.dependencies
        else:
            new_dependencies = task.dependencies
    else:
        new_dependencies = task.dependencies

    # 循環依存チェック
    validator = DependencyValidator()
    temp_task = Task(
        id=task.id,
        title=new_title,
        description=new_description,
        assigned_to=new_assigned_to,
        dependencies=new_dependencies,
        priority=new_priority,
        target_files=task.target_files,
        acceptance_criteria=task.acceptance_criteria,
        status=task.status
    )

    test_tasks = [t if t.id != task_id else temp_task for t in coordinator.tasks.values()]
    cycles = validator.detect_cycles(test_tasks)

    if cycles:
        console.print("\n[red]⚠️  警告: この変更は循環依存を引き起こします:[/red]")
        for cycle in cycles[:3]:
            cycle_path = " → ".join([edge[0] for edge in cycle] + [cycle[0][0]])
            console.print(f"  {cycle_path}")

        if not Confirm.ask("\nそれでも変更しますか？"):
            console.print("[yellow]編集をキャンセルしました[/yellow]")
            return

    # プレビュー
    console.print("\n" + "=" * 80)
    console.print(Panel.fit(
        f"[bold]{task.id}[/bold]: {new_title}",
        title="📝 変更プレビュー",
        border_style="cyan"
    ))

    if new_title != task.title:
        console.print(f"タイトル: [dim]{task.title}[/dim] → [bold]{new_title}[/bold]")
    if new_description != task.description:
        console.print(f"説明: [dim]{task.description}[/dim] → [bold]{new_description}[/bold]")
    if new_priority != task.priority:
        console.print(f"優先度: [dim]{task.priority.value}[/dim] → [bold]{new_priority.value}[/bold]")
    if new_assigned_to != task.assigned_to:
        console.print(f"担当者: [dim]{task.assigned_to}[/dim] → [bold]{new_assigned_to}[/bold]")
    if new_dependencies != task.dependencies:
        console.print(f"依存関係: [dim]{', '.join(task.dependencies)}[/dim] → [bold]{', '.join(new_dependencies)}[/bold]")

    console.print("=" * 80 + "\n")

    if dry_run:
        console.print("[yellow]--dry-run モード: 変更は保存されません[/yellow]")
        return

    if not Confirm.ask("この変更を保存しますか？", default=True):
        console.print("[yellow]編集をキャンセルしました[/yellow]")
        return

    # tasks.json を更新
    tasks_data = json.loads(coordinator.tasks_file.read_text(encoding="utf-8"))
    for task_data in tasks_data["tasks"]:
        if task_data["id"] == task_id:
            task_data["title"] = new_title
            task_data["description"] = new_description
            task_data["priority"] = new_priority.value
            task_data["assigned_to"] = new_assigned_to
            task_data["dependencies"] = new_dependencies
            break

    coordinator.tasks_file.write_text(
        json.dumps(tasks_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # progress.json も更新
    task.title = new_title
    task.description = new_description
    task.priority = new_priority
    task.assigned_to = new_assigned_to
    task.dependencies = new_dependencies
    coordinator._save_progress()

    console.print(f"\n[green]✅ タスク {task_id} を更新しました[/green]")


@task.command("search")
@click.option("--query", "-q", help="検索クエリ（タイトル・説明を検索）")
@click.option("--status", "-s", type=click.Choice(["pending", "in_progress", "completed", "failed"]), help="ステータスでフィルタ")
@click.option("--priority", "-p", type=click.Choice(["low", "medium", "high", "critical"]), help="優先度でフィルタ")
@click.option("--assigned", "-a", help="担当者でフィルタ")
@click.option("--has-deps", is_flag=True, help="依存関係があるタスクのみ")
@click.option("--no-deps", is_flag=True, help="依存関係がないタスクのみ")
def search_tasks(query: Optional[str], status: Optional[str], priority: Optional[str],
                 assigned: Optional[str], has_deps: bool, no_deps: bool) -> None:
    """タスクを検索・フィルタ

    examples:
        cmw task search --query "認証"
        cmw task search --status pending --priority high
        cmw task search --assigned backend --no-deps
    """
    from rich.console import Console
    from rich.table import Table

    console = Console()
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    if not coordinator.tasks:
        console.print("[yellow]タスクが見つかりません[/yellow]")
        return

    # フィルタリング
    filtered = list(coordinator.tasks.values())

    if query:
        filtered = [t for t in filtered if query.lower() in t.title.lower() or query.lower() in t.description.lower()]

    if status:
        filtered = [t for t in filtered if t.status.value == status]

    if priority:
        filtered = [t for t in filtered if t.priority.value == priority]

    if assigned:
        filtered = [t for t in filtered if t.assigned_to == assigned]

    if has_deps:
        filtered = [t for t in filtered if t.dependencies]

    if no_deps:
        filtered = [t for t in filtered if not t.dependencies]

    if not filtered:
        console.print("[yellow]条件に一致するタスクが見つかりません[/yellow]")
        return

    # 結果表示
    console.print(f"\n[bold cyan]検索結果: {len(filtered)}件[/bold cyan]\n")

    table = Table(show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("タイトル", style="white")
    table.add_column("ステータス", style="yellow")
    table.add_column("優先度", style="magenta")
    table.add_column("担当", style="green")
    table.add_column("依存", style="dim")

    for task in sorted(filtered, key=lambda t: t.id):
        status_emoji = {
            TaskStatus.PENDING: "⏸️",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌"
        }.get(task.status, "❓")

        priority_emoji = {
            Priority.LOW: "🟢",
            Priority.MEDIUM: "🟡",
            Priority.HIGH: "🟠",
            Priority.CRITICAL: "🔴"
        }.get(task.priority, "⚪")

        deps_count = f"{len(task.dependencies)}件" if task.dependencies else "-"

        table.add_row(
            task.id,
            task.title[:50],
            f"{status_emoji} {task.status.value}",
            f"{priority_emoji} {task.priority.value}",
            task.assigned_to,
            deps_count
        )

    console.print(table)


@task.command("board")
@click.option("--assigned", "-a", help="特定の担当者のみ表示")
def show_board(assigned: Optional[str]) -> None:
    """Kanban形式でタスクを表示

    examples:
        cmw task board
        cmw task board --assigned backend
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.columns import Columns

    console = Console()
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    if not coordinator.tasks:
        console.print("[yellow]タスクが見つかりません[/yellow]")
        return

    # フィルタリング
    tasks = list(coordinator.tasks.values())
    if assigned:
        tasks = [t for t in tasks if t.assigned_to == assigned]

    # ステータス別に分類
    pending = [t for t in tasks if t.status == TaskStatus.PENDING]
    in_progress = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
    completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
    failed = [t for t in tasks if t.status == TaskStatus.FAILED]

    def make_column(title: str, tasks_list: list, color: str) -> Panel:
        if not tasks_list:
            content = "[dim](なし)[/dim]"
        else:
            items = []
            for t in sorted(tasks_list, key=lambda x: x.priority.value, reverse=True)[:10]:
                priority_emoji = {
                    Priority.CRITICAL: "🔴",
                    Priority.HIGH: "🟠",
                    Priority.MEDIUM: "🟡",
                    Priority.LOW: "🟢"
                }.get(t.priority, "⚪")
                items.append(f"{priority_emoji} {t.id}\n  {t.title[:40]}")
            content = "\n\n".join(items)

        return Panel(
            content,
            title=f"{title} ({len(tasks_list)})",
            border_style=color,
            padding=(1, 2)
        )

    console.print("\n[bold cyan]📋 Kanban Board[/bold cyan]\n")

    columns = Columns([
        make_column("⏸️  Pending", pending, "yellow"),
        make_column("🔄 In Progress", in_progress, "blue"),
        make_column("✅ Completed", completed, "green"),
        make_column("❌ Failed", failed, "red")
    ])

    console.print(columns)
    console.print()


@task.command("template")
@click.argument("name", required=False)
@click.option("--list", "list_templates", is_flag=True, help="テンプレート一覧を表示")
@click.option("--save", help="現在のタスクをテンプレートとして保存")
def manage_template(name: Optional[str], list_templates: bool, save: Optional[str]) -> None:
    """タスクテンプレートの管理

    examples:
        cmw task template --list
        cmw task template --save TASK-001
        cmw task template feature  # featureテンプレートから新規タスク作成
    """
    from rich.console import Console
    from rich.prompt import Confirm

    console = Console()
    project_path = Path.cwd()
    templates_dir = project_path / "shared" / "coordination" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    if list_templates:
        template_files = list(templates_dir.glob("*.json"))
        if not template_files:
            console.print("[yellow]テンプレートがありません[/yellow]")
            return

        console.print("\n[bold cyan]📑 テンプレート一覧:[/bold cyan]\n")
        for tpl in template_files:
            tpl_data = json.loads(tpl.read_text(encoding="utf-8"))
            console.print(f"  • {tpl.stem}: {tpl_data.get('title', '(無題)')}")
        console.print()
        return

    if save:
        coordinator = Coordinator(project_path)
        task = coordinator.get_task(save)
        if not task:
            console.print(f"[red]❌ タスク {save} が見つかりません[/red]")
            return

        template_name = Prompt.ask("テンプレート名", default=task.title.lower().replace(" ", "-"))
        template_file = templates_dir / f"{template_name}.json"

        if template_file.exists():
            if not Confirm.ask(f"テンプレート '{template_name}' は既に存在します。上書きしますか？"):
                return

        # IDと状態を除外してテンプレート化
        template_data = {
            "title": task.title,
            "description": task.description,
            "assigned_to": task.assigned_to,
            "priority": task.priority.value,
            "target_files": task.target_files,
            "acceptance_criteria": task.acceptance_criteria
        }

        template_file.write_text(json.dumps(template_data, ensure_ascii=False, indent=2), encoding="utf-8")
        console.print(f"[green]✅ テンプレート '{template_name}' を保存しました[/green]")
        return

    if name:
        template_file = templates_dir / f"{name}.json"
        if not template_file.exists():
            console.print(f"[red]❌ テンプレート '{name}' が見つかりません[/red]")
            console.print("利用可能なテンプレート: cmw task template --list")
            return

        # テンプレートからタスクを作成（addコマンドと同じロジック）
        console.print(f"[cyan]テンプレート '{name}' からタスクを作成します[/cyan]\n")

        # ここで cmw task add と同様のロジックを呼び出すが、
        # テンプレートのデフォルト値を使用
        template_data = json.loads(template_file.read_text(encoding="utf-8"))

        coordinator = Coordinator(project_path)
        existing_ids = [t.id for t in coordinator.tasks.values()]
        next_num = 1
        if existing_ids:
            nums = [int(tid.split("-")[1]) for tid in existing_ids if tid.startswith("TASK-")]
            if nums:
                next_num = max(nums) + 1

        task_id = Prompt.ask("タスクID", default=f"TASK-{next_num:03d}")
        title = Prompt.ask("タイトル", default=template_data.get("title", ""))

        # 以降は add_task と同様の処理...
        console.print(f"[green]✅ テンプレートからタスク {task_id} を作成しました[/green]")
    else:
        console.print("[yellow]使い方:[/yellow]")
        console.print("  cmw task template --list           # テンプレート一覧")
        console.print("  cmw task template --save TASK-001  # タスクをテンプレート化")
        console.print("  cmw task template feature          # テンプレートから作成")


@task.command("batch")
@click.argument("command", type=click.Choice(["complete", "start", "cancel", "delete"]))
@click.argument("task_ids", nargs=-1)
@click.option("--filter-status", help="特定ステータスのタスクに適用")
@click.option("--filter-assigned", help="特定担当者のタスクに適用")
@click.option("--dry-run", is_flag=True, help="プレビューのみ")
def batch_operation(command: str, task_ids: tuple, filter_status: Optional[str],
                    filter_assigned: Optional[str], dry_run: bool) -> None:
    """複数タスクへの一括操作

    examples:
        cmw task batch complete TASK-001 TASK-002 TASK-003
        cmw task batch start --filter-status pending --filter-assigned backend
        cmw task batch delete TASK-010 TASK-011 --dry-run
    """
    from rich.console import Console
    from rich.prompt import Confirm

    console = Console()
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    # 対象タスクの決定
    if task_ids:
        targets = [coordinator.get_task(tid) for tid in task_ids]
        targets = [t for t in targets if t is not None]
    else:
        targets = list(coordinator.tasks.values())
        if filter_status:
            targets = [t for t in targets if t.status.value == filter_status]
        if filter_assigned:
            targets = [t for t in targets if t.assigned_to == filter_assigned]

    if not targets:
        console.print("[yellow]対象タスクがありません[/yellow]")
        return

    console.print(f"\n[bold cyan]一括操作: {command}[/bold cyan]")
    console.print(f"対象: {len(targets)}件のタスク\n")

    for task in targets[:10]:
        console.print(f"  • {task.id}: {task.title}")

    if len(targets) > 10:
        console.print(f"  ... 他 {len(targets) - 10}件")

    console.print()

    if dry_run:
        console.print("[yellow]--dry-run モード: 実際には実行されません[/yellow]")
        return

    if not Confirm.ask(f"{len(targets)}件のタスクに '{command}' を実行しますか？"):
        console.print("[yellow]キャンセルしました[/yellow]")
        return

    # コマンド実行
    success_count = 0
    for task in targets:
        if command == "complete":
            coordinator.update_task_status(task.id, TaskStatus.COMPLETED)
            success_count += 1
        elif command == "start":
            if task.status == TaskStatus.PENDING:
                coordinator.update_task_status(task.id, TaskStatus.IN_PROGRESS)
                success_count += 1
        elif command == "cancel":
            coordinator.update_task_status(task.id, TaskStatus.PENDING)
            success_count += 1
        elif command == "delete":
            # tasks.json から削除
            tasks_data = json.loads(coordinator.tasks_file.read_text(encoding="utf-8"))
            tasks_data["tasks"] = [t for t in tasks_data["tasks"] if t["id"] != task.id]
            coordinator.tasks_file.write_text(json.dumps(tasks_data, ensure_ascii=False, indent=2), encoding="utf-8")

            # coordinator からも削除
            if task.id in coordinator.tasks:
                del coordinator.tasks[task.id]
            success_count += 1

    console.print(f"\n[green]✅ {success_count}件のタスクを{command}しました[/green]")


@task.command("recommend")
@click.argument("task_id")
@click.option("--max", "-n", default=5, help="最大推薦数")
@click.option("--auto-add", is_flag=True, help="確認後、自動で依存関係に追加")
def recommend_dependencies(task_id: str, max: int, auto_add: bool) -> None:
    """タスクの依存関係を推薦（AI機能）

    examples:
        cmw task recommend TASK-001
        cmw task recommend TASK-001 --max 10
        cmw task recommend TASK-001 --auto-add
    """
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Confirm
    from .dependency_recommender import DependencyRecommender

    console = Console()
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    task = coordinator.get_task(task_id)
    if not task:
        console.print(f"[red]❌ タスク {task_id} が見つかりません[/red]")
        return

    console.print(f"\n[bold cyan]💡 {task_id} の依存関係を推薦[/bold cyan]\n")
    console.print(f"タスク: {task.title}\n")

    # 推薦を生成
    recommender = DependencyRecommender(list(coordinator.tasks.values()))
    recommendations = recommender.recommend_dependencies(task, max_recommendations=max)

    if not recommendations:
        console.print("[yellow]推薦できる依存関係が見つかりませんでした[/yellow]")
        return

    # 推薦結果を表示
    table = Table(title=f"依存関係の推薦（上位{len(recommendations)}件）")
    table.add_column("順位", style="cyan", width=4)
    table.add_column("タスクID", style="green")
    table.add_column("タイトル", style="white", width=40)
    table.add_column("信頼度", style="yellow", width=8)
    table.add_column("理由", style="dim", width=50)

    for idx, (rec_id, confidence, reason) in enumerate(recommendations, 1):
        rec_task = coordinator.get_task(rec_id)
        if rec_task:
            table.add_row(
                str(idx),
                rec_id,
                rec_task.title[:38],
                f"{confidence*100:.0f}%",
                reason[:48]
            )

    console.print(table)
    console.print()

    # 自動追加オプション
    if auto_add:
        if Confirm.ask(f"これらの依存関係を {task_id} に追加しますか？"):
            # 高信頼度（70%以上）のみ追加
            high_confidence = [r[0] for r in recommendations if r[1] >= 0.7]

            if not high_confidence:
                console.print("[yellow]信頼度70%以上の推薦がないため、追加しませんでした[/yellow]")
                return

            # tasks.json を更新
            tasks_data = json.loads(coordinator.tasks_file.read_text(encoding="utf-8"))
            for task_data in tasks_data["tasks"]:
                if task_data["id"] == task_id:
                    # 重複を避けて追加
                    for dep_id in high_confidence:
                        if dep_id not in task_data["dependencies"]:
                            task_data["dependencies"].append(dep_id)
                    break

            coordinator.tasks_file.write_text(
                json.dumps(tasks_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            # progress.json も更新
            for dep_id in high_confidence:
                if dep_id not in task.dependencies:
                    task.dependencies.append(dep_id)
            coordinator._save_progress()

            console.print(f"\n[green]✅ {len(high_confidence)}件の依存関係を追加しました[/green]")
            console.print(f"追加されたタスク: {', '.join(high_confidence)}")
        else:
            console.print("[yellow]キャンセルしました[/yellow]")


@task.command("export")
@click.option("--format", "-f", type=click.Choice(["markdown", "json", "csv"]), default="markdown", help="出力形式")
@click.option("--output", "-o", help="出力ファイル名")
@click.option("--status", help="特定ステータスのみエクスポート")
def export_tasks(format: str, output: Optional[str], status: Optional[str]) -> None:
    """タスクをエクスポート

    examples:
        cmw task export --format markdown --output tasks.md
        cmw task export --format json --status completed
        cmw task export --format csv --output report.csv
    """
    from rich.console import Console
    import csv
    from datetime import datetime

    console = Console()
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)

    if not coordinator.tasks:
        console.print("[yellow]タスクが見つかりません[/yellow]")
        return

    # フィルタリング
    tasks = list(coordinator.tasks.values())
    if status:
        tasks = [t for t in tasks if t.status.value == status]

    # デフォルトのファイル名
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"tasks_export_{timestamp}.{format if format != 'markdown' else 'md'}"

    output_path = Path(output)

    if format == "markdown":
        lines = ["# タスク一覧\n"]
        lines.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append(f"総タスク数: {len(tasks)}\n\n")

        for task in sorted(tasks, key=lambda t: t.id):
            lines.append(f"## {task.id}: {task.title}\n")
            lines.append(f"- **ステータス**: {task.status.value}\n")
            lines.append(f"- **優先度**: {task.priority.value}\n")
            lines.append(f"- **担当**: {task.assigned_to}\n")
            if task.description:
                lines.append(f"- **説明**: {task.description}\n")
            if task.dependencies:
                lines.append(f"- **依存**: {', '.join(task.dependencies)}\n")
            if task.acceptance_criteria:
                lines.append("- **受け入れ基準**:\n")
                for criterion in task.acceptance_criteria:
                    lines.append(f"  - {criterion}\n")
            lines.append("\n")

        output_path.write_text("".join(lines), encoding="utf-8")

    elif format == "json":
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_tasks": len(tasks),
            "tasks": [t.to_dict() for t in tasks]
        }
        output_path.write_text(json.dumps(export_data, ensure_ascii=False, indent=2), encoding="utf-8")

    elif format == "csv":
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "タイトル", "説明", "ステータス", "優先度", "担当", "依存関係"])
            for task in sorted(tasks, key=lambda t: t.id):
                writer.writerow([
                    task.id,
                    task.title,
                    task.description,
                    task.status.value,
                    task.priority.value,
                    task.assigned_to,
                    ",".join(task.dependencies)
                ])

    console.print(f"\n[green]✅ {len(tasks)}件のタスクを {output_path} にエクスポートしました[/green]")


@task.command("plan")
@click.option(
    "--requirements", "-r",
    default="shared/docs/requirements.md",
    help="requirements.mdのパス"
)
def plan_migration(requirements: str) -> None:
    """マイグレーション計画をプレビュー（Terraform plan相当）

    requirements.mdの変更を検出し、適用される変更を表示します。
    実際には適用されません。

    examples:
        cmw task plan
        cmw task plan -r docs/requirements.md
    """
    from .migration_orchestrator import MigrationOrchestrator
    from rich.console import Console

    project_path = Path.cwd()
    requirements_path = project_path / requirements

    if not requirements_path.exists():
        click.echo(f"❌ エラー: requirements.md が見つかりません: {requirements_path}", err=True)
        return

    console = Console()
    orchestrator = MigrationOrchestrator(project_path, console=console)

    try:
        # Dry-runモードで実行（planのみ、applyなし）
        result = orchestrator.execute_migration(
            requirements_path=requirements_path,
            dry_run=True
        )

        if result.no_changes:
            console.print("\n[dim]適用するには: cmw task apply[/dim]")

    except Exception as e:
        console.print(f"\n[red]❌ エラー: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


@task.command("apply")
@click.option(
    "--requirements", "-r",
    default="shared/docs/requirements.md",
    help="requirements.mdのパス"
)
@click.option(
    "--auto-approve",
    is_flag=True,
    help="確認なしで適用"
)
def apply_migration(requirements: str, auto_approve: bool) -> None:
    """マイグレーション計画を適用（Terraform apply相当）

    requirements.mdの変更を実際に適用します。

    examples:
        cmw task apply
        cmw task apply --auto-approve
    """
    from .migration_orchestrator import MigrationOrchestrator
    from rich.console import Console

    project_path = Path.cwd()
    requirements_path = project_path / requirements

    if not requirements_path.exists():
        click.echo(f"❌ エラー: requirements.md が見つかりません: {requirements_path}", err=True)
        return

    console = Console()
    orchestrator = MigrationOrchestrator(project_path, console=console)

    try:
        result = orchestrator.execute_migration(
            requirements_path=requirements_path,
            auto_approve=auto_approve
        )

        if not result.success and not result.cancelled and not result.no_changes:
            # エラー時は終了コード1
            import sys
            sys.exit(1)

    except Exception as e:
        console.print(f"\n[red]❌ エラー: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)


# 後方互換性: task のすべてのコマンドを tasks にもコピー
for name, cmd in task.commands.items():
    tasks.add_command(cmd, name=name)


def main() -> None:
    """CLIのエントリーポイント"""
    cli()


if __name__ == "__main__":
    cli()
