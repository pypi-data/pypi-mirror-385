"""
State Reconciliation Module

Kubernetes風の状態調整を実装
Desired State (requirements.md) と Actual State (tasks.json + progress.json) の差分を検出・調整
"""

from typing import List, Tuple, Optional, Dict
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from .models import Task, TaskStatus
from .task_migrator import TaskMigrator
from .requirements_parser import RequirementsParser
from .coordinator import Coordinator


class DiffActionType(str, Enum):
    """差分アクションの種類"""
    ADD = "add"              # 新規タスク追加
    MIGRATE = "migrate"      # 既存タスク状態を新タスクに引き継ぎ
    UPDATE = "update"        # タスク内容を更新（大幅変更）
    DEPRECATE = "deprecate"  # タスクを非推奨化
    NO_CHANGE = "no_change"  # 変更なし


@dataclass
class DiffAction:
    """個別の差分アクション"""
    action_type: DiffActionType
    old_task: Optional[Task] = None
    new_task: Optional[Task] = None
    similarity: float = 0.0
    reason: str = ""


@dataclass
class StateDiff:
    """
    Desired StateとActual Stateの差分

    Terraform plan風の差分表現
    """
    actions: List[DiffAction] = field(default_factory=list)

    def add_action(self, action: DiffAction) -> None:
        """アクションを追加"""
        self.actions.append(action)

    def has_changes(self) -> bool:
        """変更があるか"""
        return any(
            a.action_type != DiffActionType.NO_CHANGE
            for a in self.actions
        )

    def count_by_type(self, action_type: DiffActionType) -> int:
        """指定タイプのアクション数"""
        return sum(1 for a in self.actions if a.action_type == action_type)

    def summary(self) -> str:
        """
        Terraform plan風のサマリー

        Returns:
            "Plan: 7 to add, 2 to change, 0 to deprecate"
        """
        add_count = self.count_by_type(DiffActionType.ADD)
        migrate_count = self.count_by_type(DiffActionType.MIGRATE)
        update_count = self.count_by_type(DiffActionType.UPDATE)
        deprecate_count = self.count_by_type(DiffActionType.DEPRECATE)

        change_count = migrate_count + update_count

        return f"Plan: {add_count} to add, {change_count} to change, {deprecate_count} to deprecate"

    def get_additions(self) -> List[DiffAction]:
        """追加アクションのみ取得"""
        return [a for a in self.actions if a.action_type == DiffActionType.ADD]

    def get_migrations(self) -> List[DiffAction]:
        """マイグレーションアクションのみ取得"""
        return [a for a in self.actions if a.action_type == DiffActionType.MIGRATE]

    def get_updates(self) -> List[DiffAction]:
        """更新アクションのみ取得"""
        return [a for a in self.actions if a.action_type == DiffActionType.UPDATE]

    def get_deprecations(self) -> List[DiffAction]:
        """非推奨化アクションのみ取得"""
        return [a for a in self.actions if a.action_type == DiffActionType.DEPRECATE]


@dataclass
class ReconciliationResult:
    """状態調整の結果"""
    success: bool = False
    no_changes: bool = False
    cancelled: bool = False
    diff: Optional[StateDiff] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # 統計情報
    tasks_added: int = 0
    tasks_migrated: int = 0
    tasks_updated: int = 0
    tasks_deprecated: int = 0


