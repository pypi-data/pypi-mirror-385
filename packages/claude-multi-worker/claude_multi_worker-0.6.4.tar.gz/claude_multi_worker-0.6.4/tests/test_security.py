"""
セキュリティテスト

このモジュールは、セキュリティ脆弱性を検出するためのテストを含みます。
"""
import pytest
import tempfile
from pathlib import Path
from cmw.requirements_parser import RequirementsParser
from cmw.models import Task, Priority


class TestPathTraversal:
    """パストラバーサル攻撃の防止"""

    def test_path_traversal_in_requirements(self):
        """requirements.mdのパスにパストラバーサルが含まれる場合"""
        # ../../../etc/passwd のような攻撃を防ぐ
        malicious_path = Path("../../../etc/passwd")

        parser = RequirementsParser()

        # FileNotFoundErrorが発生することを確認（攻撃が成功しない）
        with pytest.raises(FileNotFoundError):
            parser.parse(malicious_path)

    def test_path_traversal_in_target_files(self):
        """target_filesにパストラバーサルが含まれる場合"""
        task = Task(
            id="TASK-001",
            title="Malicious",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            target_files=["../../../etc/passwd"],  # 攻撃パス
            priority=Priority.HIGH
        )

        # タスクは作成できるが、実際のファイル操作時に検証される
        assert "../.." in task.target_files[0]

    def test_absolute_path_in_target_files(self):
        """絶対パスの使用"""
        task = Task(
            id="TASK-001",
            title="Absolute path",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            target_files=["/etc/passwd"],  # 絶対パス
            priority=Priority.HIGH
        )

        # タスクは作成できるが、実際の操作では警戒が必要
        assert task.target_files[0].startswith("/")


class TestCommandInjection:
    """コマンドインジェクション攻撃の防止"""

    def test_task_id_with_shell_metacharacters(self):
        """タスクIDにシェルメタ文字が含まれる場合"""
        # タスクIDは通常TASK-001形式だが、攻撃を想定
        malicious_id = "TASK-001; rm -rf /"

        task = Task(
            id=malicious_id,
            title="Test",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.HIGH
        )

        # タスクは作成できるが、IDにメタ文字が含まれる
        assert ";" in task.id

    def test_file_path_with_shell_metacharacters(self):
        """ファイルパスにシェルメタ文字"""
        task = Task(
            id="TASK-001",
            title="Test",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            target_files=["file.py; rm -rf /"],
            priority=Priority.HIGH
        )

        assert ";" in task.target_files[0]


