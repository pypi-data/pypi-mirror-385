"""
requirements.mdを解析してタスクを自動生成するモジュール

このモジュールは、Markdown形式のrequirements.mdを解析し、
タスク定義(tasks.json)を自動生成します。
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re

from .models import Task, Priority
from .dependency_validator import DependencyValidator
from .task_filter import TaskFilter


class RequirementsParser:
    """requirements.mdを解析してタスクを自動生成"""

    def __init__(self) -> None:
        self.task_counter = 0
        self.validator = DependencyValidator()
        self.task_filter = TaskFilter()

    def parse(self, requirements_path: Path) -> List[Task]:
        """
        Markdownファイルを解析してタスクリストを生成

        Args:
            requirements_path: requirements.mdのパス

        Returns:
            生成されたタスクのリスト
        """
        content = self._load_requirements(requirements_path)
        sections = self._extract_sections(content)
        tasks = self._generate_tasks_from_sections(sections)
        tasks = self._filter_non_tasks(tasks)
        tasks = self._infer_dependencies(tasks)
        tasks = self._detect_and_fix_cycles(tasks)
        return tasks

    def _load_requirements(self, requirements_path: Path) -> str:
        """requirements.mdを読み込む"""
        if not requirements_path.exists():
            raise FileNotFoundError(f"Requirements file not found: {requirements_path}")
        return requirements_path.read_text(encoding="utf-8")

    def _generate_tasks_from_sections(self, sections: List[Dict]) -> List[Task]:
        """セクションからタスクリストを生成"""
        tasks = []
        for section in sections:
            # メインタスクを生成
            if section["criteria"] or section["technical_notes"]:
                task = self._section_to_task(section)
                if task:
                    tasks.append(task)

            # サブセクションからタスクを生成
            for subsection in section["subsections"]:
                subtask = self._subsection_to_task(subsection, section)
                if subtask:
                    tasks.append(subtask)
        return tasks

    def _filter_non_tasks(self, tasks: List[Task]) -> List[Task]:
        """非タスク項目をフィルタリングして実装タスクのみ返す"""
        all_items = tasks
        tasks, non_tasks = self.task_filter.filter_tasks(all_items)

        if non_tasks:
            self._print_non_task_report(non_tasks, tasks)

        return tasks

    def _print_non_task_report(self, non_tasks: List[Task], tasks: List[Task]) -> None:
        """非タスク項目のレポートを表示"""
        print(f"\n📋 {len(non_tasks)}件の非タスク項目を検出:")
        for non_task in non_tasks:
            print(f"  - {non_task.id}: {non_task.title}")

        print("\n💡 これらは実装タスクではなく参照情報です")
        print(f"✅ {len(tasks)}個の実装タスクを生成しました\n")

    def _detect_and_fix_cycles(self, tasks: List[Task]) -> List[Task]:
        """循環依存を検出して自動修正"""
        cycles = self.validator.detect_cycles(tasks)

        if not cycles:
            return tasks

        self._print_cycles_report(cycles)
        suggestions = self.validator.suggest_fixes(cycles, tasks)
        self._print_fix_suggestions(suggestions)

        print("\n🔧 自動修正を適用中...")
        tasks = self.validator.auto_fix_cycles(tasks, cycles, auto_apply=True)

        self._verify_cycles_fixed(tasks)
        return tasks

    def _print_cycles_report(self, cycles: List[List[Tuple[str, str]]]) -> None:
        """循環依存のレポートを表示"""
        print(f"\n⚠️  {len(cycles)}件の循環依存を検出しました:")
        for i, cycle in enumerate(cycles, 1):
            # cycleはエッジのリスト [(from, to), ...]
            nodes = [edge[0] for edge in cycle]
            print(f"  {i}. {' ↔ '.join(nodes)}")

    def _print_fix_suggestions(self, suggestions: List[Dict]) -> None:
        """修正提案を表示"""
        print("\n💡 推奨される修正:")
        for suggestion in suggestions:
            for fix in suggestion["suggestions"][:1]:  # 最良の提案のみ表示
                print(f"  - {fix['from_task']} → {fix['to_task']} を削除")
                print(f"    理由: {fix['reason']}")
                print(f"    信頼度: {fix['confidence']:.0%}")

    def _verify_cycles_fixed(self, tasks: List[Task]) -> None:
        """循環依存が修正されたか確認"""
        remaining_cycles = self.validator.detect_cycles(tasks)
        if remaining_cycles:
            print(f"\n⚠️  {len(remaining_cycles)}件の循環依存が残っています")
            print("   手動での確認と修正が必要です")
        else:
            print("\n✅ 全ての循環依存を解決しました")

    def _extract_sections(self, content: str) -> List[Dict]:
        """
        Markdownからセクションを抽出

        戦略:
        - ## レベルの見出しをメインタスクとして認識
        - ### レベルの見出しをサブタスクとして認識
        - リストアイテムを受け入れ基準として抽出
        - コードブロックを技術仕様として抽出
        """
        from typing import Any

        sections: List[Dict[str, Any]] = []
        current_section: Optional[Dict[str, Any]] = None
        current_subsection: Optional[Dict[str, Any]] = None
        in_code_block = False

        for line in content.split("\n"):
            # コードブロックの開始/終了
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            # H2見出し = 新しいメインタスク
            if line.startswith("## "):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "level": 2,
                    "title": line[3:].strip(),
                    "subsections": [],
                    "criteria": [],
                    "technical_notes": [],
                }
                current_subsection = None

            # H3見出し = サブタスク
            elif line.startswith("### ") and current_section:
                current_subsection = {
                    "level": 3,
                    "title": line[4:].strip(),
                    "criteria": [],
                    "parent_title": current_section["title"],
                }
                current_section["subsections"].append(current_subsection)

            # リスト項目 = 受け入れ基準
            elif line.strip().startswith("-") and current_section:
                criterion = line.strip()[1:].strip()
                if criterion:  # 空行を除外
                    if current_subsection:
                        current_subsection["criteria"].append(criterion)
                    else:
                        current_section["criteria"].append(criterion)

        if current_section:
            sections.append(current_section)

        return sections

    def _section_to_task(self, section: Dict) -> Optional[Task]:
        """セクションをTaskオブジェクトに変換"""
        # タスクIDを生成
        self.task_counter += 1
        task_id = f"TASK-{self.task_counter:03d}"

        # target_filesを推論
        target_files = self._infer_target_files(section["title"], section["criteria"])

        if not target_files:
            # ファイルが推論できない場合はスキップ
            return None

        # 優先度を推論
        priority = self._infer_priority(section["title"])

        # 説明を生成
        description = self._generate_description(section)

        return Task(
            id=task_id,
            title=section["title"],
            description=description,
            target_files=target_files,
            acceptance_criteria=section["criteria"],
            priority=priority,
            dependencies=[],  # 後で推論
            assigned_to=self._infer_assigned_to(target_files),
        )

    def _subsection_to_task(self, subsection: Dict, parent_section: Dict) -> Optional[Task]:
        """サブセクションをTaskオブジェクトに変換"""
        self.task_counter += 1
        task_id = f"TASK-{self.task_counter:03d}"

        # サブセクションのコンテキストを考慮
        combined_title = f"{parent_section['title']} - {subsection['title']}"
        target_files = self._infer_target_files(combined_title, subsection["criteria"])

        if not target_files:
            return None

        priority = self._infer_priority(subsection["title"])

        return Task(
            id=task_id,
            title=subsection["title"],
            description=f"{parent_section['title']}の一部として{subsection['title']}を実装する",
            target_files=target_files,
            acceptance_criteria=subsection["criteria"],
            priority=priority,
            dependencies=[],
            assigned_to=self._infer_assigned_to(target_files),
        )

    def _infer_target_files(self, title: str, criteria: List[str]) -> List[str]:
        """
        タイトルと受け入れ基準からtarget_filesを推論

        戦略:
        1. エンドポイント記述から対応するルーターファイルを推論
        2. モデル定義からモデルファイルを推論
        3. データベース記述からdatabase.pyを推論
        4. テスト記述からテストファイルを推論
        """
        files: set[str] = set()
        content = title + " " + " ".join(criteria)
        content_lower = content.lower()

        # 各ファイルタイプの検出ロジックを実行
        self._detect_router_files(content, content_lower, files)
        self._detect_backend_files(content_lower, files)
        self._detect_test_files(content_lower, files)
        self._detect_documentation_files(content_lower, files)

        return sorted(files)

    def _detect_router_files(self, content: str, content_lower: str, files: set[str]) -> None:
        """エンドポイント/ルーターファイルを検出"""
        if not re.search(r"POST|GET|PUT|DELETE|PATCH|エンドポイント|API", content):
            return

        if any(kw in content for kw in ["/auth", "認証", "ログイン", "登録"]):
            files.add("backend/routers/auth.py")
        elif "/task" in content or ("タスク" in content and "エンドポイント" in content):
            files.add("backend/routers/tasks.py")
        else:
            # 一般的なルーターファイル
            endpoint_match = re.search(r"/([\w-]+)", content)
            if endpoint_match:
                resource = endpoint_match.group(1)
                files.add(f"backend/routers/{resource}.py")

    def _detect_backend_files(self, content_lower: str, files: set[str]) -> None:
        """バックエンドファイル（models, database, schemasなど）を検出"""
        # モデル検出
        if any(kw in content_lower for kw in ["モデル", "model", "データモデル", "orm"]):
            files.add("backend/models.py")

        # データベース検出
        if any(kw in content_lower for kw in ["データベース", "database", "db設定", "sqlalchemy"]):
            files.add("backend/database.py")

        # スキーマ検出
        if any(kw in content_lower for kw in ["スキーマ", "schema", "pydantic", "バリデーション"]):
            files.add("backend/schemas.py")

        # 認証ユーティリティ検出
        if any(kw in content_lower for kw in ["jwt", "トークン", "パスワード", "ハッシュ", "bcrypt"]):
            if "エンドポイント" not in content_lower:  # エンドポイントでない場合
                files.add("backend/auth.py")

        # 依存関係/ミドルウェア検出
        if any(kw in content_lower for kw in ["ミドルウェア", "middleware", "依存関係", "dependencies"]):
            files.add("backend/dependencies.py")

        # メインアプリケーション検出
        if any(kw in content_lower for kw in ["fastapi", "アプリケーション設定", "main.py", "cors"]):
            files.add("backend/main.py")

    def _detect_test_files(self, content_lower: str, files: set[str]) -> None:
        """テストファイルを検出"""
        if not any(kw in content_lower for kw in ["テスト", "test"]):
            return

        if "認証" in content_lower or "auth" in content_lower:
            files.add("tests/test_auth_endpoints.py")
        elif "タスク" in content_lower and ("api" in content_lower or "エンドポイント" in content_lower):
            files.add("tests/test_tasks_endpoints.py")
        else:
            files.add("tests/test_integration.py")

    def _detect_documentation_files(self, content_lower: str, files: set[str]) -> None:
        """ドキュメントファイルを検出"""
        # requirements.txt検出
        if any(kw in content_lower for kw in ["requirements", "依存パッケージ", "パッケージ"]):
            files.add("requirements.txt")

        # README検出
        if any(kw in content_lower for kw in ["readme", "ドキュメント", "セットアップ手順"]):
            files.add("README.md")

    def _infer_priority(self, title: str) -> Priority:
        """タイトルから優先度を推論"""
        title_lower = title.lower()

        # 高優先度キーワード
        high_keywords = [
            "データベース",
            "database",
            "モデル",
            "model",
            "認証",
            "auth",
            "requirements",
            "セキュリティ",
            "security",
        ]
        if any(keyword in title_lower for keyword in high_keywords):
            return Priority.HIGH

        # 低優先度キーワード
        low_keywords = ["readme", "ドキュメント", "documentation", "削除", "delete"]
        if any(keyword in title_lower for keyword in low_keywords):
            return Priority.LOW

        # デフォルトは中優先度
        return Priority.MEDIUM

    def _generate_description(self, section: Dict) -> str:
        """セクションから説明を生成"""
        if section["criteria"]:
            title_str = str(section["title"])
            return f"{title_str}を実装する"
        return str(section["title"])

    def _infer_assigned_to(self, target_files: List[str]) -> str:
        """ターゲットファイルから担当を推論"""
        files_str = " ".join(target_files)

        if "tests/" in files_str:
            return "testing"
        elif "backend/" in files_str:
            return "backend"
        elif "frontend/" in files_str:
            return "frontend"
        elif "README" in files_str or ".md" in files_str:
            return "documentation"
        else:
            return "backend"

    def _infer_dependencies(self, tasks: List[Task]) -> List[Task]:
        """
        タスク間の依存関係を推論

        戦略:
        1. ファイルベース依存: 同じファイルを編集するタスクは順序付け
        2. レイヤー依存: models → schemas → routers の順序
        3. 機能依存: 認証 → 認証が必要な機能
        """
        # タスクをIDでマッピング
        {task.id: task for task in tasks}

        # ファイルごとのタスクをグルーピング
        file_to_tasks: Dict[str, List[str]] = {}
        for task in tasks:
            for file in task.target_files:
                if file not in file_to_tasks:
                    file_to_tasks[file] = []
                file_to_tasks[file].append(task.id)

        # レイヤー定義（数値が小さいほど先に実行）
        layer_order = {
            "requirements.txt": 0,
            "database.py": 1,
            "models.py": 2,
            "schemas.py": 3,
            "auth.py": 4,
            "dependencies.py": 5,
            "routers/auth.py": 6,
            "routers/": 7,
            "main.py": 8,
            "tests/": 9,
            "README.md": 10,
        }

        for task in tasks:
            task_layer = self._get_task_layer(task, layer_order)

            for other_task in tasks:
                if task.id == other_task.id:
                    continue

                other_layer = self._get_task_layer(other_task, layer_order)

                # 下位レイヤーが依存元
                if other_layer < task_layer:
                    # ファイルが関連している場合のみ依存追加
                    if self._has_file_relation(task, other_task):
                        if other_task.id not in task.dependencies:
                            task.dependencies.append(other_task.id)

            # 同じファイルを編集するタスクの順序付け
            for file in task.target_files:
                if file in file_to_tasks:
                    earlier_tasks = [
                        tid
                        for tid in file_to_tasks[file]
                        if tid != task.id and self._is_earlier_task(tid, task.id)
                    ]
                    for earlier_id in earlier_tasks:
                        if earlier_id not in task.dependencies:
                            task.dependencies.append(earlier_id)

        return tasks

    def _get_task_layer(self, task: Task, layer_order: Dict[str, int]) -> int:
        """タスクのレイヤーを取得"""
        max_layer = 0
        for file in task.target_files:
            for pattern, layer in layer_order.items():
                if pattern in file:
                    max_layer = max(max_layer, layer)
        return max_layer

    def _has_file_relation(self, task1: Task, task2: Task) -> bool:
        """2つのタスクのファイルが関連しているか判定"""
        # 同じファイルを編集
        if set(task1.target_files) & set(task2.target_files):
            return True

        # モデルとスキーマの関係
        has_models = any("models.py" in f for f in task2.target_files)
        has_schemas = any("schemas.py" in f for f in task1.target_files)
        if has_models and has_schemas:
            return True

        # データベースとモデルの関係
        has_database = any("database.py" in f for f in task2.target_files)
        has_models_or_schemas = any(
            "models.py" in f or "schemas.py" in f for f in task1.target_files
        )
        if has_database and has_models_or_schemas:
            return True

        # 認証ユーティリティと認証エンドポイントの関係
        has_auth_util = any("auth.py" in f and "routers" not in f for f in task2.target_files)
        has_auth_router = any("routers/auth.py" in f for f in task1.target_files)
        if has_auth_util and has_auth_router:
            return True

        # スキーマとエンドポイントの関係
        has_schemas = any("schemas.py" in f for f in task2.target_files)
        has_router = any("routers/" in f for f in task1.target_files)
        if has_schemas and has_router:
            return True

        return False

    def _is_earlier_task(self, task_id1: str, task_id2: str) -> bool:
        """タスクID1がタスクID2より前かどうか"""
        # TASK-001, TASK-002などのID形式を想定
        try:
            num1 = int(task_id1.split("-")[1])
            num2 = int(task_id2.split("-")[1])
            return num1 < num2
        except (IndexError, ValueError):
            return False
