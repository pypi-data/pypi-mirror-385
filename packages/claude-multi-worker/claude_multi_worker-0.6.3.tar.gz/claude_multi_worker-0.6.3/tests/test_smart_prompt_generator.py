"""
SmartPromptGeneratorのテスト
"""

import pytest
from cmw.models import Task, TaskStatus, Priority
from cmw.smart_prompt_generator import SmartPromptGenerator


@pytest.fixture
def sample_tasks():
    """テスト用のサンプルタスク"""
    return [
        Task(
            id="TASK-001",
            title="基盤タスク",
            description="最初に実行するタスク",
            assigned_to="backend",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            dependencies=[],
            target_files=["base.py"],
            acceptance_criteria=["基盤機能が動作すること"],
        ),
        Task(
            id="TASK-002",
            title="依存タスク",
            description="TASK-001に依存するタスク",
            assigned_to="backend",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            dependencies=["TASK-001"],
            target_files=["feature.py"],
            acceptance_criteria=["機能が実装されていること", "テストがパスすること"],
        ),
    ]


class TestSmartPromptGenerator:
    """SmartPromptGeneratorのテスト"""

    def test_init(self, sample_tasks, tmp_path):
        """初期化のテスト"""
        generator = SmartPromptGenerator(sample_tasks, tmp_path)
        assert len(generator.tasks) == 2
        assert generator.analyzer is not None

    def test_generate_basic_prompt(self, sample_tasks, tmp_path):
        """基本的なプロンプト生成"""
        generator = SmartPromptGenerator(sample_tasks, tmp_path)
        prompt = generator.generate("TASK-001")

        assert "TASK-001" in prompt
        assert "基盤タスク" in prompt
        assert "高" in prompt  # 優先度

    def test_generate_with_dependencies(self, sample_tasks, tmp_path):
        """依存関係を含むプロンプト生成"""
        generator = SmartPromptGenerator(sample_tasks, tmp_path)
        prompt = generator.generate("TASK-002")

        assert "TASK-002" in prompt
        assert "依存関係" in prompt or "前提タスク" in prompt

    def test_generate_with_critical_path(self, sample_tasks, tmp_path):
        """クリティカルパス情報を含むプロンプト"""
        # TASK-001をクリティカルパス上にする
        generator = SmartPromptGenerator(sample_tasks, tmp_path)
        prompt = generator.generate("TASK-001")

        assert "クリティカルパス" in prompt or "優先的" in prompt

    def test_generate_with_target_files(self, sample_tasks, tmp_path):
        """対象ファイル情報を含むプロンプト"""
        generator = SmartPromptGenerator(sample_tasks, tmp_path)
        prompt = generator.generate("TASK-001")

        assert "base.py" in prompt
        assert "ファイル" in prompt

    def test_generate_with_acceptance_criteria(self, sample_tasks, tmp_path):
        """受入基準を含むプロンプト"""
        generator = SmartPromptGenerator(sample_tasks, tmp_path)
        prompt = generator.generate("TASK-001")

        assert "基盤機能が動作すること" in prompt
        assert "完了条件" in prompt or "チェックリスト" in prompt

    def test_generate_with_implementation_guide(self, sample_tasks, tmp_path):
        """実装ガイドを含むプロンプト"""
        generator = SmartPromptGenerator(sample_tasks, tmp_path)
        prompt = generator.generate("TASK-001")

        assert "実装" in prompt
        assert "手順" in prompt or "ガイド" in prompt

    def test_generate_nonexistent_task(self, sample_tasks, tmp_path):
        """存在しないタスクのプロンプト生成"""
        generator = SmartPromptGenerator(sample_tasks, tmp_path)
        prompt = generator.generate("TASK-999")

        assert "エラー" in prompt or "見つかりません" in prompt

    def test_generate_with_requirements_md(self, sample_tasks, tmp_path):
        """requirements.mdがある場合のプロンプト生成"""
        # requirements.mdを作成
        req_dir = tmp_path / "shared" / "docs"
        req_dir.mkdir(parents=True)
        req_file = req_dir / "requirements.md"
        req_file.write_text("# テスト要件\n\n## 基盤機能\n詳細な説明", encoding="utf-8")

        generator = SmartPromptGenerator(sample_tasks, tmp_path)
        prompt = generator.generate("TASK-001")

        # requirements.mdの参照が含まれる
        assert "requirements.md" in prompt

    def test_generate_includes_test_commands(self, sample_tasks, tmp_path):
        """テストコマンドを含むプロンプト"""
        generator = SmartPromptGenerator(sample_tasks, tmp_path)
        prompt = generator.generate("TASK-001")

        assert "pytest" in prompt or "テスト" in prompt

    def test_generate_includes_next_steps(self, sample_tasks, tmp_path):
        """次のステップを含むプロンプト"""
        generator = SmartPromptGenerator(sample_tasks, tmp_path)
        prompt = generator.generate("TASK-001")

        assert "完了後" in prompt or "次" in prompt

    def test_generate_includes_completion_instructions(self, sample_tasks, tmp_path):
        """完了方法の説明を含むプロンプト"""
        generator = SmartPromptGenerator(sample_tasks, tmp_path)
        prompt = generator.generate("TASK-001")

        assert "cmw task complete" in prompt

    def test_blocking_count_display(self, sample_tasks, tmp_path):
        """ブロック中のタスク数を表示"""
        generator = SmartPromptGenerator(sample_tasks, tmp_path)
        prompt = generator.generate("TASK-001")

        # TASK-001は1タスクをブロック
        assert "ブロック" in prompt
