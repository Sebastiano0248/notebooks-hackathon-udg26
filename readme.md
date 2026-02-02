# Data Science Project Template

This repository contains the notebooks for the UdG Hackathon 2026. It is structured to facilitate data analysis, model development, and experimentation.

## 🛠 Setup and Installation

Follow these steps to set up your local development environment.

### 1. Prerequisites

Ensure you have **Python 3.13** installed. You can check your version by running:

```bash
python --version

```

### 2. Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies:

```bash
# Create the environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

```

### 3. Install Dependencies

Install the required data science libraries (Pandas, Scikit-Learn, etc.) using the `requirements.txt` file:

```bash
pip install --upgrade pip
pip install -r requirements.txt

```

---

## 🏗 Pre-commit Hooks

To maintain code quality and ensure your notebooks and scripts stay clean, we use `pre-commit`. This will automatically run checks (like linting and formatting) every time you attempt to `git commit`.

### 1. Install pre-commit

The `pre-commit` package is included in the requirements, but you must register it with your git hooks:

```bash
pre-commit install

```

### 2. Manual Run (Optional)

If you want to run the hooks against all files without committing, use:

```bash
pre-commit run --all-files

```

---

## 📂 Project Structure

* `data/`: Raw and processed data.
* `notebooks/`: Exploratory Data Analysis (EDA) and prototyping.
* `src/`: Source code for models and data pipelines.

---

## 🚀 Usage

To start the Jupyter interface and begin working on notebooks:

```bash
jupyter lab

```
