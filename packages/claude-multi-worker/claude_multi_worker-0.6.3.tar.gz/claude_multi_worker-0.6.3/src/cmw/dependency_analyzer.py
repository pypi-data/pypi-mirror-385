"""
依存関係解析機能

タスクの依存関係を解析し、実行可能なタスク、クリティカルパス、
ボトルネックなどを特定します。
"""

from typing import List, Dict, Any

from .models import Task, TaskStatus
from .graph_visualizer import GraphVisualizer


class DependencyAnalyzer:
    """タスク依存関係の高度な解析機能"""

    def __init__(self, tasks: List[Task]):
        """
        Args:
            tasks: タスクのリスト
        """
        self.tasks = {task.id: task for task in tasks}
        self.visualizer = GraphVisualizer(tasks)
        self.graph = self.visualizer.graph

    def get_executable_tasks(self) -> List[Task]:
        """
        今すぐ実行可能なタスクを取得
        (依存関係が全て完了しているタスク)

        Returns:
            実行可能なタスクのリスト
        """
        executable = []

        for task_id, task in self.tasks.items():
            # 既に完了または進行中のタスクは除外
            if task.status in [TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS]:
                continue

            # 依存関係が全て完了しているかチェック
            if self._are_dependencies_met(task):
                executable.append(task)

        # 優先度順にソート
        executable.sort(
            key=lambda t: (
                {"high": 0, "medium": 1, "low": 2}.get(t.priority.value, 99),
                self.get_blocking_count(t.id),  # ブロックしているタスク数
            ),
            reverse=True,
        )

        return executable

    def _are_dependencies_met(self, task: Task) -> bool:
        """タスクの依存関係が全て満たされているかチェック"""
        if not task.dependencies:
            return True

        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False

        return True

    def get_critical_path(self) -> Dict[str, Any]:
        """
        クリティカルパスを計算

        Returns:
            クリティカルパス情報 {
                'tasks': タスクIDのリスト,
                'total_duration': 推定合計時間,
                'bottlenecks': ボトルネックタスク
            }
        """
        path_ids = self.visualizer.get_critical_path()

        if not path_ids:
            return {
                "tasks": [],
                "total_duration": 0,
                "bottlenecks": [],
                "completion_time": "N/A",
            }

        # パス上のタスク情報を取得
        path_tasks = [self.tasks[task_id] for task_id in path_ids if task_id in self.tasks]

        # 推定時間を計算（タスクにestimated_hoursがあれば使用）
        total_duration = 0.0
        for task in path_tasks:
            # メタデータから推定時間を取得（デフォルト4時間）
            estimated = 4.0  # デフォルト
            total_duration += estimated

        # ボトルネックタスク（多くのタスクをブロックしているタスク）
        bottlenecks = []
        for task_id in path_ids:
            blocking_count = self.get_blocking_count(task_id)
            if blocking_count >= 3:  # 3タスク以上をブロックしていたらボトルネック
                bottlenecks.append(
                    {"task_id": task_id, "title": self.tasks[task_id].title, "blocking": blocking_count}
                )

        # 完了予測（既完了タスクの平均時間から推定）
        completion_days = total_duration / 8  # 1日8時間として計算

        return {
            "tasks": path_ids,
            "total_duration": total_duration,
            "bottlenecks": bottlenecks,
            "completion_days": completion_days,
            "task_details": [{"id": t.id, "title": t.title, "status": t.status.value} for t in path_tasks],
        }

    def get_blocking_count(self, task_id: str) -> int:
        """
        このタスクがブロックしているタスク数を取得
        (直接・間接的に依存しているタスクの総数)

        Args:
            task_id: タスクID

        Returns:
            ブロックしているタスク数
        """
        dependents = self.visualizer.get_dependent_tasks(task_id)
        return len(dependents)

    def get_next_tasks_recommendation(self, num_recommendations: int = 3) -> List[Dict[str, Any]]:
        """
        次に実行すべきタスクの推奨リストを取得

        Args:
            num_recommendations: 推奨するタスク数

        Returns:
            推奨タスク情報のリスト
        """
        executable = self.get_executable_tasks()
        critical_path_ids = set(self.visualizer.get_critical_path())

        recommendations = []
        for task in executable[:num_recommendations]:
            is_critical = task.id in critical_path_ids
            blocking_count = self.get_blocking_count(task.id)

            recommendations.append(
                {
                    "task_id": task.id,
                    "title": task.title,
                    "priority": task.priority.value,
                    "is_critical_path": is_critical,
                    "blocking_count": blocking_count,
                    "reason": self._get_recommendation_reason(task, is_critical, blocking_count),
                }
            )

        return recommendations

    def _get_recommendation_reason(self, task: Task, is_critical: bool, blocking_count: int) -> str:
        """推奨理由を生成"""
        reasons = []

        if is_critical:
            reasons.append("クリティカルパス上")

        if blocking_count > 0:
            reasons.append(f"{blocking_count}タスクをブロック中")

        if task.priority.value == "high":
            reasons.append("高優先度")

        return ", ".join(reasons) if reasons else "実行可能"

    def analyze_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        プロジェクトのボトルネックを分析

        Returns:
            ボトルネック情報のリスト
        """
        bottlenecks = []

        for task_id, task in self.tasks.items():
            blocking_count = self.get_blocking_count(task_id)

            # 3つ以上のタスクをブロックしている場合はボトルネック
            if blocking_count >= 3:
                bottlenecks.append(
                    {
                        "task_id": task_id,
                        "title": task.title,
                        "status": task.status.value,
                        "blocking_count": blocking_count,
                        "severity": self._get_bottleneck_severity(blocking_count, task.status),
                    }
                )

        # 深刻度順にソート
        severity_order = {"critical": 0, "high": 1, "medium": 2}
        bottlenecks.sort(key=lambda x: severity_order.get(str(x["severity"]), 99))

        return bottlenecks

    def _get_bottleneck_severity(self, blocking_count: int, status: TaskStatus) -> str:
        """ボトルネックの深刻度を判定"""
        if status in [TaskStatus.PENDING, TaskStatus.BLOCKED] and blocking_count >= 5:
            return "critical"
        elif status == TaskStatus.PENDING and blocking_count >= 3:
            return "high"
        else:
            return "medium"

    def get_parallel_execution_plan(self, num_workers: int = 2) -> Dict[str, Any]:
        """
        並行実行プランを生成

        Args:
            num_workers: ワーカー数

        Returns:
            並行実行プラン {
                'workers': [
                    {'id': 1, 'tasks': ['TASK-001', 'TASK-003']},
                    {'id': 2, 'tasks': ['TASK-002', 'TASK-004']}
                ],
                'estimated_completion': 推定完了時間,
                'efficiency': 効率（並行化による短縮率）
            }
        """
        parallel_groups = self.visualizer.get_parallel_groups()

        # ワーカーに割り当て
        workers: List[Dict[str, Any]] = [
            {"id": i + 1, "tasks": [], "estimated_hours": 0.0} for i in range(num_workers)
        ]

        for group in parallel_groups:
            # グループ内のタスクを各ワーカーに割り当て
            for i, task_id in enumerate(group):
                worker_idx = i % num_workers
                workers[worker_idx]["tasks"].append(task_id)
                workers[worker_idx]["estimated_hours"] += 4.0  # デフォルト4時間

        # 最も時間がかかるワーカーの時間が全体の完了時間
        estimated_completion = max((float(w["estimated_hours"]) for w in workers), default=0.0)

        # 効率計算（単一ワーカーとの比較）
        total_tasks = len(self.tasks)
        single_worker_time = total_tasks * 4.0  # 全タスクを1人でやった場合
        efficiency = (
            ((single_worker_time - estimated_completion) / single_worker_time * 100)
            if single_worker_time > 0
            else 0.0
        )

        return {
            "workers": workers,
            "estimated_completion_hours": estimated_completion,
            "estimated_completion_days": estimated_completion / 8,  # 1日8時間
            "efficiency_gain": round(efficiency, 1),
            "parallel_levels": len(parallel_groups),
        }

    def is_on_critical_path(self, task_id: str) -> bool:
        """タスクがクリティカルパス上にあるかチェック"""
        critical_path = self.visualizer.get_critical_path()
        return task_id in critical_path

    def get_task_impact_score(self, task_id: str) -> int:
        """
        タスクの影響度スコアを計算
        (ブロックしているタスク数 + クリティカルパス上なら+10)

        Args:
            task_id: タスクID

        Returns:
            影響度スコア
        """
        blocking_count = self.get_blocking_count(task_id)
        is_critical = self.is_on_critical_path(task_id)

        score = blocking_count
        if is_critical:
            score += 10

        return score

    def get_completion_forecast(self) -> Dict[str, Any]:
        """
        プロジェクト完了予測を計算

        Returns:
            完了予測情報
        """
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        in_progress_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        pending_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])

        progress_percent = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # クリティカルパス情報
        critical_info = self.get_critical_path()

        # 楽観的予測（並行実行フル活用）
        parallel_plan = self.get_parallel_execution_plan(num_workers=2)
        optimistic_days = parallel_plan["estimated_completion_days"]

        # 悲観的予測（クリティカルパス基準）
        pessimistic_days = critical_info["completion_days"]

        return {
            "total_tasks": total_tasks,
            "completed": completed_tasks,
            "in_progress": in_progress_tasks,
            "pending": pending_tasks,
            "progress_percent": round(progress_percent, 1),
            "optimistic_completion_days": round(optimistic_days, 1),
            "pessimistic_completion_days": round(pessimistic_days, 1),
            "critical_path_length": len(critical_info["tasks"]),
            "bottlenecks": len(self.analyze_bottlenecks()),
        }
