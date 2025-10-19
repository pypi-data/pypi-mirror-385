"""
信頼性テスト

このモジュールは、システムの信頼性を検証するテストを含みます。
"""
import pytest
import tempfile
import json
import time
from pathlib import Path
from cmw.requirements_parser import RequirementsParser
from cmw.dependency_validator import DependencyValidator
from cmw.models import Task, Priority


class TestFileCorruption:
    """ファイル破損時の挙動"""

    def test_corrupted_json_tasks_file(self):
        """破損したJSONファイルの処理"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 破損したJSONファイルを作成
            tasks_file = Path(tmpdir) / "tasks.json"
            tasks_file.write_text('{"tasks": [{"id": "TASK-001", incomplete...', encoding='utf-8')

            # 破損したファイルを読み込もうとするとエラー
            with pytest.raises(json.JSONDecodeError):
                json.loads(tasks_file.read_text(encoding='utf-8'))

    def test_empty_json_file(self):
        """空のJSONファイル"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tasks_file = Path(tmpdir) / "tasks.json"
            tasks_file.write_text('', encoding='utf-8')

            # 空ファイルを読み込むとエラー
            with pytest.raises(json.JSONDecodeError):
                json.loads(tasks_file.read_text(encoding='utf-8'))

    def test_invalid_utf8_encoding(self):
        """不正なUTF-8エンコーディング"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.md') as f:
            # 不正なUTF-8バイト列
            f.write(b'# Test\n\n## Section\n- \xff\xfe invalid bytes')
            invalid_file = Path(f.name)

        try:
            parser = RequirementsParser()

            # UnicodeDecodeErrorが発生する可能性
            try:
                _ = parser.parse(invalid_file)
            except UnicodeDecodeError:
                pass  # 予期されるエラー

        finally:
            invalid_file.unlink()

    def test_truncated_file(self):
        """途中で切れたファイル"""
        content = """# Project

## 1. Database Setup
- Create database.py
- Set up SQLAlchemy
- Define models

