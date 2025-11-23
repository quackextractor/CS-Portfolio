from config import INPUT_FILE_PATH
from log_processor import LogProcessor

if __name__ == "__main__":
    LogProcessor(INPUT_FILE_PATH).start()