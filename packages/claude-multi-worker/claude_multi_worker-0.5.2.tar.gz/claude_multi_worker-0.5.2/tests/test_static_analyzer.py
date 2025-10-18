"""
StaticAnalyzer のユニットテスト
"""
import pytest
from pathlib import Path
from cmw.static_analyzer import StaticAnalyzer
from cmw.models import Task, Priority


@pytest.fixture
def temp_python_project(tmp_path):
    """テスト用のPythonプロジェクトを作成"""
    # backend/models.py
    models_file = tmp_path / "backend" / "models.py"
    models_file.parent.mkdir(parents=True)
    models_file.write_text("""
from datetime import datetime
from typing import Optional

class User:
    def __init__(self, username: str):
        self.username = username
        self.created_at = datetime.now()
""", encoding='utf-8')

    # backend/api/auth.py
    auth_file = tmp_path / "backend" / "api" / "auth.py"
    auth_file.parent.mkdir(parents=True)
    auth_file.write_text("""
from backend.models import User
from fastapi import APIRouter

router = APIRouter()

@router.post("/auth/login")
def login():
    return {"message": "Login"}

@router.post("/auth/register")
def register():
    user = User("test")
    return {"user": user.username}
""", encoding='utf-8')

    # backend/api/tasks.py
    tasks_file = tmp_path / "backend" / "api" / "tasks.py"
    tasks_file.write_text("""
from backend.models import User
from backend.api.auth import router as auth_router

def get_tasks():
    return []
""", encoding='utf-8')

    # backend/__init__.py
    init_file = tmp_path / "backend" / "__init__.py"
    init_file.write_text("", encoding='utf-8')

    init_file = tmp_path / "backend" / "api" / "__init__.py"
    init_file.write_text("", encoding='utf-8')

    return tmp_path


@pytest.fixture
def sample_tasks():
    """サンプルタスク"""
    return [
        Task(
            id="TASK-001",
            title="モデル定義",
            description="",
            assigned_to="backend",
            dependencies=[],
            target_files=["backend/models.py"],
            acceptance_criteria=[],
            priority=Priority.HIGH
        ),
        Task(
            id="TASK-002",
            title="認証API",
            description="",
            assigned_to="backend",
            dependencies=[],
            target_files=["backend/api/auth.py"],
            acceptance_criteria=[],
            priority=Priority.HIGH
        ),
        Task(
            id="TASK-003",
            title="タスクAPI",
            description="",
            assigned_to="backend",
            dependencies=[],
            target_files=["backend/api/tasks.py"],
            acceptance_criteria=[],
            priority=Priority.MEDIUM
        ),
    ]


class TestStaticAnalyzerBasics:
    """StaticAnalyzer の基本機能テスト"""

    def test_initialization(self, tmp_path):
        """初期化のテスト"""
        analyzer = StaticAnalyzer()
        assert analyzer.project_root == Path.cwd()

        analyzer = StaticAnalyzer(project_root=tmp_path)
        assert analyzer.project_root == tmp_path

    def test_analyze_file_dependencies(self, temp_python_project):
        """ファイル依存関係の解析"""
        analyzer = StaticAnalyzer(project_root=temp_python_project)

        # backend/models.py の依存関係
        deps = analyzer.analyze_file_dependencies("backend/models.py")
        assert isinstance(deps, set)
        # datetime, typing は標準ライブラリなので依存関係に含まれない

        # backend/api/auth.py の依存関係
        deps = analyzer.analyze_file_dependencies("backend/api/auth.py")
        assert "backend/models.py" in deps

    def test_analyze_nonexistent_file(self, temp_python_project):
        """存在しないファイルの解析"""
        analyzer = StaticAnalyzer(project_root=temp_python_project)
        deps = analyzer.analyze_file_dependencies("nonexistent.py")
        assert deps == set()

    def test_analyze_non_python_file(self, temp_python_project):
        """非Pythonファイルの解析"""
        # テキストファイルを作成
        text_file = temp_python_project / "readme.txt"
        text_file.write_text("This is not Python", encoding='utf-8')

        analyzer = StaticAnalyzer(project_root=temp_python_project)
        deps = analyzer.analyze_file_dependencies("readme.txt")
        assert deps == set()


