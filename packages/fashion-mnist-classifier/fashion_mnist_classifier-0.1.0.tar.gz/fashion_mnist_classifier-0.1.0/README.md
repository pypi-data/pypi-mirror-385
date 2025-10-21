## Description

This project implements an image classification model based on the Fashion MNIST dataset, using PyTorch Lightning to structure the code in a modular and scalable way.
The dataset is loaded directly from `torchvision.datasets`. The goal is to train a simple convolutional network that classifies images into 10 different clothing categories.

## Project Structure

```
fashion-mnist-classifier/
├── models/               # Directorio para modelos y checkpoints guardados
├── reports/              # Informes de evaluación y figuras generadas
├── src/
│   └── my_project/       # Código fuente del proyecto
│       ├── __init__.py
│       ├── config.py     # Configuraciones y parámetros
│       ├── dataset.py    # Dataset y DataModule
│       ├── model.py      # Modelo de PyTorch Lightning
│       ├── plots.py      # Funciones de visualización
│       └── train.py      # Script principal de entrenamiento
├── .gitignore
├── LICENSE               # Licencia del proyecto
├── pyproject.toml        # Metadatos y dependencias del proyecto
└── README.md             # Este archivo
```

## Installation
To install dependencies and prepare the environment with uv, run the following commands in the terminal:
1. Download and install dependencies: curl -sSf https://uv.io/install.sh | sh
2. Initialize the environment: uv init
3. Sync dependencies and environment: uv sync

## Training and Evaluation
To run the training and evaluation script, first install the package in editable mode:

```bash
uv pip install -e .
```

Then, run the following command in the terminal:

```bash
fashion-mnist-classifier
```

## Building and Publishing to PyPI
To build and publish the package to PyPI, follow these steps:

1.  **Install build tools:**
    ```bash
    uv pip install build twine
    ```
2.  **Build the package:**
    ```bash
    python -m build
    ```
3.  **Publish to PyPI:**
    ```bash
    twine upload dist/*
    ```
    You will be prompted for your PyPI username and password.


## Technical Details
-Dataset: `torchvision.datasets.FashionMNIST` with custom transformations.
-Model: Simple CNN with one convolutional layer, pooling, and fully connected layers.
-Training: Implemented with PyTorch Lightning to facilitate handling epochs, performance, and metrics.
-Configuration: Parameters such as batch size, paths, epochs defined in config.py.
-Optimization: Adam with CrossEntropyLoss.

## Reports & Visualizations
The project includes detailed reports and visualizations:
- **Confusion matrix**
- **Per-class accuracy**
- **Calibration curve**
- **Misclassified image grids**
- **Pixel distribution analysis**

All outputs are stored in the `reports/` folder.

## Contact
-delrey.132148@e.unavarra.es
-goicoechea.128710@e.unavarra.es
-haddad.179806@e.unavarra.es
