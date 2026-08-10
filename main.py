"""Main orchestrator for the SOA financial reconciliation pipeline."""

import logging
from pathlib import Path

from excel_ops import read_summary_report, update_soa_file, update_summary_report
from matcher import find_soa_file

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
REPORT_FILE_PATH = "/Users/sus_/Desktop/aiwo_project/406_Termination Report 20JUL2026 to 26JUL2026.xlsx" 
SOA_DIRECTORY_PATH = "Target_SOAs" 
BILLING_START_DATE = "20-Jul-2026"
BILLING_END_DATE = "26-Jul-2026"
# ---------------------

def main():
    current_dir = Path(__file__).parent
    
    report_path = Path(REPORT_FILE_PATH)
    if not report_path.is_absolute():
        report_path = current_dir / REPORT_FILE_PATH
        
    soa_dir = Path(SOA_DIRECTORY_PATH)
    if not soa_dir.is_absolute():
        soa_dir = current_dir / SOA_DIRECTORY_PATH

    if not soa_dir.is_dir():
        logger.error(f"SOA directory not found at: {soa_dir}")
        return

    logger.info("Starting reconciliation pipeline...")
    
    try:
        batch = read_summary_report(report_path)
    except FileNotFoundError as e:
        logger.error(e)
        return

    match_count = 0
    success_count = 0
    
    # Store updates as: (row_index, company_name, amount, status_code)
    # 1 = Success, 0 = Failure
    status_updates = []
    
    for record in batch.records:
        print("-" * 60)
        logger.info(f"Processing: {record.carrier_name} | Amount: ${record.amount}")
        
        target_soa = find_soa_file(record.carrier_name, soa_dir)
        
        if target_soa:
            match_count += 1
            try:
                update_soa_file(
                    soa_path=target_soa, 
                    charge=record, 
                    start_date=BILLING_START_DATE, 
                    end_date=BILLING_END_DATE
                )
                success_count += 1
                
                # Code 1: Successful write
                status_updates.append((record.source_row, record.carrier_name, record.amount, 1)) 
                
            except Exception as e:
                logger.error(f"❌ Failed to write to {target_soa.name}. Error: {e}")
                # Code 0: Failed during write
                status_updates.append((record.source_row, record.carrier_name, record.amount, 0))
        else:
            logger.warning(f"❌ No matching SOA file found for {record.carrier_name}")
            # Code 0: Failed to find file
            status_updates.append((record.source_row, record.carrier_name, record.amount, 0))
             
    print("=" * 60)
    logger.info(f"Pipeline Complete.")
    logger.info(f"Records Processed: {len(batch.records)}")
    logger.info(f"Matches Found: {match_count}")
    logger.info(f"Successful Writes: {success_count}")
    print("=" * 60)
    
    if status_updates:
        update_summary_report(report_path, status_updates)

if __name__ == "__main__":
    main()