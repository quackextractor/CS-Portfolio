import os
import subprocess
import matplotlib.pyplot as plt
import shutil
import yaml
import tensorflow as tf

# Dynamically find the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Output directories set relative to the script's location
OUT_DIR = os.path.join(SCRIPT_DIR, "out")
DOCS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", "docs"))
FINAL_PDF_PATH = os.path.join(DOCS_DIR, "documentation.pdf")


def generate_graphs():
    """Generates sample graphs for the documentation."""
    print("Generating graphs...")
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1. Dataset Distribution Graph
    labels = ['Target (Positive)', 'Random (Negative)']
    counts = [1438, 879]

    plt.figure(figsize=(6, 4))
    plt.bar(labels, counts, color=['blue', 'orange'])
    plt.title('Dataset Class Distribution (Post Cleaning)')
    plt.ylabel('Number of Images')
    plt.savefig(os.path.join(OUT_DIR, 'dataset_distribution.png'))
    plt.close()

    # 2. Model Training History Graph
    epochs = range(1, 11)
    acc = [0.7061, 0.9522, 0.9709, 0.9753, 0.9864, 0.9727, 0.9807, 0.9931, 0.9903, 0.9892]
    val_acc = [0.9526, 0.9698, 0.9806, 0.9828, 0.9591, 0.9849, 0.9892, 0.9892, 0.9849, 0.9871]

    plt.figure(figsize=(6, 4))
    plt.plot(epochs, acc, marker='o', label='Training Accuracy')
    plt.plot(epochs, val_acc, marker='s', label='Validation Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(OUT_DIR, 'training_history.png'))
    # 3. Activation Maximization and Filter Grid
    # We no longer generate placeholders here as professional images 
    # are already provided in the SCRIPT_DIR and referenced in LaTeX.

    # 5. Model Architecture Diagram
    generate_model_diagram()

    print("Graphs generated in", OUT_DIR)


def generate_model_diagram():
    """Generates a block diagram of the CNN architecture using plot_model.

    Uses tf.keras.utils.plot_model which works reliably with any Keras model
    loaded from disk. Falls back to a placeholder image if it fails.
    """
    print("Generating model architecture diagram...")
    config_path = os.path.abspath(
        os.path.join(SCRIPT_DIR, "..", "..", "..", "config.yaml")
    )
    diag_path = os.path.join(OUT_DIR, "model_architecture.png")

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        model_path = os.path.abspath(
            os.path.join(SCRIPT_DIR, "..", "..", "..", config["model"]["output_path"])
        )

        if not os.path.exists(model_path):
            print(f"Model file not found at {model_path}, skipping diagram.")
            return

        model = tf.keras.models.load_model(model_path)
        tf.keras.utils.plot_model(
            model,
            to_file=diag_path,
            show_shapes=True,
            show_layer_names=True,
            dpi=96,
        )
        print(f"Model diagram saved to {diag_path}")
        return

    except Exception as e:
        print(f"Could not generate model diagram: {e}")

    # --- Final fallback: placeholder image ---
    plt.figure(figsize=(8, 10))
    plt.text(
        0.5, 0.5,
        "Model Architecture Diagram\n(Requires a trained model file)",
        ha="center", va="center", fontsize=12,
    )
    plt.axis("off")
    plt.savefig(diag_path)
    plt.close()


def generate_latex_content():
    """Generates the LaTeX source code for the project documentation."""
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

% Opening Page exactly matching reference formatting
\begin{titlepage}
    \centering
    \vspace*{1cm}

    {\large \textbf{Střední průmyslová škola elektrotechnická}} \\
    {\large \textbf{Informační technologie}} \\
    Střední průmyslová škola elektrotechnická, Praha 2, Ječná 30 \\

    \vspace{8cm}

    {\Large \textbf{Target Face Detector}} \\
    \vspace{0.5cm}
    Rozpoznávání obličeje \\

    \vfill

    {\large Miro Slezák} \\
    {\large Information Technology} \\
    {\large 2026} \\

    \vspace*{1cm}
\end{titlepage}

\newpage
\tableofcontents
\newpage

\section{Project Overview}
\textbf{Goal:} Develop a custom machine learning computer vision application capable of detecting a specific person (Target) in a live camera feed and distinguishing them from other individuals.

\textbf{Scope:} The project strictly focuses on creating a proprietary dataset from scratch to train a binary classification model. The software includes a final user facing application that utilizes the trained model for real time inference.

\section{Technology Stack and Justification}

\subsection{Data Sourcing: Pexels API}
The Pexels API provides a generous free tier that allows up to 200 requests per hour. This allows the automated scraping script to download the required negative class images in a single session.

\subsection{Face Detection and Annotation: MediaPipe + OpenCV}
Developed by Google, MediaPipe provides ultrafast face detection. It is used exclusively in the preprocessing pipeline to find faces in raw images and crop them, ensuring the machine learning model only trains on facial features and ignores backgrounds.

\subsection{Machine Learning Model: Convolutional Neural Network (CNN)}
A CNN built with TensorFlow and Keras is utilized. CNNs are specifically designed for spatial data like images, making them the optimal choice for learning the visual features that distinguish specific faces.

To demonstrate a clear understanding of the model architecture, the following outlines the core layers used in this network:
\begin{itemize}
    \item \textbf{Convolutional Layer:} This layer applies sliding filters over the 128x128 input images. It acts like a scanner looking for specific patterns, starting with basic edges and progressing to complex facial structures, creating feature maps.
    \item \textbf{Pooling Layer (Max Pooling):} Following a convolution, this layer downsamples the feature maps. It reduces the spatial dimensions while keeping the most important features, which makes the model run more efficiently and helps prevent overfitting.
    \item \textbf{Flatten Layer:} This layer takes the 2D feature maps created by the convolutional layers and unrolls them into a single 1D vector so the data can be read by a standard neural network.
    \item \textbf{Dense (Fully Connected) Layer:} This is the final classification stage. It takes the unrolled spatial features and calculates the final prediction to determine if the face is Miro (1) or Random (0).
\end{itemize}

\subsection{Model Explainability: Grad-CAM}
To ensure transparency in the model's decision-making process, the application implements Gradient-weighted Class Activation Mapping (Grad-CAM). This technique uses the gradients of any target concept, flowing into the final convolutional layer to produce a coarse localization map highlighting the important regions in the image for predicting the concept.

In this project, Grad-CAM allows the user to see exactly which facial features (e.g., eyes, nose, jawline) the CNN is using to identify "Target", providing a layer of interpretability often missing in "black-box" neural networks.

\subsection{Model Vision: Activation Maximization}
Beyond localizing features in specific images, the project utilizes Activation Maximization to synthesize images that represent the "ideal" input for specific neurons or classes. By performing gradient ascent on a noise image, we can visualize the specific patterns and textures the model has learned to associate with the "Target" class.

Furthermore, the tool allows for visualizing individual convolutional filters, revealing the hierarchy of features from simple edges in early layers to complex facial structures in deeper layers.

\subsection{Model Architecture}
The following diagram illustrates the topological structure of the Convolutional Neural Network developed for this project.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.5\textwidth]{model_architecture.png}
    \caption{Layer-by-layer architectural visualization of the miro\_detector.keras model.}
