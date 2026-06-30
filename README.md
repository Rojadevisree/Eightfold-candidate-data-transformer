# Eightfold Candidate Data Transformer

A configurable, multi-source candidate data transformation pipeline built in Python for the Eightfold Engineering Intern Assignment.

The pipeline ingests candidate information from heterogeneous sources, normalizes and merges duplicate records into a single canonical profile, tracks provenance, assigns confidence scores, and produces configurable JSON outputs.

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/Rojadevisree/Eightfold-candidate-data-transformer.git
```
```bash
cd Eightfold-candidate-data-transformer
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
**PowerShell (VS Code default)**
```powershell
.\venv\Scripts\Activate.ps1
```

**Command Prompt (cmd)**
```cmd
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Pipeline
```bash
cd src
```
```bash
python pipeline.py --inputs "..\sample_inputs\recruiter_export.csv" --config "..\sample_inputs\config_default.json" --out "..\sample_inputs\output_default.json"
```

### 5. Run the tests
From the project root:
```bash
cd..
```
```bash
pytest tests/test_pipeline.py
```