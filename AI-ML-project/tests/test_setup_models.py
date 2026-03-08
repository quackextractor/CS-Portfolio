import yaml
import pytest
from unittest.mock import patch
from vendor.setup_models import _load_models, download_models


@pytest.fixture
def temp_config(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_data = {
        "models": {
            "downloads": [
                {
                    "url": "http://example.com/model.task",
                    "dest": "vendor/models/model.task",
                    "description": "Test Model",
                }
            ]
        }
    }
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)
    return str(config_file)


def test_load_models_reads_config(temp_config):
    models = _load_models(temp_config)
    assert len(models) == 1
    assert models[0]["description"] == "Test Model"


@patch("vendor.setup_models.urllib.request.urlretrieve")
@patch("vendor.setup_models.os.path.isfile")
@patch("vendor.setup_models._load_models")
def test_download_models_calls_urlretrieve(
    mock_load, mock_isfile, mock_retrieve, temp_config
):
    mock_load.return_value = [
        {"url": "http://test.com", "dest": "dest/path", "description": "desc"}
    ]
    mock_isfile.return_value = False

    download_models(temp_config)

    mock_retrieve.assert_called_once_with("http://test.com", "dest/path")


@patch("vendor.setup_models.urllib.request.urlretrieve")
@patch("vendor.setup_models.os.path.isfile")
@patch("vendor.setup_models._load_models")
def test_download_models_already_exists(
    mock_load, mock_isfile, mock_retrieve, temp_config
):
    mock_load.return_value = [
        {"url": "http://test.com", "dest": "dest/path", "description": "desc"}
    ]
    mock_isfile.return_value = True

    download_models(temp_config)

    mock_retrieve.assert_not_called()


def test_download_models_empty_config(tmp_path):
    config_file = tmp_path / "empty_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump({}, f)

    # Should not raise any error
    download_models(str(config_file))