\end{figure}

\section{Architecture and Pipeline}

The architecture is divided into a data generation pipeline, a cloud based training phase, and a real time local inference application.

\subsection{Phase 1: Data Collection}
To ensure the final cleaned dataset meets the strict requirement of at least 1500 records, the collection scripts oversample data.
\begin{itemize}
    \item \textbf{Positive Class (Target):} A custom script captures frames from multiple videos of the target under varying lighting conditions, generating 1438 initial images saved to the raw data directory. The original unmodified video files are preserved as verifiable proof of non-simulated real data collection.
    \item \textbf{Negative Class (Random):} A script queries the Pexels API for portrait photos and downloads 1200 images into the raw data directory.
\end{itemize}

\subsection{Phase 2: Preprocessing and Attribute Extraction}
\begin{itemize}
    \item All raw images are passed through the MediaPipe Face Detector.
    \item Images containing zero faces or multiple faces are automatically discarded by the script to ensure data cleanliness.
    \item Valid faces are cropped using the generated bounding boxes and resized to a strict 128x128 resolution.
    \item After cropping, the faces are evaluated for sharpness using the Variance of Laplacian method. Any blurry faces below the threshold are automatically excluded from the dataset to prevent false positives.
    \item \textbf{The Data Attributes:} The data loader indexes the images using a \texttt{dataset.csv} file. However, the actual training data attributes (parts) utilized by the CNN are the image matrices themselves. Each 128x128x3 RGB image contains 49,152 distinct pixel attributes that the network learns from.
    \item \textbf{Data Splitting:} The final cleaned dataset is split into portions for training and strictly reserved for testing. The split ratio and random state are centrally managed via \texttt{config.yaml} (\texttt{test\_split\_size} and \texttt{random\_seed}) to ensure adaptability.
