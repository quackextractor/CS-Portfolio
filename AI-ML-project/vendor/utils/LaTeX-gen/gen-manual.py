import os
import subprocess
import shutil

# Dynamically find the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Output directories set relative to the script's location
OUT_DIR = os.path.join(SCRIPT_DIR, "out")
DOCS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", "docs"))
FINAL_PDF_PATH = os.path.join(DOCS_DIR, "user_manual.pdf")

def generate_latex_content():
    """Generates the LaTeX source code for the user manual."""
    latex_template = r"""\documentclass[12pt, a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{hyperref}
\usepackage{titlesec}
\usepackage{parskip}
\usepackage{graphicx}
\usepackage{float}

\begin{document}

\begin{titlepage}
    \centering
    \vspace*{1cm}

    {\large \textbf{Střední průmyslová škola elektrotechnická}} \\
    {\large \textbf{Informační technologie}} \\
    Střední průmyslová škola elektrotechnická, Praha 2, Ječná 30 \\

    \vspace{8cm}

    {\Large \textbf{Miro Face Detector}} \\
    \vspace{0.5cm}
    {\Large User Manual} \\

    \vfill

    {\large Miro Slezák} \\
    {\large Information Technology} \\
    {\large 2026} \\

    \vspace*{1cm}
\end{titlepage}

\newpage
\tableofcontents
\newpage

\section{Introduction}

This manual provides a comprehensive, step-by-step guide to operating the Miro Face Detector. It covers the entire pipeline, from recording your initial training data to running the real-time webcam inference application.

\section{Step 1: Environment Setup}

Before collecting data, ensure your system is prepared.

\begin{enumerate}
    \item \textbf{Windows Automated Setup:} Open your terminal in the project root and run \texttt{setup.bat}. This script automatically creates a virtual environment, installs dependencies from \texttt{requirements.txt}, and downloads the required MediaPipe Face Detector model.
    \item \textbf{Manual Setup (Mac/Linux):} 
    \begin{itemize}
        \item Create and activate a virtual environment: \texttt{python -m venv .venv} and \texttt{source .venv/bin/activate}.
        \item Install packages: \texttt{pip install -r requirements.txt}.
        \item Download the MediaPipe model: \texttt{python main.py setup}.
    \end{itemize}
\end{enumerate}

\section{Step 2: Acquiring Data}

The machine learning model requires robust data to distinguish the positive class (you) from the negative class (random people).

\subsection{Recording the Positive Class Video}

You must record a video of yourself to generate the positive dataset.

\textbf{Tips for High-Quality Video Recording:}
\begin{itemize}
    \item \textbf{Lighting:} Ensure your face is evenly lit. Avoid heavy shadows or severe backlighting which can obscure facial features.
    \item \textbf{Angles:} Slowly move your head to capture different angles (front, slight left, slight right, looking slightly up and down).
    \item \textbf{Background:} A neutral, uncluttered background is preferred but not strictly required, as the preprocessing pipeline will crop the background out.
    \item \textbf{Obstructions:} Do not cover your face with hands or accessories during the recording.
\end{itemize}

\subsection{Extracting Video Frames}

Once recorded, place your video file in the project directory. Run the extraction command via the unified CLI.

\texttt{python main.py extract <video\_path> -{}-frame\_rate 5}

\textbf{Parameters:}
\begin{itemize}
    \item \texttt{--frame\_rate}: Controls how many frames are skipped. The default is 5 (extracts 1 frame every 5 frames). Adjust this based on your video length to yield approximately 1438 images.
    \item \texttt{--output\_dir}: The target folder, which defaults to \texttt{data/raw/positive}.
\end{itemize}

\subsection{Scraping the Negative Class}

The application requires images of other people to learn who you are not. Download these via the Pexels API. Ensure your \texttt{.env} file contains your \texttt{PEXELS\_API\_KEY}.

\texttt{python main.py scrape -{}-total 1200}

This command will populate the \texttt{data/raw/negative} directory.

\section{Step 3: Preprocessing and Building the Dataset}
The raw data must be cleaned, cropped, and normalized using MediaPipe. Run the build command:

\texttt{python main.py build}

This process evaluates all images in the \texttt{raw/} directory, discards images with zero or multiple faces, crops valid faces, resizes them to 128x128 pixels, and saves them to \texttt{data/processed/} alongside a generated \texttt{dataset.csv}.

\textbf{Configuration Parameters (\texttt{config.yaml}):}
Before training, you may adjust variables in the \texttt{config.yaml} file:
\begin{itemize}
    \item \texttt{test\_split\_size}: Determines the percentage of data reserved for evaluation (default is 0.2).
    \item \texttt{img\_size}: The pixel resolution for the face crops (default is 128).
\end{itemize}

\section{Step 4: Model Training}
The model is trained using Google Colab.

\begin{enumerate}
    \item Upload the \texttt{notebooks/model\_training.ipynb} file to Google Colab.
    \item Upload your \texttt{config.yaml} and dataset (the \texttt{data/processed/} folder and \texttt{dataset.csv}) to your Google Drive.
    \item Example: drive mounted fine and the location of the dataset is at\\ \texttt{/content/drive/MyDrive/processed}. Ensure your \texttt{config.yaml} reflects these paths.
    \item Execute the cells within the notebook sequentially to train the Convolutional Neural Network (CNN).
    \item Once training is complete, the final weights will be exported as \texttt{miro\_detector.keras}. Download this file and place it in the \texttt{models/} directory within your local project.
\end{enumerate}

\section{Step 5: Running the Application}

With the model trained and loaded, you can launch the live webcam inference application.

\textbf{Launch Command:}
\texttt{python main.py run}

\textbf{Application Operation:}
\begin{itemize}
    \item The app accesses your primary webcam (configurable via \texttt{camera: index} in \texttt{config.yaml}).
    \item \textbf{Video Mode:} You can also run inference on a local video file by executing \texttt{python main.py run --video path/to/video.mp4}.
    \item It draws bounding boxes in real-time, classifying faces as "Miro" (green) or "Unknown" (red).
    \item \textbf{thresholding:} If the detection is overly strict or too lenient, adjust the \texttt{threshold} parameter in \texttt{config.yaml} (default is 0.65).
    \item \textbf{Video Controls:} When in video mode, press the Spacebar to pause/resume playback. You can skip forward and backward 30 frames using the "d" and "a" keys respectfully, or use the interactive slider at the top of the window.
    \item \textbf{Quitting:} Press the \textbf{"q"} key to instantly safely terminate the camera stream and close the application.
\end{itemize}

\end{document}
"""
    return latex_template

