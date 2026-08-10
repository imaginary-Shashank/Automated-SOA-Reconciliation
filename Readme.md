# Automated SOA Financial Reconciliation Pipeline

An industrial-grade Python application that automates the weekly financial reconciliation of telecom termination charges across fragmented Excel ledgers (Statements of Account). 

This pipeline replaces manual, error-prone data entry with a deterministic, strict validation backend and a frictionless Streamlit web interface.

# The Business Problem
Financial teams often handle billing reports that must be mapped to hundreds of individual partner Excel files. Doing this manually leads to:
* **High Error Rates:** Copy pasting data across hundreds of rows introduces human error.
* **Corrupted Ledgers:** Opening and modifying complex Excel templates can accidentally overwrite historical formulas and linked Power Queries.
* **Operational Drag:** A task that takes a human hours to complete should take a machine seconds.

# The Solution
This tool ingests a weekly billing sheet, strictly validates the financial data, and deterministically matches each charge to the correct partner's SOA file. 

* Key Features:
* Strict Data Validation: Utilizes `pydantic` schemas to ensure all incoming data (currencies, names, statuses) is perfectly typed before it ever touches a target file.
* Formula Preservation: Uses native Excel manipulation (via `openpyxl`) to inject new rows of data into existing templates *without* stripping or breaking the underlying `.xlsx` formulas.
* Self-Documenting: The pipeline automatically duplicates the source summary report and writes back the success/failure status of every single transaction.
* Frictionless UI: Wrapped in a `streamlit` desktop-ready interface so non-technical operations teams can execute the pipeline via a simple web form.

# Tech Stack
* **Language:** Python 3.11+
* **Frontend:** Streamlit
* **Data Validation:** Pydantic
* **Excel Processing:** Openpyxl
* **Packaging:** PyInstaller (for standalone Windows `.exe` distribution)

# How to Run Locally

# 1. Clone the Repository
git clone [https://github.com/imaginary-Shashank/Automated-SOA-Reconciliation.git](https://github.com/imaginary-Shashank/Automated-SOA-Reconciliation.git)
cd Automated-SOA-Reconciliation

# 2. Install Dependencies
pip install streamlit openpyxl pydantic

# 3. Launch the Application
streamlit run app.py

Architecture Flow
App.py: Streamlit orchestrator receives the target directory and billing period.
Excel_ops.py (Reader): Extracts the raw summary data and yields it to the validator.
Schemas.py: TerminationCharge model drops any row with malformed financial data.
Matcher.py: Deterministically links the company name to the correct local & Aiwo SOA.xlsx file.
Excel_ops.py (Writer): Safely opens the target ledger, locates the first empty billing row, injects the float amount, and saves. Updates the original summary report with a 1 (Done) or 0 (Failed).


**Author: Shashank Shekhar**