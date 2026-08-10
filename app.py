"""Streamlit UI for the SOA Financial Reconciliation Pipeline."""

import streamlit as st
from pathlib import Path

# Import your bulletproof backend functions
from excel_ops import read_summary_report, update_soa_file, update_summary_report
from matcher import find_soa_file

# Configure the visual layout of the web page
st.set_page_config(page_title="SOA Reconciler", page_icon="📊", layout="centered")

st.title("📊 SOA Reconciliation Pipeline")
st.markdown("Automate weekly billing charges directly into partner SOA files and generate a processed summary report.")
st.divider()

# --- UI FORM ---
with st.form("pipeline_form"):
    st.subheader("Configuration")
    
    report_path_input = st.text_input(
        "Weekly Billing Sheet Path"
    )
    
    soa_dir_input = st.text_input(
        "Target SOA Directory Path"
    )
    
    col1, col2 = st.columns(2)
    start_date = col1.text_input("Billing Start Date", value="20-Jul-2026")
    end_date = col2.text_input("Billing End Date", value="26-Jul-2026")
    
    submitted = st.form_submit_button("Run Pipeline", type="primary")

# --- EXECUTION LOGIC ---
if submitted:
    # .strip(' "\'') removes any accidental spaces or quote marks you might have pasted
    clean_report_path = report_path_input.strip(' "\'')
    clean_soa_dir = soa_dir_input.strip(' "\'')
    
    report_path = Path(clean_report_path)
    soa_dir = Path(clean_soa_dir)
    
    # 1. Pre-flight Validation
    if not report_path.is_file():
        st.error(f"Cannot find the billing sheet at: {report_path}")
        st.info("💡 Tip: Ensure the file name matches exactly, and isn't named 'Report (1).xlsx' or 'Report.xlsx.xlsx'")
        st.stop()
        
    if not soa_dir.is_dir():
        st.error(f"Cannot find the SOA directory at: {soa_dir}")
        st.stop()
        
    # 2. Setup Live Log Window
    st.subheader("Run Cycle Logs")
    # ... (the rest of the code remains exactly the same below this)
        
    # 2. Setup Live Log Window
    st.subheader("Run Cycle Logs")
    log_window = st.empty()
    log_text = "Initializing run cycle...\n"
    log_window.code(log_text, language="text")
    
    def add_log(message: str):
        """Helper to append text to the on-screen terminal window."""
        global log_text
        log_text += f"{message}\n"
        log_window.code(log_text, language="text")

    # 3. Read Summary Report
    try:
        batch = read_summary_report(report_path)
        add_log(f"Successfully loaded {len(batch.records)} records from summary sheet.")
    except Exception as e:
        st.error(f"Error reading report: {e}")
        st.stop()

    match_count = 0
    success_count = 0
    status_updates = []

    # Visual progress bar
    progress_bar = st.progress(0)
    total_records = len(batch.records)
    
    # 4. Pipeline Execution
    for idx, record in enumerate(batch.records):
        add_log(f"\n[{idx+1}/{total_records}] Processing: {record.carrier_name} | ${record.amount}")
        
        target_soa = find_soa_file(record.carrier_name, soa_dir)
        
        if target_soa:
            match_count += 1
            try:
                update_soa_file(
                    soa_path=target_soa, 
                    charge=record, 
                    start_date=start_date, 
                    end_date=end_date
                )
                success_count += 1
                status_updates.append((record.source_row, record.carrier_name, record.amount, 1))
                add_log(f"  ✅ SUCCESS: Wrote to {target_soa.name}")
            except Exception as e:
                add_log(f"  ❌ WRITE ERROR: {e}")
                status_updates.append((record.source_row, record.carrier_name, record.amount, 0))
        else:
            add_log(f"  ❌ MATCH FAILED: No file found")
            status_updates.append((record.source_row, record.carrier_name, record.amount, 0))
            
        # Update the UI progress bar
        progress_bar.progress((idx + 1) / total_records)

    # 5. Finalize and Write Back
    add_log("\n========================================")
    add_log(f"Pipeline Complete.")
    add_log(f"Records Processed: {total_records}")
    add_log(f"Matches Found: {match_count}")
    add_log(f"Successful Writes: {success_count}")
    
    if status_updates:
        try:
            update_summary_report(report_path, status_updates)
            add_log("✅ Summary report duplicated and updated with status tracking.")
        except Exception as e:
            add_log(f"❌ Failed to update summary report: {e}")
            
    st.success("Run cycle finished successfully! Check the new PROCESSED summary file.")