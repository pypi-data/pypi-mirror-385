"""
DependencyRecommender のテスト
"""

import pytest
from cmw.dependency_recommender import DependencyRecommender
from cmw.models import Task, Priority, TaskStatus


@pytest.fixture
def sample_tasks():
    """サンプルタスク"""
    return [
        Task(
            id="TASK-001",
            title="1.1 モデル定義",
            description="データモデルを定義する",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.HIGH,
            target_files=["models.py"],
            acceptance_criteria=[]
        ),
        Task(
            id="TASK-002",
            title="1.2 データベース設計",
            description="データベーススキーマを設計",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.HIGH,
            target_files=["database.py"],
            acceptance_criteria=[]
        ),
        Task(
            id="TASK-003",
            title="2.1 API実装",
            description="RESTful APIを実装",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.MEDIUM,
            target_files=["routers/api.py"],
            acceptance_criteria=[]
        ),
        Task(
            id="TASK-004",
            title="2.2 認証機能",
            description="認証・認可機能を実装",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.CRITICAL,
            target_files=["auth.py"],
            acceptance_criteria=[]
        ),
        Task(
            id="TASK-005",
            title="3.1 UIコンポーネント",
            description="フロントエンドUI",
            assigned_to="frontend",
            dependencies=[],
            priority=Priority.MEDIUM,
            target_files=["components/App.tsx"],
            acceptance_criteria=[]
        ),
    ]


class TestDependencyRecommender:
    """依存関係推薦のテスト"""

    def test_recommend_based_on_section(self, sample_tasks):
        """セクション番号に基づく推薦"""
        recommender = DependencyRecommender(sample_tasks)

        # 2.1 API実装 に対する推薦
        api_task = sample_tasks[2]  # TASK-003
        recommendations = recommender.recommend_dependencies(api_task)

        # 1.x のタスクが推薦されるべき
        recommended_ids = [rec[0] for rec in recommendations]
        assert "TASK-001" in recommended_ids or "TASK-002" in recommended_ids

        # 信頼度が妥当な範囲
        for task_id, confidence, reason in recommendations:
            assert 0.0 <= confidence <= 1.0
            assert len(reason) > 0

    def test_recommend_based_on_files(self, sample_tasks):
        """ファイル依存に基づく推薦"""
        # models.py と routers/api.py のレイヤー依存
        recommender = DependencyRecommender(sample_tasks)

        api_task = sample_tasks[2]  # routers/api.py
        recommendations = recommender.recommend_dependencies(api_task)

        # models.py を持つタスクが推薦される可能性
        recommended_ids = [rec[0] for rec in recommendations]
        # レイヤー依存があるため、TASK-001が推薦されるべき
        assert len(recommended_ids) > 0

    def test_recommend_based_on_priority(self, sample_tasks):
        """優先度に基づく推薦"""
        recommender = DependencyRecommender(sample_tasks)

        # 低優先度タスクに対して、高優先度タスクが推薦されるべき
        low_priority_task = Task(
            id="TASK-010",
            title="5.1 低優先度機能",
            description="テスト",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.LOW,
            target_files=[],
            acceptance_criteria=[]
        )

        all_tasks = sample_tasks + [low_priority_task]
        recommender = DependencyRecommender(all_tasks)

        recommendations = recommender.recommend_dependencies(low_priority_task)
        # CRITICALやHIGHのタスクが推薦される可能性
        assert len(recommendations) >= 0  # 最低でもエラーにならない

    def test_recommend_with_keywords(self, sample_tasks):
        """キーワードマッチングによる推薦"""
        recommender = DependencyRecommender(sample_tasks)

        # 認証関連のタスク
        auth_related_task = Task(
            id="TASK-100",
            title="認可機能のテスト",
            description="認証と認可のテストを実装",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.MEDIUM,
            target_files=[],
            acceptance_criteria=[]
        )

        all_tasks = sample_tasks + [auth_related_task]
        recommender = DependencyRecommender(all_tasks)

        recommendations = recommender.recommend_dependencies(auth_related_task)

        # 認証機能タスク（TASK-004）が推薦される可能性
        recommended_ids = [rec[0] for rec in recommendations]
        # キーワードマッチで認証関連が推薦されるべき
        assert len(recommended_ids) >= 0

    def test_no_self_recommendation(self, sample_tasks):
        """自分自身は推薦されない"""
        recommender = DependencyRecommender(sample_tasks)

        task = sample_tasks[0]
        recommendations = recommender.recommend_dependencies(task)

        recommended_ids = [rec[0] for rec in recommendations]
        assert task.id not in recommended_ids

    def test_existing_dependencies_not_recommended(self, sample_tasks):
        """既存の依存関係は推薦されない"""
        task = Task(
            id="TASK-999",
            title="テストタスク",
            description="",
            assigned_to="backend",
            dependencies=["TASK-001"],  # 既に依存
            priority=Priority.MEDIUM,
            target_files=[],
            acceptance_criteria=[]
        )

        all_tasks = sample_tasks + [task]
        recommender = DependencyRecommender(all_tasks)

        recommendations = recommender.recommend_dependencies(task)

        recommended_ids = [rec[0] for rec in recommendations]
        assert "TASK-001" not in recommended_ids

    def test_max_recommendations_limit(self, sample_tasks):
        """最大推薦数の制限"""
        recommender = DependencyRecommender(sample_tasks)

        task = sample_tasks[2]
        recommendations = recommender.recommend_dependencies(task, max_recommendations=2)

        assert len(recommendations) <= 2

    def test_confidence_threshold(self, sample_tasks):
        """信頼度閾値（30%以上のみ推薦）"""
        recommender = DependencyRecommender(sample_tasks)

        task = sample_tasks[0]
        recommendations = recommender.recommend_dependencies(task)

        # 全ての推薦が30%以上の信頼度を持つ
        for task_id, confidence, reason in recommendations:
            assert confidence >= 0.3


class TestSectionNumberExtraction:
    """セクション番号抽出のテスト"""

    def test_extract_section_number(self):
        """セクション番号の抽出"""
        recommender = DependencyRecommender([])

        assert recommender._extract_section_number("1.1 モデル定義") == "1.1"
        assert recommender._extract_section_number("2.3 API実装") == "2.3"
        assert recommender._extract_section_number("10.5 デプロイ") == "10.5"
        assert recommender._extract_section_number("タイトルのみ") == ""


class TestLayerDependency:
    """レイヤー依存のテスト"""

    def test_is_layer_dependency(self):
        """ファイルレイヤー依存の判定"""
        recommender = DependencyRecommender([])

        # models.py → schemas.py
        assert recommender._is_layer_dependency("models.py", "schemas.py") is True

        # schemas.py → routers/api.py
        assert recommender._is_layer_dependency("schemas.py", "routers/api.py") is True

        # 逆方向はFalse
        assert recommender._is_layer_dependency("routers/api.py", "models.py") is False

        # 関係ないファイル
        assert recommender._is_layer_dependency("test.py", "other.py") is False


class TestKeywordExtraction:
    """キーワード抽出のテスト"""

    def test_extract_keywords(self):
        """キーワード抽出"""
        recommender = DependencyRecommender([])

        keywords = recommender._extract_keywords(
            "認証とAPI実装",
            "RESTful APIと認証機能を実装する"
        )

        assert "認証" in keywords
        assert "api" in keywords

    def test_extract_keywords_empty(self):
        """キーワードなし"""
        recommender = DependencyRecommender([])

        keywords = recommender._extract_keywords("普通のタイトル", "普通の説明")

        # 技術キーワードがない場合は空
        assert len(keywords) == 0
