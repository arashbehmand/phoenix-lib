"""Tests for phoenix_lib.config.yaml_loader."""

from phoenix_lib.config.yaml_loader import (CONFIG_FILE_ENV_VAR,
                                            load_yaml_config)


class TestLoadYamlConfig:
    def test_returns_empty_dict_when_no_paths(self):
        result = load_yaml_config()
        assert result == {}

    def test_returns_empty_dict_for_nonexistent_local_path(self, tmp_path):
        result = load_yaml_config(local_path=tmp_path / "missing.yaml")
        assert result == {}

    def test_loads_local_path(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text("key: value\nnumber: 42", encoding="utf-8")
        result = load_yaml_config(local_path=cfg_file)
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_loads_nested_yaml(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text("outer:\n  inner: deep", encoding="utf-8")
        result = load_yaml_config(local_path=cfg_file)
        assert result["outer"]["inner"] == "deep"

    def test_empty_yaml_returns_empty_dict(self, tmp_path):
        cfg_file = tmp_path / "empty.yaml"
        cfg_file.write_text("", encoding="utf-8")
        result = load_yaml_config(local_path=cfg_file)
        assert result == {}

    def test_docker_path_takes_precedence_over_local(self, tmp_path):
        local_file = tmp_path / "local.yaml"
        local_file.write_text("source: local", encoding="utf-8")
        docker_file = tmp_path / "docker.yaml"
        docker_file.write_text("source: docker", encoding="utf-8")
        result = load_yaml_config(local_path=local_file, docker_path=docker_file)
        assert result["source"] == "docker"

    def test_local_used_when_docker_not_exists(self, tmp_path):
        local_file = tmp_path / "local.yaml"
        local_file.write_text("source: local", encoding="utf-8")
        result = load_yaml_config(
            local_path=local_file, docker_path=tmp_path / "nonexistent.yaml"
        )
        assert result["source"] == "local"

    def test_env_var_overrides_all(self, tmp_path, monkeypatch):
        local_file = tmp_path / "local.yaml"
        local_file.write_text("source: local", encoding="utf-8")
        env_file = tmp_path / "env_config.yaml"
        env_file.write_text("source: env", encoding="utf-8")
        monkeypatch.setenv(CONFIG_FILE_ENV_VAR, str(env_file))
        result = load_yaml_config(local_path=local_file)
        assert result["source"] == "env"

    def test_env_var_nonexistent_path_returns_empty(self, tmp_path, monkeypatch):
        monkeypatch.setenv(CONFIG_FILE_ENV_VAR, str(tmp_path / "ghost.yaml"))
        result = load_yaml_config()
        assert result == {}

    def test_invalid_yaml_returns_empty_dict(self, tmp_path):
        cfg_file = tmp_path / "bad.yaml"
        cfg_file.write_text("key: [unclosed bracket", encoding="utf-8")
        result = load_yaml_config(local_path=cfg_file)
        assert result == {}

    def test_returns_dict_type(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text("x: 1", encoding="utf-8")
        result = load_yaml_config(local_path=cfg_file)
        assert isinstance(result, dict)