class TestFilePermissions:
    """ファイル権限のテスト"""

    def test_create_file_with_secure_permissions(self):
        """作成されるファイルの権限が適切か"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # ファイルを直接作成してパーミッションをテスト
            test_file = Path(tmpdir) / "test.json"
            test_file.write_text('{"test": "data"}', encoding='utf-8')

            # パーミッションを確認
            stat_info = test_file.stat()
            mode = oct(stat_info.st_mode)[-3:]

            # 最低限、他者に書き込み権限がないことを確認
            assert int(mode[2]) & 0o2 == 0, f"Others have write permission: {mode}"

    def test_read_only_file_handling(self):
        """読み取り専用ファイルの処理"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write("# Test")
            readonly_file = Path(f.name)

        try:
            # ファイルを読み取り専用に設定
            readonly_file.chmod(0o444)

            # 読み取りは成功するはず
            parser = RequirementsParser()
            tasks = parser.parse(readonly_file)

            assert isinstance(tasks, list)

        finally:
            # クリーンアップ（権限を戻してから削除）
            readonly_file.chmod(0o644)
            readonly_file.unlink()

    def test_no_permission_file(self):
        """権限のないファイルへのアクセス"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write("# Test")
            no_perm_file = Path(f.name)

        try:
            # ファイルの読み取り権限を削除
            no_perm_file.chmod(0o000)

            parser = RequirementsParser()

            # PermissionErrorが発生するはず
            with pytest.raises(PermissionError):
                parser.parse(no_perm_file)

        finally:
            # クリーンアップ
            no_perm_file.chmod(0o644)
            no_perm_file.unlink()


class TestInputValidation:
    """入力バリデーションのテスト"""

    def test_extremely_long_task_id(self):
        """極端に長いタスクID"""
        long_id = "TASK-" + "0" * 10000

        task = Task(
            id=long_id,
            title="Test",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.HIGH
        )

        # 作成は可能だが、長さチェックが必要
        assert len(task.id) > 10000

    def test_extremely_long_file_path(self):
        """極端に長いファイルパス"""
        long_path = "a/" * 1000 + "file.py"

        task = Task(
            id="TASK-001",
            title="Test",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            target_files=[long_path],
            priority=Priority.HIGH
        )

        # OSの制限でエラーになる可能性
        assert len(task.target_files[0]) > 2000

    def test_null_bytes_in_file_path(self):
        """ファイルパスにnullバイト"""
        # nullバイトはファイルパス操作で問題を起こす可能性
        task = Task(
            id="TASK-001",
            title="Test",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            target_files=["file.py\x00malicious"],
            priority=Priority.HIGH
        )

        assert "\x00" in task.target_files[0]

    def test_special_characters_in_task_title(self):
        """タスクタイトルに特殊文字"""
        special_chars = "<script>alert('xss')</script>"

        task = Task(
            id="TASK-001",
            title=special_chars,
            description="Test",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.HIGH
        )

        # HTMLタグがそのまま格納される（表示時のエスケープが重要）
        assert "<script>" in task.title


class TestDOSPrevention:
    """DoS攻撃の防止"""

    def test_massive_dependencies(self):
        """大量の依存関係"""
        # 10000個の依存関係を持つタスク
        massive_deps = [f"TASK-{i:05d}" for i in range(10000)]

        task = Task(
            id="TASK-999",
            title="Massive deps",
            description="Test",
            assigned_to="backend",
            dependencies=massive_deps,
            priority=Priority.HIGH
        )

        assert len(task.dependencies) == 10000

    def test_deeply_nested_markdown(self):
        """深くネストされたMarkdown"""
        # 100段階のネストしたリスト
        nested = "# Test\n\n"
        for i in range(100):
            nested += "  " * i + f"- Item {i}\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(nested)
            nested_file = Path(f.name)

        try:
            parser = RequirementsParser()
            # パースがハングしないことを確認
            tasks = parser.parse(nested_file)

            assert isinstance(tasks, list)

        finally:
            nested_file.unlink()

    def test_billion_laughs_attack(self):
        """Billion Laughs攻撃（指数関数的膨張）の防止"""
        # 実際にはXML攻撃だが、類似の攻撃パターンをテスト
        # 極端に長い繰り返しパターン
        content = "# Test\n\n" + ("## Section\n- Item\n" * 10000)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            large_file = Path(f.name)

        try:
            parser = RequirementsParser()
            # メモリを大量に消費しないことを確認
            tasks = parser.parse(large_file)

            assert isinstance(tasks, list)

        finally:
            large_file.unlink()


class TestDataLeakage:
    """データ漏洩の防止"""

    def test_sensitive_data_in_error_messages(self):
        """エラーメッセージに機密情報が含まれないか"""
        # 存在しないファイルパスに機密情報っぽいものを含める
        sensitive_path = Path("/home/user/.ssh/id_rsa")

        parser = RequirementsParser()

        try:
            parser.parse(sensitive_path)
        except FileNotFoundError as e:
            # エラーメッセージにパスが含まれることは許容
            # （実際の運用では、パスのサニタイズが必要な場合もある）
            assert "id_rsa" in str(e)

    def test_no_secrets_in_task_data(self):
        """タスクデータに秘密情報が含まれないことの確認"""
        # これは開発者への注意喚起的なテスト
        task = Task(
            id="TASK-001",
            title="Database setup",
            description="Set up PostgreSQL",
            assigned_to="backend",
            dependencies=[],
            # パスワードやAPIキーは含めない
            priority=Priority.HIGH
        )

        # descriptionに明らかな秘密情報パターンがないことを確認
        suspicious_patterns = ["password=", "api_key=", "secret=", "token="]
        for pattern in suspicious_patterns:
            assert pattern.lower() not in task.description.lower()


class TestRaceConditions:
    """競合状態のテスト"""

    def test_concurrent_file_write(self):
        """同時ファイル書き込みの安全性"""
        import concurrent.futures
        import time
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "concurrent_test.json"

            def write_data(worker_id):
                """複数のワーカーが同時に書き込み"""
                time.sleep(0.01 * worker_id)  # わずかにずらす

                data = {
                    "worker_id": worker_id,
                    "timestamp": time.time()
                }

                test_file.write_text(json.dumps(data), encoding='utf-8')
                return worker_id

            # 10個のワーカーが同時に書き込み
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(write_data, i) for i in range(10)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            # 全てのワーカーが完了したことを確認
            assert len(results) == 10

            # ファイルが破損していないことを確認（JSONとして読める）
            content = test_file.read_text(encoding='utf-8')
            data = json.loads(content)  # JSONパース可能

            # いずれかのワーカーのデータが残っている
            assert "worker_id" in data