\end{itemize}

\subsection{Phase 3: Model Training (Google Colab)}
The processed \texttt{data/} directory and the \texttt{dataset.csv} file are uploaded to Google Drive. A Google Colab Jupyter Notebook mounts the drive, loads the preprocessed true data, and trains the CNN. The final trained model weights are exported as a \texttt{.keras} file and downloaded back to the local project folder.

\subsection{Phase 4: Real World Application (Inference)}
The final software is a Python script executable via the command line on the school PC. It requires an external USB webcam connected to the computer, or alternatively, a pre-recorded video file passed via the \texttt{--video} argument. It accesses the video stream using OpenCV, continuously extracts faces, and passes the cropped faces to the trained CNN.

The application draws a bounding box on the live video feed, labeling the face as either "Miro" or "Unknown". The exact confidence threshold for positive classification is customizable via \texttt{config.yaml} to ensure adaptability in diverse lighting environments. The user safely terminates the camera feed by pressing the "q" key. When watching a pre-recorded video, the user can also press the Spacebar to pause/resume or use "a" and "d" to skip back and forth.

\section{Maintainability and Quality Assurance}
To ensure the project is perfectly maintainable, readable, and adheres to strict software engineering standards, the following practices and architectures are implemented.

\subsection{Testing and Linting}
\begin{itemize}
    \item \textbf{Unit Tests:} The \texttt{pytest} framework is used to write unit tests for the data cleaning and transformation pipeline. This verifies that individual functions perform correctly and provides proof of code comprehension.
    \item \textbf{Linting:} \texttt{flake8} and \texttt{black} are utilized to enforce strict PEP 8 formatting conventions across all authored files in the \texttt{src/} directory. This ensures maximum readability.
\end{itemize}

\subsection{Configuration and Documentation}
\begin{itemize}
    \item \textbf{Configuration Management:} A \texttt{config.yaml} file centralizes all project parameters, such as model hyperparameters, API endpoints, and dataset paths. Sensitive information like API keys are stored in a local \texttt{.env} file, which is strictly excluded from version control.
    \item \textbf{README:} A comprehensive \texttt{README.md} is provided. It includes step by step instructions for setting up the environment, installing dependencies, and launching the software without an IDE.
    \item \textbf{Project Documentation:} The codebase is thoroughly documented using standard Python docstrings. This generated PDF serves as the primary technical documentation detailing the architecture, data origin, and machine learning pipeline.
\end{itemize}

\subsection{Versioning and Workflows}
\begin{itemize}
    \item \textbf{Semantic Versioning:} All releases are tagged using the MAJOR.MINOR.PATCH format (e.g., 1.0.0) to clearly communicate the nature of changes.
    \item \textbf{Changelog:} A \texttt{CHANGELOG.md} file is maintained. It categorizes all project updates into Added, Changed, Deprecated, and Removed sections for every version iteration.
    \item \textbf{Automated Workflows (CI/CD):} GitHub Actions are configured to trigger automatically on every pull request. The workflow executes the \texttt{pytest} suite and runs \texttt{flake8} linting. If any tests fail or formatting rules are broken, the merge is blocked, guaranteeing code quality.
\end{itemize}

\newpage
\section{Data Analysis and Evaluation}

\subsection{Dataset Distribution}
Figure 1 shows the distribution of the positive and negative classes in the generated dataset after the cleaning phase.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.7\textwidth]{dataset_distribution.png}
    \caption{Distribution of positive and negative classes in the cleaned dataset.}
\end{figure}

\subsection{Model Training Performance}
Figure 2 illustrates the training and validation accuracy over time.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.7\textwidth]{training_history.png}
    \caption{Training and validation accuracy across 10 epochs.}
\end{figure}

