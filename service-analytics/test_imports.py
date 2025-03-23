"""
Simple script to test if all imports are working correctly.
"""

import sys
import os
import traceback

# Add the project directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

print("Testing imports...")

try:
    print("Importing importers module...")
    # Import local modules
    from src.data_processing.importers import (
        load_type6_report, load_sales_journal, load_gps_tracking
    )
    print("✓ Importers module imported successfully")
    
    print("Importing integrator module...")
    from src.data_processing.integrator import (
        map_tech_codes_to_devices, match_jobs_to_gps_stops, merge_sales_with_jobs, add_alert_data_to_techs
    )
    print("✓ Integrator module imported successfully")
    
    print("Importing classifier module...")
    from src.analysis.classifier import classify_all_jobs
    print("✓ Classifier module imported successfully")
    
    # This was the failing import originally
    print("Testing the problematic import from text_mining...")
    from src.analysis.text_mining import extract_cancellation_reasons_from_df, extract_time_on_job
    print("✓ Text_mining module imported successfully")
    
    # Let's verify that the specific imports from cancel_categories work
    print("Importing CANCEL_CATEGORIES and CATEGORY_PRIORITY...")
    from config.cancel_categories import CANCEL_CATEGORIES, CATEGORY_PRIORITY
    print(f"✓ CANCEL_CATEGORIES has {len(CANCEL_CATEGORIES)} categories")
    print(f"✓ CATEGORY_PRIORITY has {len(CATEGORY_PRIORITY)} items")
    
    print("Importing metrics module...")
    from src.analysis.metrics import (
        calculate_tech_revenue_metrics, calculate_performance_metrics, 
        calculate_cancellation_metrics, calculate_alert_scores, analyze_idle_time
    )
    print("✓ Metrics module imported successfully")

    # Import visualization modules
    print("Importing dashboard visualization module...")
    import src.visualization.dashboard as dashboard_viz
    print("✓ Dashboard visualization module imported successfully")
    
    # Test imports from config to make sure they work
    print("Importing SERVICE_CALL_PRICES...")
    from config.settings import SERVICE_CALL_PRICES
    print("✓ Service call prices imported successfully")
    
    print("Importing ALERT_WEIGHTS and DRIVING_SCORE_THRESHOLDS...")
    from config.alert_weights import ALERT_WEIGHTS, DRIVING_SCORE_THRESHOLDS
    print("✓ Alert weights imported successfully")
    
    print("\nAll imports successful!")
except Exception as e:
    print(f"Error importing modules: {str(e)}")
    print("\nDetailed traceback:")
    print(traceback.format_exc()) 