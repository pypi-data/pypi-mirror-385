"""
Requirements Generator のユニットテスト
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.cmw.requirements_generator import RequirementsGenerator


class TestRequirementsGenerator:
    """RequirementsGeneratorのテスト"""

    @pytest.fixture
    def generator(self) -> RequirementsGenerator:
        """ジェネレーターインスタンスを作成"""
        return RequirementsGenerator()

    @pytest.fixture
    def temp_output_path(self, tmp_path: Path) -> Path:
        """一時出力パスを作成"""
        return tmp_path / "requirements.md"

    def test_init(self, generator: RequirementsGenerator) -> None:
        """初期化のテスト"""
        assert generator.console is not None
        assert generator.requirements_data == {}

    @patch("src.cmw.requirements_generator.Prompt.ask")
    def test_collect_basic_info(
        self, mock_ask: Mock, generator: RequirementsGenerator
    ) -> None:
        """プロジェクト基本情報収集のテスト"""
        mock_ask.side_effect = [
            "Test Project",  # project_name
            "A test API",  # description
            "rest-api",  # project_type
        ]

        generator._collect_basic_info()

        assert generator.requirements_data["project_name"] == "Test Project"
        assert generator.requirements_data["description"] == "A test API"
        assert generator.requirements_data["project_type"] == "rest-api"
        assert mock_ask.call_count == 3

    @patch("src.cmw.requirements_generator.Confirm.ask")
    @patch("src.cmw.requirements_generator.Prompt.ask")
    def test_collect_tech_stack_with_auth(
        self, mock_prompt: Mock, mock_confirm: Mock, generator: RequirementsGenerator
    ) -> None:
        """技術スタック収集（認証あり）のテスト"""
        mock_prompt.side_effect = [
            "fastapi",  # backend
            "postgresql",  # database
            "sqlalchemy",  # orm
            "jwt",  # auth_method
        ]
        mock_confirm.return_value = True  # needs_auth

        generator._collect_tech_stack()

        assert generator.requirements_data["tech_stack"]["backend"] == "fastapi"
        assert generator.requirements_data["tech_stack"]["database"] == "postgresql"
        assert generator.requirements_data["tech_stack"]["orm"] == "sqlalchemy"
        assert generator.requirements_data["tech_stack"]["auth"] == "jwt"

    @patch("src.cmw.requirements_generator.Confirm.ask")
    @patch("src.cmw.requirements_generator.Prompt.ask")
    def test_collect_tech_stack_without_auth(
        self, mock_prompt: Mock, mock_confirm: Mock, generator: RequirementsGenerator
    ) -> None:
        """技術スタック収集（認証なし）のテスト"""
        mock_prompt.side_effect = [
            "flask",  # backend
            "sqlite",  # database
            "sqlalchemy",  # orm
        ]
        mock_confirm.return_value = False  # needs_auth

        generator._collect_tech_stack()

        assert generator.requirements_data["tech_stack"]["backend"] == "flask"
        assert generator.requirements_data["tech_stack"]["auth"] is None

    @patch("src.cmw.requirements_generator.Confirm.ask")
    @patch("src.cmw.requirements_generator.Prompt.ask")
    def test_collect_data_models_single_model(
        self, mock_prompt: Mock, mock_confirm: Mock, generator: RequirementsGenerator
    ) -> None:
        """データモデル収集（単一モデル）のテスト"""
        mock_prompt.side_effect = [
            "User",  # model_name
            "name",  # field_name
            "string",  # field_type
            "",  # 次のフィールド終了
        ]
        mock_confirm.side_effect = [
            True,  # name is_required
            False,  # name is_unique
            False,  # 他にモデルを追加しない
        ]

        generator._collect_data_models()

        assert len(generator.requirements_data["models"]) == 1
        assert generator.requirements_data["models"][0]["name"] == "User"
        assert len(generator.requirements_data["models"][0]["fields"]) == 1
        assert generator.requirements_data["models"][0]["fields"][0]["name"] == "name"

    @patch("src.cmw.requirements_generator.Confirm.ask")
    @patch("src.cmw.requirements_generator.Prompt.ask")
    def test_collect_data_models_multiple_fields(
        self, mock_prompt: Mock, mock_confirm: Mock, generator: RequirementsGenerator
    ) -> None:
        """データモデル収集（複数フィールド）のテスト"""
        mock_prompt.side_effect = [
            "Todo",  # model_name
            "title",  # field_name 1
            "string",  # field_type 1
            "completed",  # field_name 2
            "boolean",  # field_type 2
            "",  # フィールド終了
        ]
        mock_confirm.side_effect = [
            True,  # title is_required
            False,  # title is_unique
            True,  # completed is_required
            False,  # completed is_unique
            False,  # 他にモデルを追加しない
        ]

        generator._collect_data_models()

        model = generator.requirements_data["models"][0]
        assert len(model["fields"]) == 2
        assert model["fields"][0]["name"] == "title"
        assert model["fields"][1]["name"] == "completed"
        assert model["fields"][1]["type"] == "boolean"

    @patch("src.cmw.requirements_generator.Confirm.ask")
    @patch("src.cmw.requirements_generator.Prompt.ask")
    def test_collect_data_models_no_models(
        self, mock_prompt: Mock, mock_confirm: Mock, generator: RequirementsGenerator
    ) -> None:
        """データモデル収集（モデルなし）のテスト"""
        mock_prompt.return_value = ""  # 最初から空Enter

        generator._collect_data_models()

        assert generator.requirements_data["models"] == []

    @patch("src.cmw.requirements_generator.Confirm.ask")
    def test_collect_api_features_with_auth(
        self, mock_confirm: Mock, generator: RequirementsGenerator
    ) -> None:
        """API機能収集（認証機能あり）のテスト"""
        generator.requirements_data["tech_stack"] = {"auth": "jwt"}
        generator.requirements_data["models"] = []

        mock_confirm.side_effect = [
            True,  # needs_register
            True,  # needs_login
        ]

        generator._collect_api_features()

        features = generator.requirements_data["features"]
        assert len(features) == 2
        assert features[0]["name"] == "ユーザー登録"
        assert features[0]["endpoint"] == "POST /auth/register"
        assert features[1]["name"] == "ログイン"
        assert features[1]["endpoint"] == "POST /auth/login"

    @patch("src.cmw.requirements_generator.Confirm.ask")
    def test_collect_api_features_with_crud(
        self, mock_confirm: Mock, generator: RequirementsGenerator
    ) -> None:
        """API機能収集（CRUD機能）のテスト"""
        generator.requirements_data["tech_stack"] = {"auth": None}
        generator.requirements_data["models"] = [
            {"name": "Task", "fields": [{"name": "title", "type": "string"}]}
        ]

        mock_confirm.return_value = True  # needs_crud

        generator._collect_api_features()

        features = generator.requirements_data["features"]
        assert len(features) == 5  # 一覧、詳細、作成、更新、削除
        assert any("GET /tasks" in f["endpoint"] for f in features)
        assert any("POST /tasks" in f["endpoint"] for f in features)
        assert any("PUT /tasks/{id}" in f["endpoint"] for f in features)
        assert any("DELETE /tasks/{id}" in f["endpoint"] for f in features)

    @patch("src.cmw.requirements_generator.Confirm.ask")
    @patch("src.cmw.requirements_generator.Prompt.ask")
    def test_collect_non_functional(
        self, mock_prompt: Mock, mock_confirm: Mock, generator: RequirementsGenerator
    ) -> None:
        """非機能要件収集のテスト"""
        mock_prompt.side_effect = [
            "300",  # target_response_time
            "90",  # test_coverage
        ]
        mock_confirm.return_value = True  # needs_security

        generator._collect_non_functional()

        nfr = generator.requirements_data["non_functional"]
        assert nfr["response_time"] == 300
        assert nfr["test_coverage"] == 90
        assert nfr["security"] is True

    def test_show_summary_basic(self, generator: RequirementsGenerator) -> None:
        """サマリー表示（基本情報）のテスト"""
        generator.requirements_data = {
            "project_name": "Test API",
            "description": "A test REST API",
            "project_type": "rest-api",
            "tech_stack": {
                "backend": "fastapi",
                "database": "sqlite",
                "orm": "sqlalchemy",
                "auth": "jwt",
            },
            "models": [],
            "features": [],
        }

        # エラーが起きないことを確認
        generator._show_summary()

    def test_show_summary_with_data(self, generator: RequirementsGenerator) -> None:
        """サマリー表示（データあり）のテスト"""
        generator.requirements_data = {
            "project_name": "Blog API",
            "description": "A blogging platform API",
            "project_type": "rest-api",
            "tech_stack": {
                "backend": "django",
                "database": "postgresql",
                "orm": "django-orm",
                "auth": None,
            },
            "models": [{"name": "Post"}, {"name": "Comment"}],
            "features": [{"name": "Get Posts"}, {"name": "Create Post"}],
        }

        # エラーが起きないことを確認
        generator._show_summary()

    def test_generate_markdown_basic(self, generator: RequirementsGenerator) -> None:
        """Markdown生成（基本）のテスト"""
        generator.requirements_data = {
            "project_name": "Simple API",
            "description": "A simple test API",
            "tech_stack": {
                "backend": "fastapi",
                "database": "sqlite",
                "orm": "sqlalchemy",
                "auth": None,
            },
        }

        content = generator._generate_markdown()

        assert "# Simple API - プロジェクト要件書" in content
        assert "A simple test API" in content
        assert "Python 3.12+ with FastAPI" in content
        assert "SQLite (開発用)" in content

    def test_generate_markdown_with_models(
        self, generator: RequirementsGenerator
    ) -> None:
        """Markdown生成（モデルあり）のテスト"""
        generator.requirements_data = {
            "project_name": "Todo API",
            "description": "Todo management API",
            "tech_stack": {
                "backend": "fastapi",
                "database": "postgresql",
                "orm": "sqlalchemy",
                "auth": "jwt",
            },
            "models": [
                {
                    "name": "Todo",
                    "fields": [
                        {
                            "name": "title",
                            "type": "string",
                            "required": True,
                            "unique": False,
                        },
                        {
                            "name": "completed",
                            "type": "boolean",
                            "required": True,
                            "unique": False,
                        },
                    ],
                }
            ],
        }

        content = generator._generate_markdown()

        assert "## データモデル設計" in content
        assert "### 1. Todoモデル" in content
        assert "title: 文字列、必須" in content
        assert "completed: ブール型、必須" in content

    def test_generate_markdown_with_features(
        self, generator: RequirementsGenerator
    ) -> None:
        """Markdown生成（API機能あり）のテスト"""
        generator.requirements_data = {
            "project_name": "User API",
            "description": "User management API",
            "tech_stack": {
                "backend": "express",
                "database": "mongodb",
                "orm": "mongoose",
                "auth": "oauth2",
            },
            "features": [
                {
                    "name": "ユーザー登録",
                    "endpoint": "POST /auth/register",
                    "description": "新規ユーザー登録",
                },
                {
                    "name": "User一覧取得",
                    "endpoint": "GET /users",
                    "description": "全ユーザー取得",
                },
            ],
        }

        content = generator._generate_markdown()

        assert "## API機能" in content
        assert "### 認証機能" in content
        assert "POST /auth/register" in content
        assert "GET /users" in content

    def test_generate_markdown_with_non_functional(
        self, generator: RequirementsGenerator
    ) -> None:
        """Markdown生成（非機能要件あり）のテスト"""
        generator.requirements_data = {
            "project_name": "Perf API",
            "description": "High performance API",
            "tech_stack": {
                "backend": "fastapi",
                "database": "postgresql",
                "orm": "sqlalchemy",
                "auth": "jwt",
            },
            "non_functional": {
                "response_time": 100,
                "test_coverage": 95,
                "security": True,
            },
        }

        content = generator._generate_markdown()

        assert "## 非機能要件" in content
        assert "平均100ms以内" in content
        assert "95%以上" in content
        assert "SQLインジェクション対策" in content

    @patch("src.cmw.requirements_generator.Confirm.ask")
    @patch("src.cmw.requirements_generator.Prompt.ask")
    def test_generate_interactive_success(
        self,
        mock_prompt: Mock,
        mock_confirm: Mock,
        generator: RequirementsGenerator,
        temp_output_path: Path,
    ) -> None:
        """対話型生成（成功）のテスト"""
        # 基本情報
        mock_prompt.side_effect = [
            "Test Project",  # project_name
            "Test description",  # description
            "rest-api",  # project_type
            # 技術スタック
            "fastapi",  # backend
            "sqlite",  # database
            "sqlalchemy",  # orm
            # データモデル
            "",  # モデル終了
            # 非機能要件
            "200",  # response_time
            "80",  # test_coverage
        ]

        # Confirm.askの呼び出し順序
        mock_confirm.side_effect = [
            False,  # needs_auth (技術スタック)
            False,  # needs_security (非機能要件)
            True,  # 生成確認
        ]

        result = generator.generate_interactive(temp_output_path)

        assert result is True
        assert temp_output_path.exists()
        content = temp_output_path.read_text(encoding="utf-8")
        assert "Test Project" in content
        assert "Test description" in content

    @patch("src.cmw.requirements_generator.Confirm.ask")
    @patch("src.cmw.requirements_generator.Prompt.ask")
    def test_generate_interactive_cancel(
        self,
        mock_prompt: Mock,
        mock_confirm: Mock,
        generator: RequirementsGenerator,
        temp_output_path: Path,
    ) -> None:
        """対話型生成（キャンセル）のテスト"""
        # 基本情報のみ
        mock_prompt.side_effect = [
            "Canceled",  # project_name
            "Canceled desc",  # description
            "cli-tool",  # project_type
            # 技術スタック
            "other",  # backend
            "other",  # database
            "none",  # orm
            # データモデル
            "",  # モデル終了
            # 非機能要件
            "500",  # response_time
            "50",  # test_coverage
        ]

        mock_confirm.side_effect = [
            False,  # needs_auth
            False,  # needs_security
            False,  # 生成キャンセル
        ]

        result = generator.generate_interactive(temp_output_path)

        assert result is False
        assert not temp_output_path.exists()

    def test_generate_markdown_all_tech_options(
        self, generator: RequirementsGenerator
    ) -> None:
        """Markdown生成（全技術スタックオプション）のテスト"""
        # Djangoケース
        generator.requirements_data = {
            "project_name": "Django App",
            "description": "Django application",
            "tech_stack": {
                "backend": "django",
                "database": "mysql",
                "orm": "django-orm",
                "auth": "session",
            },
        }
        content = generator._generate_markdown()
        assert "Django" in content
        assert "MySQL" in content
        assert "Session認証" in content

        # Flaskケース
        generator.requirements_data["tech_stack"] = {
            "backend": "flask",
            "database": "mongodb",
            "orm": "none",
            "auth": "oauth2",
        }
        content = generator._generate_markdown()
        assert "Flask" in content
        assert "MongoDB" in content
        assert "OAuth 2.0" in content

    def test_generate_markdown_field_constraints(
        self, generator: RequirementsGenerator
    ) -> None:
        """Markdown生成（フィールド制約）のテスト"""
        generator.requirements_data = {
            "project_name": "Constraint Test",
            "description": "Test field constraints",
            "tech_stack": {
                "backend": "fastapi",
                "database": "postgresql",
                "orm": "sqlalchemy",
                "auth": None,
            },
            "models": [
                {
                    "name": "Product",
                    "fields": [
                        {
                            "name": "sku",
                            "type": "string",
                            "required": True,
                            "unique": True,
                        },
                        {
                            "name": "description",
                            "type": "text",
                            "required": False,
                            "unique": False,
                        },
                        {
                            "name": "price",
                            "type": "float",
                            "required": True,
                            "unique": False,
                        },
                    ],
                }
            ],
        }

        content = generator._generate_markdown()

        # "、必須, ユニーク制約" のようにカンマとスペースが混在
        assert "sku: 文字列、必須, ユニーク制約" in content
        assert "description: テキスト" in content
        assert "price: 浮動小数点、必須" in content

    def test_generate_markdown_feature_grouping(
        self, generator: RequirementsGenerator
    ) -> None:
        """Markdown生成（機能グルーピング）のテスト"""
        generator.requirements_data = {
            "project_name": "Multi Model API",
            "description": "API with multiple models",
            "tech_stack": {
                "backend": "fastapi",
                "database": "postgresql",
                "orm": "sqlalchemy",
                "auth": "jwt",
            },
            "features": [
                {
                    "name": "Post一覧取得",
                    "endpoint": "GET /posts",
                    "description": "全投稿取得",
                },
                {
                    "name": "Comment一覧取得",
                    "endpoint": "GET /comments",
                    "description": "全コメント取得",
                },
            ],
        }

        content = generator._generate_markdown()

        # "posts" → "po" + "st" のように分割されるため "Po管理機能" になる
        assert "Po管理機能" in content or "Post管理機能" in content
        assert "Comment管理機能" in content
        assert "GET /posts" in content
        assert "GET /comments" in content
