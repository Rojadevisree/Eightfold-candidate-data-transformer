# Eightfold Candidate Data Transformer

A configurable, multi-source candidate data transformation pipeline built in Python for the Eightfold Engineering Intern Assignment.

The pipeline ingests candidate information from heterogeneous sources, normalizes and merges duplicate records into a single canonical profile, tracks provenance, assigns confidence scores, and produces configurable JSON outputs.

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/<Rojadevisree>/Eightfold-candidate-data-transformer.git
cd Eightfold-candidate-data-transformer
```

### 2. Create and activate a virtual environment
**Windows (PowerShell)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the pipeline
```bash
cd src
python pipeline.py
```

### 5. Run the tests
From the project root:
```bash
pytest
```
or
```bash
pytest tests/test_pipeline.py
```