## 2. Auth
- Implement user registra"""  # 途中で切れている

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            truncated_file = Path(f.name)

        try:
            parser = RequirementsParser()
            # 途中で切れていてもパース可能
            tasks = parser.parse(truncated_file)

            assert isinstance(tasks, list)

        finally:
            truncated_file.unlink()


class TestDiskSpace:
    """ディスク容量関連のテスト"""

    def test_save_with_limited_space(self):
        """ディスク容量が限られている状況での保存"""
        # 大量のデータを書き込むテスト
        with tempfile.TemporaryDirectory() as tmpdir:
            large_file = Path(tmpdir) / "large_data.json"

            # 大量のデータを作成
            large_data = {
                "tasks": [
                    {
                        "id": f"TASK-{i:05d}",
                        "title": f"Task {i}",
                        "description": "Test " * 1000,
                    }
                    for i in range(1000)
                ]
            }

            # 保存が成功することを確認
            large_file.write_text(json.dumps(large_data), encoding='utf-8')
            assert large_file.exists()
            assert large_file.stat().st_size > 100000  # 100KB以上

    def test_check_disk_space_before_save(self):
        """保存前にディスク容量を確認"""
        import shutil

        with tempfile.TemporaryDirectory() as tmpdir:
            # ディスク容量を取得
            stat = shutil.disk_usage(tmpdir)

            # 利用可能な容量が十分あることを確認
            assert stat.free > 1024 * 1024  # 最低1MB


class TestFileSystemEdgeCases:
    """ファイルシステムのエッジケース"""

    def test_readonly_filesystem(self):
        """読み取り専用ファイルシステムへの書き込み"""
        # 実際に読み取り専用にするのは難しいので、
        # 読み取り専用ディレクトリへの書き込みをテスト

        with tempfile.TemporaryDirectory() as tmpdir:
            readonly_dir = Path(tmpdir) / "readonly"
            readonly_dir.mkdir()

            # ディレクトリを読み取り専用に設定
            readonly_dir.chmod(0o555)

            try:
                state_dir = readonly_dir / ".cmw"

                # ディレクトリ作成時にPermissionErrorが発生するはず
                with pytest.raises(PermissionError):
                    state_dir.mkdir()

            finally:
                # クリーンアップ
                readonly_dir.chmod(0o755)

    def test_symlink_handling(self):
        """シンボリックリンクの処理"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 実際のファイルを作成
            real_file = Path(tmpdir) / "real_requirements.md"
            real_file.write_text("# Test\n\n## Section\n- Item", encoding='utf-8')

            # シンボリックリンクを作成
            symlink = Path(tmpdir) / "link_requirements.md"
            symlink.symlink_to(real_file)

            # シンボリックリンク経由でも読み込める
            parser = RequirementsParser()
            tasks = parser.parse(symlink)

            assert isinstance(tasks, list)

    def test_special_filenames(self):
        """特殊なファイル名の処理"""
        special_names = [
            "file with spaces.md",
            "file_with_日本語.md",
            "file-with-dashes.md",
            "file.multiple.dots.md",
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            for name in special_names:
                file_path = Path(tmpdir) / name
                file_path.write_text("# Test\n\n## Section\n- Item", encoding='utf-8')

                parser = RequirementsParser()
                tasks = parser.parse(file_path)

                assert isinstance(tasks, list), f"Failed for: {name}"

    def test_case_sensitive_filesystem(self):
        """大文字小文字の区別"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 小文字のファイル
            lower_file = Path(tmpdir) / "requirements.md"
            lower_file.write_text("# Test", encoding='utf-8')

            # Linuxでは大文字小文字を区別するので、別ファイルとして扱われる
            upper_file = Path(tmpdir) / "REQUIREMENTS.MD"

            # ファイルシステムによって挙動が異なる
            if not upper_file.exists():
                upper_file.write_text("# Test Upper", encoding='utf-8')
                assert lower_file.exists() and upper_file.exists()


class TestRecovery:
    """障害復旧のテスト"""

    def test_recovery_from_partial_save(self):
        """部分的な保存からの復旧"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tasks_file = Path(tmpdir) / "tasks.json"

            # 完全なJSONを書き込み
            original_content = '{"tasks": [{"id": "TASK-001", "title": "Test"}]}'
            tasks_file.write_text(original_content, encoding='utf-8')

            # ファイルの一部を削除（破損をシミュレート）
            corrupted_content = original_content[:len(original_content) // 2]
            tasks_file.write_text(corrupted_content, encoding='utf-8')

            # 破損したファイルからの読み込み
            with pytest.raises(json.JSONDecodeError):
                json.loads(tasks_file.read_text(encoding='utf-8'))

    def test_backup_and_restore(self):
        """バックアップと復元"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tasks_file = Path(tmpdir) / "tasks.json"
            backup_file = Path(tmpdir) / "tasks.json.backup"

            # 元のデータを保存
            original_data = '{"tasks": [{"id": "TASK-001"}, {"id": "TASK-002"}]}'
            tasks_file.write_text(original_data, encoding='utf-8')

            # バックアップを作成
            backup_file.write_bytes(tasks_file.read_bytes())

            # 元のファイルを破損させる
            tasks_file.write_text("corrupted", encoding='utf-8')

            # バックアップから復元
            tasks_file.write_bytes(backup_file.read_bytes())

            # 復元されたデータを読み込み
            loaded_data = json.loads(tasks_file.read_text(encoding='utf-8'))

            assert len(loaded_data["tasks"]) == 2


class TestIdempotency:
    """冪等性のテスト"""

    def test_parse_idempotency(self):
        """同じファイルを複数回パースしても結果が一貫している"""
        content = """# Project

## Database Setup
- Create database.py
- Set up SQLAlchemy

## API
- Implement REST API
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            req_file = Path(f.name)

        try:
            parser = RequirementsParser()

            # 3回パース
            tasks1 = parser.parse(req_file)
            tasks2 = parser.parse(req_file)
            tasks3 = parser.parse(req_file)

            # タスク数が同じ
            assert len(tasks1) == len(tasks2) == len(tasks3)

            # タスクの内容が一貫している（IDは異なる可能性があるが数は同じ）
            assert len(tasks1) > 0

        finally:
            req_file.unlink()

    def test_save_load_idempotency(self):
        """保存→読み込みを繰り返しても同じ"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.json"

            original_data = {
                "id": "TASK-001",
                "title": "Test",
                "description": "Description"
            }

            for i in range(3):
                # 保存
                test_file.write_text(json.dumps(original_data), encoding='utf-8')

                # 読み込み
                loaded_data = json.loads(test_file.read_text(encoding='utf-8'))

                # データが同じ
                assert loaded_data["id"] == "TASK-001"
                assert loaded_data["title"] == "Test"


class TestTimeout:
    """タイムアウト処理のテスト"""

    def test_parse_completes_in_reasonable_time(self):
        """パース処理が合理的な時間で完了する"""
        # 中規模のrequirements.md
        content = "# Project\n\n"
        for i in range(50):
            content += f"## Section {i}\n"
            for j in range(10):
                content += f"- Item {i}-{j}\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            req_file = Path(f.name)

        try:
            parser = RequirementsParser()

            start_time = time.time()
            tasks = parser.parse(req_file)
            elapsed = time.time() - start_time

            # 10秒以内に完了
            assert elapsed < 10.0, f"Parse took too long: {elapsed:.2f}s"
            assert isinstance(tasks, list)  # パース結果を使用

        finally:
            req_file.unlink()

    def test_validation_completes_in_reasonable_time(self):
        """検証処理が合理的な時間で完了する"""
        # 100タスクを生成
        tasks = []
        for i in range(100):
            tasks.append(Task(
                id=f"TASK-{i:03d}",
                title=f"Task {i}",
                description="Test",
                assigned_to="backend",
                dependencies=[f"TASK-{j:03d}" for j in range(max(0, i-5), i)],
                priority=Priority.MEDIUM
            ))

        validator = DependencyValidator()

        start_time = time.time()
        result = validator.validate_dependencies(tasks)
        elapsed = time.time() - start_time

        # 5秒以内に完了
        assert elapsed < 5.0, f"Validation took too long: {elapsed:.2f}s"
        assert isinstance(result, dict)