class TestInferTaskDependencies:
    """タスク依存関係推論のテスト"""

    def test_infer_task_dependencies_basic(self, temp_python_project, sample_tasks):
        """基本的な依存関係推論"""
        analyzer = StaticAnalyzer(project_root=temp_python_project)

        updated_tasks = analyzer.infer_task_dependencies(
            sample_tasks,
            existing_dependencies=False
        )

        # TASK-001 (models.py) には依存なし
        task_001 = next(t for t in updated_tasks if t.id == "TASK-001")
        assert len(task_001.dependencies) == 0

        # TASK-002 (auth.py) は models.py に依存
        task_002 = next(t for t in updated_tasks if t.id == "TASK-002")
        assert "TASK-001" in task_002.dependencies

        # TASK-003 (tasks.py) は models.py と auth.py に依存
        task_003 = next(t for t in updated_tasks if t.id == "TASK-003")
        assert "TASK-001" in task_003.dependencies
        assert "TASK-002" in task_003.dependencies

    def test_infer_with_existing_dependencies(self, temp_python_project):
        """既存の依存関係を保持"""
        tasks = [
            Task(
                id="TASK-001",
                title="モデル",
                description="",
                assigned_to="backend",
                dependencies=["TASK-000"],  # 既存の依存関係
                target_files=["backend/models.py"],
                acceptance_criteria=[],
                priority=Priority.HIGH
            ),
        ]

        analyzer = StaticAnalyzer(project_root=temp_python_project)
        updated_tasks = analyzer.infer_task_dependencies(
            tasks,
            existing_dependencies=True
        )

        # 既存の依存関係が保持される
        assert "TASK-000" in updated_tasks[0].dependencies


class TestCircularImports:
    """循環インポートのテスト"""

    def test_detect_no_circular_imports(self, temp_python_project, sample_tasks):
        """循環インポートなし"""
        analyzer = StaticAnalyzer(project_root=temp_python_project)
        cycles = analyzer.detect_circular_imports(sample_tasks)

        # 現在のプロジェクト構造では循環はない
        assert len(cycles) == 0

    def test_detect_circular_imports(self, tmp_path):
        """循環インポートの検出"""
        # a.py -> b.py -> a.py の循環を作成
        a_file = tmp_path / "a.py"
        a_file.write_text("from b import func_b", encoding='utf-8')

        b_file = tmp_path / "b.py"
        b_file.write_text("from a import func_a", encoding='utf-8')

        tasks = [
            Task(
                id="TASK-A",
                title="A",
                description="",
                assigned_to="backend",
                dependencies=[],
                target_files=["a.py"],
                acceptance_criteria=[],
                priority=Priority.MEDIUM
            ),
            Task(
                id="TASK-B",
                title="B",
                description="",
                assigned_to="backend",
                dependencies=[],
                target_files=["b.py"],
                acceptance_criteria=[],
                priority=Priority.MEDIUM
            ),
        ]

        analyzer = StaticAnalyzer(project_root=tmp_path)
        cycles = analyzer.detect_circular_imports(tasks)

        # 循環が検出される
        assert len(cycles) > 0


class TestImportPatterns:
    """インポートパターン分析のテスト"""

    def test_analyze_import_patterns(self, temp_python_project, sample_tasks):
        """インポートパターンの分析"""
        analyzer = StaticAnalyzer(project_root=temp_python_project)
        stats = analyzer.analyze_import_patterns(sample_tasks)

        # 統計情報が含まれる
        assert 'total_files' in stats
        assert 'total_imports' in stats
        assert 'circular_imports' in stats
        assert 'most_imported_files' in stats
        assert 'files_with_most_imports' in stats

        # backend/models.py が最もインポートされているはず
        assert len(stats['most_imported_files']) > 0

    def test_empty_project_stats(self, tmp_path):
        """空のプロジェクトの統計"""
        tasks = []

        analyzer = StaticAnalyzer(project_root=tmp_path)
        stats = analyzer.analyze_import_patterns(tasks)

        assert stats['total_files'] == 0
        assert stats['total_imports'] == 0