class StateReconciler:
    """
    状態調整クラス（Kubernetes Reconciliation Pattern）

    Reconciliation Loop:
    1. Observe (観測)
    2. Diff (差分計算)
    3. Act (アクション実行) ← このクラスは差分計算のみ、実行はMigrationOrchestratorで
    """

    def __init__(self, project_path: Path):
        """
        初期化

        Args:
            project_path: プロジェクトのルートパス
        """
        self.project_path = project_path
        self.requirements_path = project_path / "shared" / "docs" / "requirements.md"

        self.parser = RequirementsParser()
        self.migrator = TaskMigrator(project_path)
        self.coordinator = Coordinator(project_path)

    def compute_diff(
        self,
        requirements_path: Optional[Path] = None
    ) -> StateDiff:
        """
        Desired StateとActual Stateの差分を計算

        Args:
            requirements_path: requirements.mdのパス（Noneの場合はデフォルト）

        Returns:
            StateDiff: 差分情報
        """
        if requirements_path is None:
            requirements_path = self.requirements_path

        # Step 1: Observe - 望ましい状態と現在の状態を観測
        desired_tasks = self._observe_desired_state(requirements_path)
        current_tasks = self._observe_actual_state()

        # Step 2: Diff - 差分を計算
        diff = self._calculate_diff(desired_tasks, current_tasks)

        return diff

    def _observe_desired_state(self, requirements_path: Path) -> List[Task]:
        """
        Desired Stateを観測（requirements.mdから生成）

        Args:
            requirements_path: requirements.mdのパス

        Returns:
            List[Task]: 望ましいタスクリスト
        """
        return self.parser.parse(requirements_path)

    def _observe_actual_state(self) -> List[Task]:
        """
        Actual Stateを観測（tasks.json + progress.json）

        Returns:
            List[Task]: 現在のタスクリスト（状態含む）
        """
        return list(self.coordinator.tasks.values())

    def _calculate_diff(
        self,
        desired_tasks: List[Task],
        current_tasks: List[Task]
    ) -> StateDiff:
        """
        差分を計算

        アルゴリズム:
        1. TaskMigratorでマッチングマップ作成（類似度70%以上）
        2. 各desired taskについて:
           - マッチあり + 類似度高い → MIGRATE（状態引き継ぎ）
           - マッチあり + 類似度低い → UPDATE（内容変更）
           - マッチなし → ADD（新規追加）
        3. 各current taskについて:
           - マッチなし → DEPRECATE（削除）

        Args:
            desired_tasks: 望ましいタスクリスト
            current_tasks: 現在のタスクリスト

        Returns:
            StateDiff: 差分
        """
        diff = StateDiff()

        # マッチングマップを作成（old_id -> new_id）
        migration_map = self.migrator._create_migration_map(current_tasks, desired_tasks)

        # 逆マップも作成（new_id -> old_id）
        reverse_map = {new_id: old_id for old_id, new_id in migration_map.items()}

        # Desired tasksを処理
        for desired_task in desired_tasks:
            if desired_task.id in reverse_map:
                # マッチした既存タスクがある
                old_task_id = reverse_map[desired_task.id]
                old_task = next((t for t in current_tasks if t.id == old_task_id), None)

                if old_task:
                    # 類似度を計算
                    similarity = self.migrator._calculate_similarity(old_task, desired_task)

                    if self._has_significant_changes(old_task, desired_task):
                        # 大幅な変更 → UPDATE
                        diff.add_action(DiffAction(
                            action_type=DiffActionType.UPDATE,
                            old_task=old_task,
                            new_task=desired_task,
                            similarity=similarity,
                            reason=self._describe_changes(old_task, desired_task)
                        ))
                    else:
                        # 軽微な変更または変更なし → MIGRATE
                        diff.add_action(DiffAction(
                            action_type=DiffActionType.MIGRATE,
                            old_task=old_task,
                            new_task=desired_task,
                            similarity=similarity,
                            reason="状態を引き継ぎ"
                        ))
            else:
                # マッチなし → 新規タスク
                diff.add_action(DiffAction(
                    action_type=DiffActionType.ADD,
                    new_task=desired_task,
                    reason="新規タスク"
                ))

        # Current tasksでマッチしなかったものを処理
        for current_task in current_tasks:
            if current_task.id not in migration_map:
                # マッチなし → 非推奨化
                diff.add_action(DiffAction(
                    action_type=DiffActionType.DEPRECATE,
                    old_task=current_task,
                    reason="requirements.mdから削除"
                ))

        return diff

    def _has_significant_changes(self, old_task: Task, new_task: Task) -> bool:
        """
        重大な変更があるか判定

        判定基準:
        - タイトルが50%以上異なる
        - 対象ファイルが50%以上異なる
        - 依存関係が大幅に変更（完了済みタスクの場合は警告対象）

        Args:
            old_task: 旧タスク
            new_task: 新タスク

        Returns:
            bool: 重大な変更がある場合True
        """
        # タイトルの類似度
        title_similarity = self.migrator._string_similarity(old_task.title, new_task.title)
        if title_similarity < 0.5:
            return True

        # ファイルの重複率
        files1 = set(old_task.target_files)
        files2 = set(new_task.target_files)
        if files1 and files2:
            overlap = len(files1 & files2) / len(files1 | files2)
            if overlap < 0.5:
                return True

        # 依存関係の変更（完了済みタスクの場合は重大）
        if old_task.status == TaskStatus.COMPLETED:
            if set(old_task.dependencies) != set(new_task.dependencies):
                return True

        return False

    def _describe_changes(self, old_task: Task, new_task: Task) -> str:
        """
        変更内容を説明

        Args:
            old_task: 旧タスク
            new_task: 新タスク

        Returns:
            str: 変更内容の説明
        """
        changes = []

        # タイトル変更
        if old_task.title != new_task.title:
            changes.append(f"タイトル: '{old_task.title}' → '{new_task.title}'")

        # 依存関係変更
        old_deps = set(old_task.dependencies)
        new_deps = set(new_task.dependencies)
        if old_deps != new_deps:
            added = new_deps - old_deps
            removed = old_deps - new_deps
            if added:
                changes.append(f"依存追加: {', '.join(added)}")
            if removed:
                changes.append(f"依存削除: {', '.join(removed)}")

        # ファイル変更
        old_files = set(old_task.target_files)
        new_files = set(new_task.target_files)
        if old_files != new_files:
            added = new_files - old_files
            removed = old_files - new_files
            if added:
                changes.append(f"ファイル追加: {', '.join(list(added)[:3])}")
            if removed:
                changes.append(f"ファイル削除: {', '.join(list(removed)[:3])}")

        return "; ".join(changes) if changes else "軽微な変更"
