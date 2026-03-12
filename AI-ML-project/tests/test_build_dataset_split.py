import unittest
from unittest.mock import patch
from src.build_dataset import run_processing, run_building


class TestBuildDatasetSplit(unittest.TestCase):
    @patch('src.build_dataset.load_config')
    @patch('src.build_dataset.process_images')
    @patch('os.path.exists')
    def test_run_processing_target_positive(self, mock_exists, mock_process, mock_config):
        mock_config.return_value = {
            "data": {
                "raw_positive_dir": "raw_pos",
                "raw_negative_dir": "raw_neg",
                "processed_dir": "proc"
            },
            "model": {"img_size": 128}
        }
        mock_exists.return_value = True

        run_processing(class_target="positive")

        # Should only call process_images for positive
        self.assertEqual(mock_process.call_count, 1)
        _, kwargs = mock_process.call_args
        self.assertEqual(kwargs['label'], 1)

    @patch('src.build_dataset.load_config')
    @patch('os.walk')
    @patch('os.path.exists')
    @patch('pandas.DataFrame.to_csv')
    def test_run_building(self, mock_to_csv, mock_exists, mock_walk, mock_config):
        mock_config.return_value = {
            "data": {
                "processed_dir": "proc",
                "dataset_csv": "dataset.csv"
            }
        }
        mock_exists.return_value = True
        # Mocking os.walk for positive and negative
        mock_walk.side_effect = [
            [("proc/positive/vid1", [], ["frame1.jpg"])],
            [("proc/negative/vid2", [], ["frame2.jpg"])],
        ]

        run_building()

        # Verify it scanned the directories
        self.assertEqual(mock_walk.call_count, 2)
        # Verify it tried to save the CSV
        mock_to_csv.assert_called_once()


if __name__ == '__main__':
    unittest.main()