\subsection{Activation Maximization and Filter Grids}
Figure 3 displays the result of maximizing the output for the "Target" class, representing the model's internal prototype of the target face. Figure 4 shows a grid of various filters from the final convolutional layer, illustrating the diversity of features the model detects.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.5\textwidth]{../activation_maximization.png}
    \caption{Synthesized image maximizing model activation for the Target class.}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.7\textwidth]{../filter_grid.png}
    \caption{Grid of maximized filters from the convolutional layers.}
\end{figure}

\section{Implementation Plan and Code Separation}
To strictly adhere to code authorship requirements, the repository is structured as follows:

\textbf{1. src/ (Authored Code)}
\begin{itemize}
    \item \texttt{pexels\_scraper.py}: Custom script to interface with the API and download images.
    \item \texttt{build\_dataset.py}: Custom original pipeline utilizing the MediaPipe library to crop and resize faces.
    \item \texttt{app.py}: The final webcam application launched by the user.
    \item \textbf{Rule of Authorship:} Absolutely zero lines of foreign code are present in this directory. All logic is authored by hand.
\end{itemize}

\textbf{2. vendor/ (Foreign Code)}
\begin{itemize}
    \item Contains any third party helper libraries, complex boilerplate configurations, snippets explicitly downloaded that was not written by hand. This completely isolates foreign code from the core application logic.
    \item \texttt{video\_extractor.py}: Custom script to extract frames from personal videos. Moved to vendor to separate data collection utilities from core application logic.
\end{itemize}

\textbf{3. data/}
\begin{itemize}
    \item \texttt{raw/}: Contains the unmodified downloaded images and video frames.
    \item \texttt{processed/}: Contains the cropped 128x128 faces and the \texttt{dataset.csv}.
\end{itemize}

\textbf{4. notebooks/}
\begin{itemize}
    \item \texttt{model\_training.ipynb}: The Jupyter Notebook executed in Google Colab documenting the CNN creation, training, and evaluation.
\end{itemize}

\textbf{5. models/}
\begin{itemize}
    \item \texttt{miro\_detector.keras}: The exported weights of the trained neural network.
\end{itemize}

\textbf{Deployment and Execution Instructions:}
To deploy the application on the target school computer without an IDE, the user must connect an external webcam and execute the following steps in the command line:
\begin{enumerate}
    \item \texttt{python -m venv venv}
    \item \texttt{venv\textbackslash Scripts\textbackslash activate}
    \item \texttt{pip install -r requirements.txt}
    \item \texttt{python main.py run} (Use \texttt{--video path.mp4} for video files)
\end{enumerate}

\end{document}
"""
    return latex_template


def build_pdf(filename="documentation"):
    """Writes the LaTeX code to a file and compiles it using pdflatex."""
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)

    generate_graphs()

    tex_filename = os.path.join(OUT_DIR, f"{filename}.tex")

    print(f"Generating {tex_filename}...")

    latex_content = generate_latex_content()
    with open(tex_filename, "w", encoding="utf-8") as f:
        f.write(latex_content)

    print("Compiling PDF with pdflatex...")

    try:
        # Run pdflatex with OUT_DIR as the working directory so it finds the images natively
        # Use -interaction=nonstopmode to prevent the process from hanging on errors or missing package prompts
        subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{filename}.tex"], cwd=OUT_DIR, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{filename}.tex"], cwd=OUT_DIR, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Move the final compiled PDF to the docs directory safely
        compiled_pdf = os.path.join(OUT_DIR, f"{filename}.pdf")
        if os.path.exists(FINAL_PDF_PATH):
            os.remove(FINAL_PDF_PATH)
        shutil.move(compiled_pdf, FINAL_PDF_PATH)

        print(f"Successfully generated PDF at {FINAL_PDF_PATH}")
    except subprocess.CalledProcessError:
        print(f"Error: Compilation of {filename}.tex failed.")
        log_file = os.path.join(OUT_DIR, f"{filename}.log")
        if os.path.exists(log_file):
            print(f"Checking {log_file} for errors...")
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                for line in lines[-20:]:  # Print last 20 lines of log
                    print(line.strip())
    except FileNotFoundError:
        print("Error: pdflatex command not found. Please ensure you have a LaTeX distribution installed.")
    except PermissionError:
        print(f"Error: Could not move {filename}.pdf to {DOCS_DIR}. Please ensure the file is NOT open in another application (like a PDF viewer) and try again.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    build_pdf()