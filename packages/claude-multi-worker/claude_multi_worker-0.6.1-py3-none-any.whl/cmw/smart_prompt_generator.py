"""
スマートプロンプト生成機能

依存関係、ファイル情報、requirements.mdの内容などを
統合して、より文脈豊かなプロンプトを自動生成します。
"""

from typing import List, Optional
from pathlib import Path

from .models import Task, TaskStatus
from .dependency_analyzer import DependencyAnalyzer
from .prompt_template import PromptTemplate


class SmartPromptGenerator:
    """文脈を理解したインテリジェントなプロンプト生成"""

    def __init__(self, tasks: List[Task], project_root: Optional[Path] = None):
        """
        Args:
            tasks: 全タスクのリスト
            project_root: プロジェクトルートディレクトリ
        """
        self.tasks = {task.id: task for task in tasks}
        self.task_list = tasks
        self.project_root = project_root or Path.cwd()
        self.analyzer = DependencyAnalyzer(tasks)
        self.base_generator = PromptTemplate(project_root)

    def generate(self, task_id: str) -> str:
        """
        スマートプロンプトを生成

        Args:
            task_id: タスクID

        Returns:
            生成されたプロンプト
        """
        task = self.tasks.get(task_id)
        if not task:
            return f"エラー: タスク {task_id} が見つかりません"

        sections = []

        # 1. タスク概要（重要度を強調）
        sections.append(self._build_enhanced_overview(task))

        # 2. 依存関係（前後のタスク）
        sections.append(self._build_enhanced_dependencies(task))

        # 3. 関連ファイル（推測含む）
        sections.append(self._build_file_section(task))

        # 4. requirements.md から該当部分を抽出
        sections.append(self._build_requirements_section(task))

        # 5. 実装ガイド
        sections.append(self._build_implementation_guide(task))

        # 6. 完了条件チェックリスト
        sections.append(self._build_checklist(task))

        # 7. テストコマンド
        sections.append(self._build_test_commands(task))

        # 8. 次のステップ
        sections.append(self._build_next_steps(task))

        # 9. 完了方法
        sections.append(self._build_completion_instructions())

        return "\n\n".join(filter(None, sections))

    def _build_enhanced_overview(self, task: Task) -> str:
        """強化されたタスク概要"""
        is_critical = self.analyzer.is_on_critical_path(task.id)
        blocking_count = self.analyzer.get_blocking_count(task.id)

        lines = [
            "╭" + "─" * 50 + "╮",
            f"│ 📋 タスク: {task.id} - {task.title}",
            "╰" + "─" * 50 + "╯",
            "",
            "┌─ 🎯 タスク概要 " + "─" * 30 + "┐",
            f"│ 優先度: {'🔴 高' if task.priority.value == 'high' else '🟡 中' if task.priority.value == 'medium' else '🟢 低'}",
            f"│ 担当: {task.assigned_to}",
        ]

        if is_critical:
            lines.append("│")
            lines.append("│ ⚠️  このタスクはクリティカルパス上にあります")
            lines.append("│     優先的に完了させてください")

        if blocking_count > 0:
            lines.append("│")
            lines.append(f"│ 🚧 このタスクは {blocking_count}個のタスク をブロック中")
            lines.append("│     他のタスクがこのタスクの完了を待っています")

        lines.append("└" + "─" * 48 + "┘")

        return "\n".join(lines)

    def _build_enhanced_dependencies(self, task: Task) -> str:
        """強化された依存関係セクション"""
        lines = [
            "┌─ 🔗 依存関係 " + "─" * 33 + "┐",
        ]

        # 前提タスク
        upstream = [self.tasks[dep_id] for dep_id in task.dependencies if dep_id in self.tasks]
        if upstream:
            lines.append("│ 前提タスク:")
            for dep_task in upstream:
                status_icon = self._get_status_icon(dep_task.status)
                lines.append(f"│   {status_icon} {dep_task.id}: {dep_task.title}")
        else:
            lines.append("│ 前提タスク: なし (すぐ開始可能)")

        lines.append("│")

        # このタスクの完了を待つタスク
        downstream_ids = self.analyzer.visualizer.get_dependent_tasks(task.id)
        if downstream_ids:
            lines.append("│ このタスクの完了を待つタスク:")
            for dep_id in list(downstream_ids)[:3]:  # 最大3件表示
                downstream_task: Optional[Task] = self.tasks.get(dep_id)
                if downstream_task:
                    lines.append(f"│   ├─ {downstream_task.id}: {downstream_task.title}")
            if len(downstream_ids) > 3:
                lines.append(f"│   └─ 他 {len(downstream_ids) - 3}件")

            # 次のクリティカルパスタスク
            critical_path = self.analyzer.visualizer.get_critical_path()
            try:
                current_idx = critical_path.index(task.id)
                if current_idx + 1 < len(critical_path):
                    next_critical = self.tasks[critical_path[current_idx + 1]]
                    lines.append("│")
                    lines.append(f"│ 💡 次のクリティカルパスタスク: {next_critical.id}")
            except (ValueError, IndexError):
                pass
        else:
            lines.append("│ 待機中のタスク: なし")

        lines.append("└" + "─" * 48 + "┘")

        return "\n".join(lines)

    def _build_file_section(self, task: Task) -> str:
        """ファイル関連セクション"""
        lines = [
            "┌─ 📁 関連ファイル " + "─" * 29 + "┐",
        ]

        if task.target_files:
            # 新規作成と既存修正を分類
            lines.append("│ 作成・編集が必要:")
            for file_path in task.target_files:
                full_path = self.project_root / file_path
                exists = full_path.exists()
                icon = "📝" if exists else "🆕"
                lines.append(f"│   {icon} {file_path}")
        else:
            lines.append("│ 対象ファイル: 指定なし")

        # requirements.md を参照ファイルとして追加
        req_path = self.project_root / "shared" / "docs" / "requirements.md"
        if req_path.exists():
            lines.append("│")
            lines.append("│ 参照ファイル:")
            lines.append("│   📖 shared/docs/requirements.md (仕様)")

        lines.append("└" + "─" * 48 + "┘")

        return "\n".join(lines)

    def _build_requirements_section(self, task: Task) -> str:
        """requirements.mdから関連部分を抽出"""
        req_path = self.project_root / "shared" / "docs" / "requirements.md"

        if not req_path.exists():
            return ""

        try:
            # requirements.mdの内容を読み込み
            req_path.read_text(encoding="utf-8")

            # タスクタイトルに関連する行を抽出（簡易実装）
            lines = [
                "┌─ 📝 実装ガイド (requirements.mdより) " + "─" * 5 + "┐",
                "│",
            ]

            # タスク説明を表示
            if task.description:
                for line in task.description.split("\n"):
                    lines.append(f"│ {line}")

            lines.append("│")
            lines.append("│ 詳細は requirements.md を参照してください")
            lines.append("└" + "─" * 48 + "┘")

            return "\n".join(lines)

        except Exception:
            return ""

    def _build_implementation_guide(self, task: Task) -> str:
        """実装ガイドセクション"""
        lines = [
            "┌─ 🛠️  実装手順 (推奨) " + "─" * 24 + "┐",
        ]

        # タスクのタグや種類から推奨手順を生成
        if "model" in task.assigned_to.lower() or "model" in task.title.lower():
            lines.extend([
                "│ 1. データモデルクラスを定義",
                "│ 2. バリデーションロジックを実装",
                "│ 3. ユニットテストを作成",
                "│ 4. マイグレーション生成（必要に応じて）",
            ])
        elif "api" in task.assigned_to.lower() or "api" in task.title.lower():
            lines.extend([
                "│ 1. APIエンドポイントを定義",
                "│ 2. リクエスト/レスポンススキーマを作成",
                "│ 3. ビジネスロジックを実装",
                "│ 4. エラーハンドリングを追加",
                "│ 5. APIテストを作成",
            ])
        elif "test" in task.assigned_to.lower():
            lines.extend([
                "│ 1. テストケースを洗い出し",
                "│ 2. テストフィクスチャを準備",
                "│ 3. 正常系テストを実装",
                "│ 4. 異常系テストを実装",
                "│ 5. カバレッジを確認",
            ])
        else:
            lines.extend([
                "│ 1. タスクの要件を確認",
                "│ 2. 必要なファイルを作成",
                "│ 3. 実装",
                "│ 4. テスト",
                "│ 5. 動作確認",
            ])

        lines.append("└" + "─" * 48 + "┘")

        return "\n".join(lines)

    def _build_checklist(self, task: Task) -> str:
        """完了条件チェックリスト"""
        lines = [
            "┌─ ✅ 完了条件チェックリスト " + "─" * 18 + "┐",
        ]

        if task.acceptance_criteria:
            for criterion in task.acceptance_criteria:
                lines.append(f"│ [ ] {criterion}")
        else:
            # デフォルトのチェックリスト
            lines.extend([
                "│ [ ] 対象ファイルを作成・編集",
                "│ [ ] コードが正しく動作",
                "│ [ ] テストが全てパス",
                "│ [ ] エラーハンドリングを実装",
            ])

        lines.append("└" + "─" * 48 + "┘")

        return "\n".join(lines)

    def _build_test_commands(self, task: Task) -> str:
        """テストコマンドセクション"""
        lines = [
            "┌─ 🧪 テストコマンド " + "─" * 26 + "┐",
        ]

        # テストファイルがあればそのパスを表示
        test_files = [f for f in task.target_files if "test" in f.lower()]

        if test_files:
            lines.append("│ # 該当テストのみ実行")
            for test_file in test_files:
                lines.append(f"│ pytest {test_file} -v")
            lines.append("│")

        lines.extend([
            "│ # 全テスト実行",
            "│ pytest -v",
            "│",
            "│ # カバレッジ確認",
            "│ pytest --cov=src --cov-report=term",
        ])

        lines.append("└" + "─" * 48 + "┘")

        return "\n".join(lines)

    def _build_next_steps(self, task: Task) -> str:
        """次のステップセクション"""
        # 次に実行可能になるタスクを取得
        downstream_ids = self.analyzer.visualizer.get_dependent_tasks(task.id)

        if not downstream_ids:
            return ""

        lines = [
            "┌─ 🔄 完了後の次ステップ " + "─" * 22 + "┐",
            "│ このタスク完了後、以下が実行可能になります:",
            "│",
        ]

        # 直接依存しているタスクのみ表示
        direct_deps = []
        for other_task in self.task_list:
            if task.id in other_task.dependencies:
                direct_deps.append(other_task)

        if direct_deps:
            # クリティカルパス上のタスクを優先表示
            critical_path = self.analyzer.visualizer.get_critical_path()
            critical_next = [t for t in direct_deps if t.id in critical_path]

            if critical_next:
                next_task = critical_next[0]
                lines.append(f"│ 1. [推奨] {next_task.id}: {next_task.title}")
                lines.append("│    → クリティカルパス上のタスク")
                lines.append(f"│    → cmw task prompt {next_task.id}")
                lines.append("│")

            # その他のタスク
            other_next = [t for t in direct_deps if t not in critical_next][:2]
            for i, next_task in enumerate(other_next, 2 if critical_next else 1):
                lines.append(f"│ {i}. {next_task.id}: {next_task.title}")

        lines.append("└" + "─" * 48 + "┘")

        return "\n".join(lines)

    def _build_completion_instructions(self) -> str:
        """完了方法の説明"""
        lines = [
            "┌─ 💾 作業を終えたら " + "─" * 25 + "┐",
            "│ # タスクを完了としてマーク",
            "│ cmw task complete " + self.tasks[list(self.tasks.keys())[0]].id,
            "│",
            "│ # 生成ファイルも記録する場合",
            "│ cmw task complete <TASK-ID> --artifacts '[\"file1.py\", \"file2.py\"]'",
            "└" + "─" * 48 + "┘",
        ]

        return "\n".join(lines)

    def _get_status_icon(self, status: TaskStatus) -> str:
        """ステータスアイコンを取得"""
        icons = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.BLOCKED: "🚫",
        }
        return icons.get(status, "❓")