def build_pdf(filename="user_manual"):
    """Writes the LaTeX code to a file and compiles it using pdflatex."""
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)

    tex_filename = os.path.join(OUT_DIR, f"{filename}.tex")

    print(f"Generating {tex_filename}...")
    latex_content = generate_latex_content()

    with open(tex_filename, "w", encoding="utf-8") as f:
        f.write(latex_content)

    print("Compiling PDF with pdflatex...")
    try:
        # Run pdflatex twice to resolve TOC references
        subprocess.run(["pdflatex", f"{filename}.tex"], cwd=OUT_DIR, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["pdflatex", f"{filename}.tex"], cwd=OUT_DIR, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
        # Move the final compiled PDF to the docs directory safely
        compiled_pdf = os.path.join(OUT_DIR, f"{filename}.pdf")
        if os.path.exists(FINAL_PDF_PATH):
            os.remove(FINAL_PDF_PATH)
        shutil.move(compiled_pdf, FINAL_PDF_PATH)
    
        print(f"Successfully generated PDF at {FINAL_PDF_PATH}")
    except subprocess.CalledProcessError:
        print("Error: Compilation failed. Please ensure you have a LaTeX distribution installed.")
    except FileNotFoundError:
        print("Error: pdflatex command not found.")


if __name__ == "__main__":
    build_pdf()