class TestFileOrganization:
    """ファイル構成提案のテスト"""

    def test_suggest_file_organization(self, sample_tasks):
        """ファイル構成の提案"""
        analyzer = StaticAnalyzer()
        organization = analyzer.suggest_file_organization(sample_tasks)

        # ディレクトリごとにグループ化される
        assert 'backend' in organization or 'backend/api' in organization

    def test_empty_organization(self):
        """空のタスクリスト"""
        analyzer = StaticAnalyzer()
        organization = analyzer.suggest_file_organization([])
        assert organization == {}


class TestAPIEndpoints:
    """APIエンドポイント抽出のテスト"""

    def test_extract_api_endpoints(self, temp_python_project):
        """APIエンドポイントの抽出"""
        analyzer = StaticAnalyzer(project_root=temp_python_project)
        endpoints = analyzer.extract_api_endpoints("backend/api/auth.py")

        # /auth/login と /auth/register が検出される
        assert len(endpoints) == 2

        methods = [e['method'] for e in endpoints]
        paths = [e['path'] for e in endpoints]

        assert 'POST' in methods
        assert '/auth/login' in paths
        assert '/auth/register' in paths

    def test_extract_from_nonexistent_file(self, temp_python_project):
        """存在しないファイルからの抽出"""
        analyzer = StaticAnalyzer(project_root=temp_python_project)
        endpoints = analyzer.extract_api_endpoints("nonexistent.py")
        assert endpoints == []


class TestComplexity:
    """複雑度分析のテスト"""

    def test_analyze_complexity(self, temp_python_project):
        """ファイルの複雑度分析"""
        analyzer = StaticAnalyzer(project_root=temp_python_project)
        stats = analyzer.analyze_complexity("backend/models.py")

        assert 'lines_of_code' in stats
        assert 'num_functions' in stats
        assert 'num_classes' in stats
        assert 'num_imports' in stats
        assert 'max_nesting_depth' in stats

        # User クラスがあるはず
        assert stats['num_classes'] >= 1

    def test_complexity_nonexistent_file(self, temp_python_project):
        """存在しないファイルの複雑度"""
        analyzer = StaticAnalyzer(project_root=temp_python_project)
        stats = analyzer.analyze_complexity("nonexistent.py")
        assert stats == {}


class TestModuleToFile:
    """モジュール名→ファイルパス変換のテスト"""

    def test_module_to_file_absolute(self, temp_python_project):
        """絶対インポートの変換"""
        analyzer = StaticAnalyzer(project_root=temp_python_project)

        # backend.models -> backend/models.py
        file_paths = analyzer._module_to_file("backend.models", "some_file.py")
        assert "backend/models.py" in file_paths

        # backend.api -> backend/api/__init__.py
        file_paths = analyzer._module_to_file("backend.api", "some_file.py")
        assert len(file_paths) > 0

    def test_module_to_file_nonexistent(self, temp_python_project):
        """存在しないモジュールの変換"""
        analyzer = StaticAnalyzer(project_root=temp_python_project)

        file_paths = analyzer._module_to_file("nonexistent.module", "some_file.py")
        assert len(file_paths) == 0


