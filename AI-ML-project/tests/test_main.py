from unittest.mock import patch, MagicMock
import unittest
from main import main


class TestMainCLI(unittest.TestCase):
    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('importlib.util.spec_from_file_location')
    def test_setup_command(self, mock_spec, mock_args):
        # Mock 'setup' command
        args = MagicMock()
        args.command = 'setup'
        mock_args.return_value = args

        with patch('vendor.setup_models.download_models') as mock_download:
            cfg_data = (
                "model:\n  output_path: 'test.keras'\n"
                "  img_size: 128\ndata:\n  dataset_csv: 'test.csv'"
            )
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', unittest.mock.mock_open(read_data=cfg_data)):
                    try:
                        main()
                        mock_download.assert_called_once()
                    except SystemExit:
                        pass

    @patch('main.argparse.ArgumentParser.parse_args')
    def test_extract_command_with_config(self, mock_args):
        # Mock 'extract' command with --config
        args = MagicMock()
        args.command = 'extract'
        args.config = 'batch_extract.json'
        args.video_path = None
        args.output_dir = 'data/raw/positive'
        args.frame_rate = 5
        args.batch = False
        mock_args.return_value = args

        with patch('vendor.utils.video_extractor.extract_frames') as mock_extract:
            cfg_data = (
                "model:\n  output_path: 'test.keras'\n"
                "  img_size: 128\ndata:\n  dataset_csv: 'test.csv'"
            )
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', unittest.mock.mock_open(read_data=cfg_data)):
                    try:
                        main()
                        mock_extract.assert_called_once()
                        call_args = mock_extract.call_args[1]
                        self.assertEqual(call_args['config_path'], 'batch_extract.json')
                        self.assertEqual(call_args['frame_rate'], 5)
                        self.assertEqual(call_args['batch'], False)
                    except SystemExit:
                        pass

    @patch('main.argparse.ArgumentParser.parse_args')
    def test_scrape_command(self, mock_args):
        # Mock 'scrape' command
        args = MagicMock()
        args.command = 'scrape'
        args.query = ['test query']
        args.total = 100
        args.output_dir = 'test_dir'
        mock_args.return_value = args

        with patch('src.pexels_scraper.download_pexels_images') as mock_scrape:
            cfg_data = (
                "model:\n  output_path: 'test.keras'\n"
                "  img_size: 128\ndata:\n  dataset_csv: 'test.csv'"
            )
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', unittest.mock.mock_open(read_data=cfg_data)):
                    try:
                        main()
                        mock_scrape.assert_called_once()
                        # Verify the first two args
                        args, kwargs = mock_scrape.call_args
                        self.assertEqual(args[0], ['test query'])
                        self.assertEqual(args[1], 100)
                    except SystemExit:
                        pass

    @patch('main.argparse.ArgumentParser.parse_args')
    def test_visualize_command(self, mock_args):
        # Mock 'visualize' command
        args = MagicMock()
        args.command = 'visualize'
        args.model = 'test.keras'
        args.output_dir = 'test_dir'
        args.iterations = 50
        args.lr = 0.5
        mock_args.return_value = args

        with patch('vendor.utils.generate_activation_max.generate_activation_image') as mock_viz:
            cfg_data = (
                "model:\n  output_path: 'test.keras'\n"
                "  img_size: 128\ndata:\n  dataset_csv: 'test.csv'"
            )
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', unittest.mock.mock_open(read_data=cfg_data)):
                    try:
                        main()
                        mock_viz.assert_called_once_with('test.keras', unittest.mock.ANY, 50, 0.5)
                    except SystemExit:
                        pass


if __name__ == '__main__':
    unittest.main()
