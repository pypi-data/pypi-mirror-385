"""
依存関係推薦システム

タスクのタイトル、説明、対象ファイルから適切な依存関係を推薦します。
"""

from typing import List, Dict, Tuple
from .models import Task, Priority


class DependencyRecommender:
    """依存関係の推薦を行うクラス"""

    def __init__(self, tasks: List[Task]):
        """
        推薦システムの初期化

        Args:
            tasks: 全タスクのリスト
        """
        self.tasks = tasks
        self.task_dict = {t.id: t for t in tasks}

    def recommend_dependencies(
        self, task: Task, max_recommendations: int = 5
    ) -> List[Tuple[str, float, str]]:
        """
        タスクに対する依存関係の推薦

        Args:
            task: 対象タスク
            max_recommendations: 最大推薦数

        Returns:
            (task_id, confidence, reason) のリスト
        """
        recommendations = []

        for candidate in self.tasks:
            if candidate.id == task.id:
                continue

            # 既に依存関係として設定されている場合はスキップ
            if candidate.id in task.dependencies:
                continue

            confidence, reason = self._calculate_confidence(task, candidate)

            if confidence > 0.3:  # 閾値30%以上のみ推薦
                recommendations.append((candidate.id, confidence, reason))

        # 信頼度の高い順にソート
        recommendations.sort(key=lambda x: x[1], reverse=True)

        return recommendations[:max_recommendations]

    def _calculate_confidence(self, task: Task, candidate: Task) -> Tuple[float, str]:
        """
        依存関係の信頼度を計算

        Returns:
            (confidence, reason) タプル
        """
        confidence = 0.0
        reasons = []

        # 1. セクション番号による判定（最重要）
        task_section = self._extract_section_number(task.title)
        cand_section = self._extract_section_number(candidate.title)

        if task_section and cand_section:
            task_chapter = int(task_section.split(".")[0])
            cand_chapter = int(cand_section.split(".")[0])

            # 同じ章で、候補が前のセクションの場合
            if task_chapter == cand_chapter and cand_section < task_section:
                confidence += 0.8
                reasons.append(f"同じ章の前セクション ({cand_section} < {task_section})")

            # 前の章の場合
            elif cand_chapter < task_chapter:
                confidence += 0.5
                reasons.append(f"前の章 (第{cand_chapter}章 → 第{task_chapter}章)")

        # 2. ファイルの依存関係による判定
        file_overlap = set(task.target_files) & set(candidate.target_files)
        if file_overlap:
            confidence += 0.4
            reasons.append(f"共通ファイル: {', '.join(file_overlap)}")

        # 候補のファイルがタスクのファイルに含まれる場合（layerの依存）
        if candidate.target_files:
            for cand_file in candidate.target_files:
                for task_file in task.target_files:
                    # models.py → schemas.py → routers/ のような依存
                    if self._is_layer_dependency(cand_file, task_file):
                        confidence += 0.3
                        reasons.append(f"レイヤー依存: {cand_file} → {task_file}")

        # 3. キーワードによる判定
        task_keywords = self._extract_keywords(task.title, task.description)
        cand_keywords = self._extract_keywords(candidate.title, candidate.description)

        keyword_overlap = task_keywords & cand_keywords
        if keyword_overlap:
            confidence += 0.2 * min(len(keyword_overlap) / 3, 1.0)
            reasons.append(f"共通キーワード: {', '.join(list(keyword_overlap)[:3])}")

        # 4. 優先度による判定（HIGHやCRITICALは先に実行すべき）
        if candidate.priority in [Priority.HIGH, Priority.CRITICAL]:
            if task.priority in [Priority.LOW, Priority.MEDIUM]:
                confidence += 0.1
                reasons.append(f"候補の優先度が高い ({candidate.priority.value})")

        # 5. 特定パターンの判定
        patterns = [
            ("定義", "実装", 0.6),
            ("モデル", "API", 0.5),
            ("API", "UI", 0.5),
            ("データベース", "ビジネスロジック", 0.4),
            ("認証", "認可", 0.3),
            ("基本機能", "応用機能", 0.4),
            ("設計", "実装", 0.5),
            ("実装", "テスト", 0.3),
            ("テスト", "デプロイ", 0.3),
        ]

        for pattern_from, pattern_to, pattern_conf in patterns:
            if pattern_from in candidate.title and pattern_to in task.title:
                confidence += pattern_conf
                reasons.append(f"パターンマッチ: {pattern_from} → {pattern_to}")

        # 理由を結合
        reason = "; ".join(reasons) if reasons else "関連性が検出されました"

        # 信頼度を0.0～1.0にキャップ
        confidence = min(confidence, 1.0)

        return confidence, reason

    def _extract_section_number(self, title: str) -> str:
        """セクション番号を抽出（例: "7.1 認証" → "7.1"）"""
        import re

        match = re.match(r"^(\d+\.\d+)", title)
        if match:
            return match.group(1)
        return ""

    def _is_layer_dependency(self, file1: str, file2: str) -> bool:
        """
        ファイル間にレイヤー依存があるかチェック

        例: models.py → schemas.py, schemas.py → routers/
        """
        layer_order = [
            "models.py",
            "database.py",
            "schemas.py",
            "crud.py",
            "auth.py",
            "routers/",
            "main.py",
        ]

        try:
            idx1 = next(
                i for i, layer in enumerate(layer_order) if layer in file1
            )
            idx2 = next(
                i for i, layer in enumerate(layer_order) if layer in file2
            )
            return idx1 < idx2
        except StopIteration:
            return False

    def _extract_keywords(self, title: str, description: str) -> set:
        """タイトルと説明から重要なキーワードを抽出"""
        text = f"{title} {description}".lower()

        # 技術的なキーワード
        keywords = {
            "api",
            "認証",
            "認可",
            "データベース",
            "モデル",
            "スキーマ",
            "バリデーション",
            "セキュリティ",
            "テスト",
            "デプロイ",
            "ui",
            "フロントエンド",
            "バックエンド",
            "ミドルウェア",
            "ルーティング",
            "crud",
            "rest",
            "graphql",
            "websocket",
            "キャッシュ",
            "ログ",
            "エラー処理",
            "最適化",
            "パフォーマンス",
            "docker",
            "ci/cd",
        }

        found_keywords = set()
        for keyword in keywords:
            if keyword in text:
                found_keywords.add(keyword)

        return found_keywords