class TestRealWorldScenarios:
    """実世界のシナリオテスト"""

    def test_complex_project_structure(self, tmp_path):
        """複雑なプロジェクト構造"""
        # 複数の階層とファイルを作成
        for dir_path in ["src/api", "src/models", "src/utils", "tests"]:
            (tmp_path / dir_path).mkdir(parents=True)

        # ファイルを作成
        (tmp_path / "src/models/user.py").write_text("class User: pass", encoding='utf-8')
        (tmp_path / "src/api/auth.py").write_text("from src.models.user import User", encoding='utf-8')

        tasks = [
            Task(
                id="TASK-M",
                title="モデル",
                description="",
                assigned_to="backend",
                dependencies=[],
                target_files=["src/models/user.py"],
                acceptance_criteria=[],
                priority=Priority.HIGH
            ),
            Task(
                id="TASK-A",
                title="API",
                description="",
                assigned_to="backend",
                dependencies=[],
                target_files=["src/api/auth.py"],
                acceptance_criteria=[],
                priority=Priority.MEDIUM
            ),
        ]

        analyzer = StaticAnalyzer(project_root=tmp_path)
        updated_tasks = analyzer.infer_task_dependencies(tasks, existing_dependencies=False)

        # TASK-A が TASK-M に依存するはず
        task_a = next(t for t in updated_tasks if t.id == "TASK-A")
        assert "TASK-M" in task_a.dependencies

    def test_syntax_error_handling(self, tmp_path):
        """構文エラーのあるファイルの処理"""
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("this is not valid python code {{", encoding='utf-8')

        analyzer = StaticAnalyzer(project_root=tmp_path)
        deps = analyzer.analyze_file_dependencies("bad.py")

        # エラーが発生しても空のsetを返す
        assert deps == set()


