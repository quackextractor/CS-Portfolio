import os
import pandas as pd
import pytest
from src.build_dataset import build_dataset
from unittest.mock import patch


@pytest.fixture
def mock_processing_env(tmp_path):
    # Setup temporary directories and config
    raw_pos = tmp_path / "raw_pos"
    raw_neg = tmp_path / "raw_neg"
    processed = tmp_path / "processed"
    raw_pos.mkdir()
    raw_neg.mkdir()
    processed.mkdir()

    config = {
        "data": {
            "raw_positive_dir": str(raw_pos),
            "raw_negative_dir": str(raw_neg),
            "processed_dir": str(processed),
            "dataset_csv": str(processed / "dataset.csv"),
        },
        "model": {
            "img_size": 128,
            "face_detector_model_path": "fake.task"
        }
    }

    return config


@patch("src.build_dataset.load_config")
@patch("src.build_dataset.process_images")
def test_split_integrity_by_video(mock_process, mock_load, mock_processing_env):
    mock_load.return_value = mock_processing_env

    # Simulate records from 2 videos for each label
    # Video A: 10 frames, Video B: 10 frames
    records = []
    for label in [0, 1]:
        prefix = "pos" if label == 1 else "neg"
        for video_id in ["A", "B", "C", "D"]:  # 4 videos per label to ensure splits are non-empty
            unique_video_id = f"{prefix}_{video_id}"
            for i in range(5):
                records.append({
                    "filepath": f"data/processed/{prefix}/video_{unique_video_id}_frame_{i}.jpg",
                    "label": label
                })

    # First call for positive, second for negative
    mock_process.side_effect = [
        [r for r in records if r['label'] == 1],
        [r for r in records if r['label'] == 0]
    ]

    build_dataset()

    df = pd.read_csv(mock_processing_env["data"]["dataset_csv"])

    # Check that for each video, all its frames are in the same split
    def get_video_name(path):
        return os.path.basename(path).rsplit('_', 1)[0]

    df['video_name'] = df['filepath'].apply(get_video_name)

    for video in df['video_name'].unique():
        splits_for_video = df[df['video_name'] == video]['split'].unique()
        assert len(splits_for_video) == 1, f"Video {video} leaked across splits: {splits_for_video}"

    # Also check that we have all three splits
    assert set(df['split'].unique()) == {"train", "val", "test"}
