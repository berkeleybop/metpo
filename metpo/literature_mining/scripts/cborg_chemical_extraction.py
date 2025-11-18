#!/usr/bin/env python3
"""
CBORG Chemical Utilization Extraction with Cost and Performance Tracking

This script runs chemical utilization extraction using CBORG's OpenAI/GPT-5 endpoint,
tracking execution time and API costs before and after the run.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv

def load_cborg_key():
    """Load CBORG API key from root .env file"""
    # Point to repository root .env file
    env_path = Path(__file__).parent.parent.parent / ".env"

    if not env_path.exists():
        print(f"ERROR: Environment file not found at {env_path}")
        print("Please create .env file in repository root with:")
        print("CBORG_API_KEY=sk-your-key-here")
        print("You can copy .env.template to .env and fill in your key.")
        sys.exit(1)

    load_dotenv(env_path)
    cborg_key = os.getenv("CBORG_API_KEY")

    if not cborg_key:
        print("ERROR: CBORG_API_KEY not found in .env")
        print("Please add CBORG_API_KEY=sk-your-key-here to your .env file")
        sys.exit(1)

    return cborg_key

def get_cborg_usage(api_key):
    """Get current CBORG usage/cost information"""
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get("https://api.cborg.lbl.gov/key/info", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"WARNING: Could not fetch CBORG usage: {e}")
        return None

def run_extraction(api_key):
    """Run the chemical utilization extraction with timing and logging"""
    
    # Set environment variable for OntoGPT
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = api_key
    
    # Generate timestamped output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"outputs/chemical_utilization_cborg_gpt5_{timestamp}.yaml"
    log_file = f"logs/ontogpt_verbose_{timestamp}.log"
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Build OntoGPT command
    cmd = [
        "uv", "run", "ontogpt", "-vv", "extract",
        "-t", "templates/chemical_utilization_populated.yaml",
        "-i", "test-chemical-rich/",
        "-m", "openai/gpt-5",
        "--model-provider", "openai",
        "--api-base", os.environ.get("CBORG_API_BASE", "https://api.cborg.lbl.gov"),
        "-o", output_file
    ]
    
    print("="*60)
    print("CBORG Chemical Utilization Extraction")
    print("="*60)
    print(f"Model: openai/gpt-5")
    print(f"Template: chemical_utilization_populated.yaml")
    print(f"Input: test-chemical-rich/")
    print(f"Output: {output_file}")
    print(f"Verbose log: {log_file}")
    print(f"Timestamp: {timestamp}")
    print("="*60)
    
    # Record start time
    start_time = time.time()
    start_timestamp = datetime.now().isoformat()
    
    print(f"Starting extraction at {start_timestamp}")
    print("Command:", " ".join(cmd))
    print("-"*60)
    
    # Run extraction with logging
    try:
        with open(log_file, "w") as logf:
            # Write header to log file
            logf.write(f"OntoGPT Verbose Log - {start_timestamp}\n")
            logf.write(f"Command: {' '.join(cmd)}\n")
            logf.write("="*60 + "\n\n")
            logf.flush()
            
            # Run with stdout/stderr captured to log file
            result = subprocess.run(cmd, env=env, check=True, 
                                  stdout=logf, stderr=subprocess.STDOUT)
        
        execution_time = time.time() - start_time
        
        print("-"*60)
        print(f"✅ Extraction completed successfully")
        print(f"⏱️  Execution time: {execution_time:.2f} seconds")
        print(f"📁 Output file: {output_file}")
        print(f"📋 Verbose log: {log_file}")
        
        return {
            "success": True,
            "output_file": output_file,
            "log_file": log_file,
            "execution_time": execution_time,
            "start_time": start_timestamp,
            "end_time": datetime.now().isoformat(),
            "command": " ".join(cmd)
        }
        
    except subprocess.CalledProcessError as e:
        execution_time = time.time() - start_time
        print(f"❌ Extraction failed after {execution_time:.2f} seconds")
        print(f"Error code: {e.returncode}")
        print(f"📋 Error log: {log_file}")
        
        return {
            "success": False,
            "execution_time": execution_time,
            "error_code": e.returncode,
            "log_file": log_file,
            "start_time": start_timestamp,
            "end_time": datetime.now().isoformat()
        }

def run_assessment(output_file):
    """Run quality assessment on the extraction output"""
    if not Path(output_file).exists():
        print(f"WARNING: Output file {output_file} not found, skipping assessment")
        return None
    
    print("\n" + "="*60)
    print("Running Quality Assessment")
    print("="*60)
    
    try:
        # Run assessment on outputs directory with pattern matching the specific file
        output_path = Path(output_file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        assessment_output = f"logs/unified_assessment_{timestamp}.yaml"
        
        cmd = [
            "uv", "run", "python", "metpo_assessor.py", 
            "analyze-extractions", "outputs/", 
            "--pattern", output_path.name,
            "--output", assessment_output
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Assessment file is what we specified
        print(f"✅ Assessment completed")
        print(f"📊 Assessment file: {assessment_output}")
        
        return {
            "success": True,
            "assessment_file": assessment_output,
            "output": result.stdout
        }
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Assessment failed: {e}")
        print(f"Error output: {e.stderr}")
        return {
            "success": False,
            "error": str(e),
            "stderr": e.stderr
        }

def main():
    print("CBORG Chemical Utilization Extraction with Performance Tracking")
    print("================================================================")
    
    # Load API key
    print("📋 Loading CBORG API key from local/.env...")
    api_key = load_cborg_key()
    print("✅ API key loaded successfully")
    
    # Get initial usage
    print("\n📊 Fetching initial CBORG usage...")
    initial_usage = get_cborg_usage(api_key)
    if initial_usage:
        print("✅ Initial usage retrieved")
        print(f"   Usage data: {json.dumps(initial_usage, indent=2)}")
    
    # Run extraction
    extraction_result = run_extraction(api_key)
    
    # Get final usage
    print("\n📊 Fetching final CBORG usage...")
    final_usage = get_cborg_usage(api_key)
    if final_usage:
        print("✅ Final usage retrieved")
        print(f"   Usage data: {json.dumps(final_usage, indent=2)}")
    
    # Calculate cost difference
    if initial_usage and final_usage:
        print("\n💰 Cost Analysis:")
        # This will depend on what fields CBORG returns in their usage API
        # We'll need to see the actual response structure
        print("   (Cost calculation will be implemented based on CBORG API response structure)")
    
    # Run assessment if extraction succeeded
    assessment_result = None
    if extraction_result["success"]:
        assessment_result = run_assessment(extraction_result["output_file"])
    
    # Generate summary report
    print("\n" + "="*60)
    print("EXECUTION SUMMARY")
    print("="*60)
    print(f"Status: {'✅ SUCCESS' if extraction_result['success'] else '❌ FAILED'}")
    print(f"Execution time: {extraction_result['execution_time']:.2f} seconds")
    print(f"Start time: {extraction_result['start_time']}")
    print(f"End time: {extraction_result['end_time']}")
    
    if extraction_result["success"]:
        print(f"Output file: {extraction_result['output_file']}")
        if assessment_result and assessment_result["success"]:
            print(f"Assessment: {assessment_result['assessment_file']}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"logs/cborg_extraction_results_{timestamp}.json"
    
    Path("logs").mkdir(exist_ok=True)
    
    results = {
        "timestamp": timestamp,
        "model": "openai/gpt-5",
        "provider": "cborg",
        "template": "chemical_utilization",
        "input_dir": "test-chemical-rich/",
        "initial_usage": initial_usage,
        "final_usage": final_usage,
        "extraction": extraction_result,
        "assessment": assessment_result
    }
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    print("="*60)

if __name__ == "__main__":
    main()