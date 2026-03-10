[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.12.0-blue.svg)](https://github.com/quackextractor/CS-Portfolio)

# Miro Face Detector

This repository contains the source code, data pipeline, and documentation generator for the Miro Face Detector. This is a custom machine learning computer vision application capable of detecting a specific person in a live camera feed and distinguishing them from other individuals.

## Prerequisites

To generate the documentation and run the machine learning pipeline, you must have the following installed on your Windows system:
* Python 3.8 or newer
* MiKTeX (for generating the PDF documentation)

## Installing MiKTeX on Windows

MiKTeX is required to compile the LaTeX documentation into a PDF. You can install and configure it seamlessly via the Windows Command Line using the Windows Package Manager.

1. Open Command Prompt or PowerShell as an Administrator.
2. Run the following command to download and install MiKTeX:
   `winget install MiKTeX.MiKTeX`
3. Configure MiKTeX to automatically install any missing packages on the fly to prevent compilation errors:
   `initexmf --admin --set-config-value [MPM]AutoInstall=1`
4. Close and reopen your terminal so the system recognizes the newly added `pdflatex` command.

## Installing Python Dependencies

The project uses several external Python libraries for data scraping, image processing, and documentation generation. We highly recommend using the included batch script on Windows to automate the entire setup process.

1. Open your terminal and navigate to the root directory of this project.
2. Run the automated setup script:
   `setup.bat`
3. Once the setup is complete, activate the virtual environment:
   - Command Prompt: `.venv\Scripts\activate`
   - Git Bash: `source .venv/Scripts/activate`

If you are setting this up on Mac or Linux, you will need to run the steps manually:
1. Create a virtual environment: `python -m venv .venv`
2. Activate the virtual environment: `source .venv/bin/activate`
3. Install the required packages: `pip install -r requirements.txt`
4. Download the required MediaPipe model files: `python main.py setup`

## Using the Command Line Interface (CLI)

The project is operated entirely through a unified CLI managed by `main.py`. Once your virtual environment is active and dependencies are installed, you can use the following commands:

* `python main.py setup`: Download required MediaPipe model files (already handled if you used setup.bat).
* `python main.py scrape`: Download portrait images from Pexels for the negative class.
* `python main.py extract <video_path>`: Extract frames from personal videos for the positive class.
  * Optionally, use `python main.py extract <directory_path> --batch` to process all videos in a specified folder.
* `python main.py build`: Clean, crop, and normalize raw images to build the dataset CSV.
  * Optionally, use `--no_skip_blurry` to retain blurry faces and `--blur_threshold <value>` to adjust the sensitivity.
* `python main.py run`: Launch the live webcam face detection application.
  * Optionally, use `python main.py run --video <video_path>` to run inference on a local video file with playback controls (`Space` to pause, `a`/`d` to skip).
  * Optionally, use `python main.py run --screen` to run inference on your primary screen directly.
* `python main.py visualize`: Generate an activation maximization image showing what the model has learned.
  * Optionally, use `--iterations <int>` and `--lr <float>` to tune the visualization process.
* `python main.py docs`: Generate the LaTeX project documentation PDF.

## Generating the Documentation

The documentation is generated dynamically using a Python script that builds training graphs and compiles LaTeX source code.

1. Ensure your virtual environment is activated.
2. Run the generator script via the CLI:
   `python main.py docs`
3. The final compiled PDF will be located in the `docs/` directory.

### Model Visualization
You can visualize what the model "sees" by running the activation maximization script.
```bash
python main.py visualize
```
This will generate images representing the features the model looks for:

| Class Prototype | Filter Grid |
| :---: | :---: |
| ![Class Prototype](docs/activation_maximization_placeholder.png) | ![Filter Grid](docs/filter_grid_placeholder.png) |

*(Note: The images above are placeholders. Run the command to generate real visualizations based on your trained model.)*

## Project Structure

* `src/`: Authored Python code including API scrapers, video extractors, data builders, and the final live application.
* `vendor/`: Foreign code, third party libraries, and external snippets not authored by you.
* `data/`: Divided into `raw/` and `processed/` directories to store the collected image dataset and the final `dataset.csv`.
* `notebooks/`: Google Colab Jupyter Notebooks used for cloud based model training.
* `models/`: Exported weights of the trained neural network and the downloaded MediaPipe face detector model.
* `docs/`: Generated PDF project documentation.
* `out/`: Temporary build folder for LaTeX compilation and graph generation.
* `vendor/setup_models.py`: Helper module that downloads required MediaPipe model files (invoked via `python main.py setup`).
* `setup.bat`: Windows batch script that creates a virtual environment, installs dependencies, and downloads models in one step.

## Deployment and Execution Instructions

To deploy the application on the target school computer without an IDE, ensure you have an external USB webcam connected and follow these command-line instructions:

### Prerequisites
* Python 3.10+
* Internet connection (for initial setup)
* A connected webcam

### Installation Steps

1. **Clone or Extract the Project:**
   Navigate into the project root directory.
   ```bash
   cd AI-ML-project

```

2. **Run the Automated Setup (Windows):**
This script strictly isolates the application dependencies by creating a virtual environment, installing packages, and downloading required MediaPipe models automatically.
```bash
setup.bat

```


*(Note: If on Mac/Linux, manually run `python -m venv .venv`, install from `requirements.txt`, and run `python main.py setup`)*
3. **Activate the Virtual Environment:**
* Windows (Command Prompt): `.venv\Scripts\activate.bat`
* Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`
* Windows (Git Bash): `source .venv/Scripts/activate`
* Mac/Linux: `source .venv/bin/activate`


4. **Run the Application:**
Execute the core application script via the unified CLI.
```bash
python main.py run

```


5. **Quit:**
Press the `q` key on your keyboard to instantly quit the application and release the camera stream.

### Controls
| Key | Action |
| --- | --- |
| `q` / `Esc` | Quit |
| `Space` | Pause/Resume (Video only) |
| `a` / `d` | Skip backward/forward (Video only) |
| `g` | Toggle Grad-CAM |
| `[` / `]` | Decrease/Increase Heatmap Sensitivity |
| `m` | Toggle Horizontal Mirror |
