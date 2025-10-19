"""
タスクマイグレーション機能

requirements.mdの変更時に既存タスクを新しいタスクにマイグレーションします。
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from .models import Task, TaskStatus


class TaskMigrator:
    """タスクのマイグレーションを行うクラス"""

    def __init__(self, project_path: Path):
        """
        マイグレーターの初期化

        Args:
            project_path: プロジェクトのルートパス
        """
        self.project_path = project_path
        self.tasks_file = project_path / "shared" / "coordination" / "tasks.json"
        self.progress_file = project_path / "shared" / "coordination" / "progress.json"

    def migrate_tasks(
        self, old_tasks: List[Task], new_tasks: List[Task]
    ) -> Tuple[List[Task], Dict[str, str]]:
        """
        旧タスクから新タスクへの状態とアーティファクトをマイグレーション

        Args:
            old_tasks: 既存のタスクリスト
            new_tasks: 新しく生成されたタスクリスト

        Returns:
            (migrated_tasks, migration_map) タプル
            - migrated_tasks: マイグレーション後のタスクリスト
            - migration_map: 旧タスクID -> 新タスクIDのマッピング
        """
        migration_map = self._create_migration_map(old_tasks, new_tasks)
        migrated_tasks = []

        for new_task in new_tasks:
            # 対応する旧タスクを検索
            old_task_id = self._find_old_task_id(new_task, migration_map)

            if old_task_id:
                old_task = next((t for t in old_tasks if t.id == old_task_id), None)
                if old_task:
                    # 状態とアーティファクトを継承
                    new_task.status = old_task.status
                    new_task.artifacts = old_task.artifacts.copy()
                    new_task.completed_at = old_task.completed_at
                    new_task.started_at = old_task.started_at
                    new_task.failed_at = old_task.failed_at
                    new_task.error_message = old_task.error_message

            migrated_tasks.append(new_task)

        return migrated_tasks, migration_map

    def _create_migration_map(
        self, old_tasks: List[Task], new_tasks: List[Task]
    ) -> Dict[str, str]:
        """
        旧タスクと新タスクのマッピングを作成

        マッチング戦略:
        1. タイトルが完全一致
        2. タイトルが80%以上類似
        3. セクション番号が一致
        4. 対象ファイルが50%以上一致

        Returns:
            old_task_id -> new_task_id のマッピング
        """
        mapping = {}

        for old_task in old_tasks:
            best_match = None
            best_score = 0.0

            for new_task in new_tasks:
                if new_task.id in mapping.values():
                    continue  # 既にマッピング済み

                score = self._calculate_similarity(old_task, new_task)

                if score > best_score:
                    best_score = score
                    best_match = new_task

            # 閾値70%以上でマッチング
            if best_match and best_score >= 0.7:
                mapping[old_task.id] = best_match.id

        return mapping

    def _calculate_similarity(self, task1: Task, task2: Task) -> float:
        """
        2つのタスク間の類似度を計算

        Returns:
            類似度スコア (0.0 ~ 1.0)
        """
        score = 0.0
        weights = {
            "title": 0.4,
            "section": 0.3,
            "files": 0.2,
            "description": 0.1,
        }

        # 1. タイトルの類似度
        title_similarity = self._string_similarity(task1.title, task2.title)
        score += title_similarity * weights["title"]

        # 2. セクション番号の一致
        section1 = self._extract_section_number(task1.title)
        section2 = self._extract_section_number(task2.title)
        if section1 and section2 and section1 == section2:
            score += weights["section"]

        # 3. 対象ファイルの一致率
        if task1.target_files and task2.target_files:
            files1 = set(task1.target_files)
            files2 = set(task2.target_files)
            file_overlap = len(files1 & files2)
            file_union = len(files1 | files2)
            if file_union > 0:
                file_similarity = file_overlap / file_union
                score += file_similarity * weights["files"]

        # 4. 説明の類似度
        if task1.description and task2.description:
            desc_similarity = self._string_similarity(
                task1.description, task2.description
            )
            score += desc_similarity * weights["description"]

        return score

    def _string_similarity(self, str1: str, str2: str) -> float:
        """
        2つの文字列の類似度を計算（簡易的なレーベンシュタイン距離）

        Returns:
            類似度 (0.0 ~ 1.0)
        """
        if str1 == str2:
            return 1.0

        # 単純な文字一致率を計算
        str1_lower = str1.lower()
        str2_lower = str2.lower()

        if len(str1_lower) == 0 or len(str2_lower) == 0:
            return 0.0

        # 共通部分文字列の長さを計算
        common_chars = sum(
            1 for c in str1_lower if c in str2_lower
        )
        max_len = max(len(str1_lower), len(str2_lower))

        return common_chars / max_len

    def _extract_section_number(self, title: str) -> Optional[str]:
        """セクション番号を抽出（例: "7.1 認証" → "7.1"）"""
        import re

        match = re.match(r"^(\d+\.\d+)", title)
        if match:
            return match.group(1)
        return None

    def _find_old_task_id(
        self, new_task: Task, migration_map: Dict[str, str]
    ) -> Optional[str]:
        """
        新タスクに対応する旧タスクIDを検索

        Args:
            new_task: 新タスク
            migration_map: 旧ID -> 新IDのマッピング

        Returns:
            対応する旧タスクID（存在しない場合はNone）
        """
        for old_id, new_id in migration_map.items():
            if new_id == new_task.id:
                return old_id
        return None

    def save_migration_report(
        self, migration_map: Dict[str, str], output_path: Optional[Path] = None
    ) -> None:
        """
        マイグレーションレポートを保存

        Args:
            migration_map: 旧ID -> 新IDのマッピング
            output_path: 出力先パス（Noneの場合はプロジェクト内に保存）
        """
        if output_path is None:
            output_path = (
                self.project_path
                / "shared"
                / "coordination"
                / "migration_report.json"
            )

        report = {
            "migration_map": migration_map,
            "migrated_count": len(migration_map),
        }

        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