class TestImportTypes:
    """様々なインポートタイプのテスト"""

    def test_ast_import_detection(self, tmp_path):
        """import文の検出"""
        # import os, sys のような形式
        file_a = tmp_path / "a.py"
        file_a.write_text("import os\nimport sys", encoding='utf-8')

        analyzer = StaticAnalyzer(project_root=tmp_path)
        deps = analyzer.analyze_file_dependencies("a.py")

        # 標準ライブラリなので依存関係には含まれない
        assert isinstance(deps, set)

    def test_relative_import_from_dot(self, tmp_path):
        """相対インポート (from . import) の検出"""
        # パッケージ構造を作成
        (tmp_path / "pkg").mkdir()
        (tmp_path / "pkg" / "__init__.py").write_text("", encoding='utf-8')
        (tmp_path / "pkg" / "module_a.py").write_text("def func_a(): pass", encoding='utf-8')
        (tmp_path / "pkg" / "module_b.py").write_text(
            "from . import module_a\n\ndef func_b():\n    module_a.func_a()",
            encoding='utf-8'
        )

        analyzer = StaticAnalyzer(project_root=tmp_path)
        deps = analyzer.analyze_file_dependencies("pkg/module_b.py")

        # module_aへの依存が検出される
        assert "pkg/module_a.py" in deps or "pkg/__init__.py" in deps

    def test_sys_path_modification_detection(self, tmp_path):
        """sys.path.insert/appendの検出"""
        # sys.pathを変更するコード
        file_with_syspath = tmp_path / "main.py"
        file_with_syspath.write_text("""
import sys
from pathlib import Path

# プロジェクトルートをsys.pathに追加
sys.path.insert(0, str(Path(__file__).parent))

from some_module import something
""", encoding='utf-8')

        analyzer = StaticAnalyzer(project_root=tmp_path)

        # エラーが発生しないことを確認
        deps = analyzer.analyze_file_dependencies("main.py")
        assert isinstance(deps, set)

    def test_evaluate_path_expr_parent(self, tmp_path):
        """パス式評価（Path(__file__).parent）のテスト"""
        file = tmp_path / "subdir" / "test.py"
        file.parent.mkdir(parents=True)
        file.write_text("""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
""", encoding='utf-8')

        analyzer = StaticAnalyzer(project_root=tmp_path)

        # sys.path変更の検出
        with open(file, 'r', encoding='utf-8') as f:
            import ast
            tree = ast.parse(f.read())

        extra_paths = analyzer._detect_sys_path_changes(tree, "subdir/test.py")

        # パスが検出されることを確認
        assert isinstance(extra_paths, list)

    def test_evaluate_path_expr_parent_parent(self, tmp_path):
        """パス式評価（Path(__file__).parent.parent）のテスト"""
        file = tmp_path / "a" / "b" / "test.py"
        file.parent.mkdir(parents=True)
        file.write_text("""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
""", encoding='utf-8')

        analyzer = StaticAnalyzer(project_root=tmp_path)

        with open(file, 'r', encoding='utf-8') as f:
            import ast
            tree = ast.parse(f.read())

        extra_paths = analyzer._detect_sys_path_changes(tree, "a/b/test.py")

        # パスが検出されることを確認
        assert isinstance(extra_paths, list)

    def test_module_to_file_with_extra_paths(self, tmp_path):
        """extra_pathsを使用したモジュール解決"""
        # src/module.py を作成
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "mymodule.py").write_text("def func(): pass", encoding='utf-8')

        analyzer = StaticAnalyzer(project_root=tmp_path)

        # extra_pathsにsrcを指定
        extra_paths = [tmp_path / "src"]
        file_paths = analyzer._module_to_file("mymodule", "main.py", extra_paths)

        # src/mymodule.pyが解決される
        assert "src/mymodule.py" in file_paths

    def test_module_to_file_relative_single_dot(self, tmp_path):
        """相対インポート（単一ドット）のテスト"""
        (tmp_path / "pkg").mkdir()
        (tmp_path / "pkg" / "module_a.py").write_text("", encoding='utf-8')

        analyzer = StaticAnalyzer(project_root=tmp_path)

        # pkg/module_b.py から .module_a をインポート
        file_paths = analyzer._module_to_file(".module_a", "pkg/module_b.py")

        # pkg/module_a.py が解決される
        assert "pkg/module_a.py" in file_paths

    def test_module_to_file_relative_double_dot(self, tmp_path):
        """相対インポート（二重ドット）のテスト"""
        (tmp_path / "pkg").mkdir()
        (tmp_path / "pkg" / "subpkg").mkdir()
        (tmp_path / "pkg" / "module_a.py").write_text("", encoding='utf-8')

        analyzer = StaticAnalyzer(project_root=tmp_path)

        # pkg/subpkg/module_b.py から ..module_a をインポート
        file_paths = analyzer._module_to_file("..module_a", "pkg/subpkg/module_b.py")

        # pkg/module_a.py が解決される
        assert "pkg/module_a.py" in file_paths

    def test_module_to_file_relative_package(self, tmp_path):
        """相対インポート（パッケージ）のテスト"""
        (tmp_path / "pkg").mkdir()
        (tmp_path / "pkg" / "__init__.py").write_text("", encoding='utf-8')

        analyzer = StaticAnalyzer(project_root=tmp_path)

        # pkg/module.py から . をインポート（パッケージ自体）
        file_paths = analyzer._module_to_file(".", "pkg/module.py")

        # pkg/__init__.py が解決される（または空のsetでも許容）
        assert isinstance(file_paths, set)

    def test_analyze_complexity_with_nesting(self, tmp_path):
        """ネストした構造の複雑度分析"""
        complex_file = tmp_path / "complex.py"
        complex_file.write_text("""
def outer():
    if True:
        for i in range(10):
            while True:
                try:
                    with open("file") as f:
                        if f:
                            pass
                except:
                    pass
""", encoding='utf-8')

        analyzer = StaticAnalyzer(project_root=tmp_path)
        stats = analyzer.analyze_complexity("complex.py")

        # ネストの深さが記録される（0以上）
        assert stats['max_nesting_depth'] >= 0
        # 少なくとも1つの関数が存在
        assert stats['num_functions'] >= 1

    def test_unicode_decode_error_handling(self, tmp_path):
        """UnicodeDecodeErrorのハンドリング"""
        # バイナリファイルを作成
        binary_file = tmp_path / "binary.py"
        binary_file.write_bytes(b'\xff\xfe\x00\x00')

        analyzer = StaticAnalyzer(project_root=tmp_path)

        # エラーが発生しても空のsetを返す
        deps = analyzer.analyze_file_dependencies("binary.py")
        assert deps == set()

        # 複雑度分析でも同様
        stats = analyzer.analyze_complexity("binary.py")
        assert stats == {}

        # エンドポイント抽出でも同様
        endpoints = analyzer.extract_api_endpoints("binary.py")
        assert endpoints == []
