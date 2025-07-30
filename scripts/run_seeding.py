#!/usr/bin/env python3
"""
Script to run the complete data seeding process for CarePlan AI.
This script generates sample healthcare data and prepares it for the web UI.
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from scripts.seed_data.database_seeder import DatabaseSeeder


async def main():
    """Main function to run the seeding process."""
    print("🏥 CarePlan AI Data Seeding Process")
    print("=" * 50)
    
    # Create seeder instance
    seeder = DatabaseSeeder()
    
    try:
        # Run the seeding process
        print("📊 Starting data generation...")
        sample_data = await seeder.run_seeding(num_patients=100)
        
        print("\n✅ Seeding completed successfully!")
        print(f"📁 Generated data files:")
        
        # List generated files
        data_dir = Path(__file__).parent / "seed_data"
        for file_path in data_dir.glob("*.csv"):
            file_size = file_path.stat().st_size / 1024  # KB
            print(f"   - {file_path.name} ({file_size:.1f} KB)")
        
        # Show sample data summary
        if sample_data:
            print(f"\n📋 Sample Data Summary:")
            print(f"   - Patients: {len(sample_data.get('patients', []))}")
            print(f"   - Intake Records: {len(sample_data.get('intakes', []))}")
            print(f"   - EHR Records: {len(sample_data.get('ehr_records', []))}")
            print(f"   - Care Plans: {len(sample_data.get('care_plans', []))}")
        
        print(f"\n🌐 To view the data in the web UI:")
        print(f"   1. Start the FastAPI backend:")
        print(f"      cd {project_root}")
        print(f"      uvicorn app.main:app --reload")
        print(f"   2. Start the React frontend:")
        print(f"      cd {project_root}/clients/web-ui")
        print(f"      npm install && npm start")
        print(f"   3. Open http://localhost:3000 in your browser")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)