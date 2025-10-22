import pytest

from code_review.config import DEFAULT_CONFIG, TomlConfigManager
from code_review.exceptions import ConfigurationError
from code_review.plugins.docker.schemas import DockerImageSchema


class TestTomlConfigManager:
    @pytest.fixture
    def config_manager(self, tmp_path):
        """Create a TomlConfigManager with a temporary config directory."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        return TomlConfigManager(config_dir=config_dir)

    def test_init_with_default_config(self, tmp_path):
        """Test initialization with default configuration."""
        manager = TomlConfigManager(config_dir=tmp_path)
        assert manager.config_data == DEFAULT_CONFIG
        assert manager.config_file == tmp_path / "config.toml"

    def test_init_with_custom_config(self, tmp_path):
        """Test initialization with custom configuration."""
        custom_config = {"test_key": "test_value"}
        TomlConfigManager(config_dir=tmp_path, config_file_name="custom.toml", default_config=custom_config)

    def test_save_and_load_config(self, config_manager, tmp_path):
        """Test saving and loading configuration."""
        config_manager.save_config()  # Create a sample config file
        print("Configuration file saved.", config_manager.config_file)
        assert config_manager.config_file.exists()
        loaded_config = config_manager.load_config()

        for name, image_schema in loaded_config["docker_images"].items():
            assert name in DEFAULT_CONFIG["docker_images"]
            assert isinstance(image_schema, DockerImageSchema)

    def test_load_config_old_versions(self, fixtures_folder):
        config_manager = TomlConfigManager(
            config_dir=fixtures_folder ,
            config_file_name="config-sample_v0.10.0.toml",
        )
        try:
            loaded_config = config_manager.load_config()
        except ConfigurationError as e:
            assert str(e) == ("Type error in config file: code_review.plugins.docker.schemas.DockerImageSchema() "
                              "argument after ** must be a mapping, not str")
