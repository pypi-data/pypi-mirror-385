from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

app = FastAPI(
    title="JSHunter Web Scanner",
    description="Web interface for JSHunter High-Performance JavaScript security scanner",
    version="2.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="jshunter/web/static"), name="static")

# Templates
templates = Jinja2Templates(directory="jshunter/web/templates")

# Store results by IP (in memory for demo, use proper database in production)
scan_results = {}

# Helper functions for the enhanced jshunter
def run_jshunter_scan(url: str, discord_webhook: Optional[str] = None) -> List[Dict]:
    """Run jshunter scan on a URL and return results."""
    try:
        # Use the enhanced jshunter CLI with proper output handling
        cmd = ["jshunter", "-u", url, "-o", f"/tmp/web_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"]
        if discord_webhook:
            cmd.extend(["--discord-webhook", discord_webhook])
            
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"JSHunter scan failed: {result.stderr}")
            return []
        
        # Parse results from JSON output file
        findings = []
        output_file = cmd[4]  # The -o parameter
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            finding = json.loads(line.strip())
                            findings.append({
                                "detector": finding.get("DetectorName", "Unknown"),
                                "verified": finding.get("Verified", False),
                                "raw": finding.get("Raw", "")[:50] + "..." if finding.get("Raw") else "",
                                "redacted": finding.get("Redacted", ""),
                                "source_url": finding.get("source_url", url),
                                "line": finding.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("line")
                            })
                # Cleanup
                os.remove(output_file)
            except Exception as e:
                print(f"Error parsing results: {e}")
        
        return findings
    except Exception as e:
        print(f"Error running jshunter: {e}")
        return []

def run_jshunter_file_scan(file_path: str, discord_webhook: Optional[str] = None) -> List[Dict]:
    """Run jshunter scan on a local file and return results."""
    try:
        # Create a temporary URL file
        temp_url_file = f"/tmp/url_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(temp_url_file, 'w') as f:
            f.write(f"file://{file_path}")
        
        output_file = f"/tmp/web_file_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        cmd = ["jshunter", "-f", temp_url_file, "-o", output_file]
        if discord_webhook:
            cmd.extend(["--discord-webhook", discord_webhook])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Cleanup temp URL file
        if os.path.exists(temp_url_file):
            os.remove(temp_url_file)
        
        if result.returncode != 0:
            print(f"JSHunter file scan failed: {result.stderr}")
            return []
        
        # Parse results from JSON output file
        findings = []
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            finding = json.loads(line.strip())
                            findings.append({
                                "detector": finding.get("DetectorName", "Unknown"),
                                "verified": finding.get("Verified", False),
                                "raw": finding.get("Raw", "")[:50] + "..." if finding.get("Raw") else "",
                                "redacted": finding.get("Redacted", ""),
                                "source_url": finding.get("source_url", f"file://{file_path}"),
                                "line": finding.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("line")
                            })
                # Cleanup
                os.remove(output_file)
            except Exception as e:
                print(f"Error parsing file scan results: {e}")
        
        return findings
    except Exception as e:
        print(f"Error running jshunter on file: {e}")
        return []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/scan/file")
async def scan_file(request: Request, file: UploadFile = File(...), discord_webhook: str = Form(None)):
    client_ip = request.client.host
    
    # Create temporary directory for the file
    temp_dir = Path("temp") / datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = temp_dir / file.filename
    
    try:
        # Save uploaded file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Run scan using enhanced jshunter with Discord webhook support
        results = run_jshunter_file_scan(str(file_path), discord_webhook)
        
        # Store results for this IP
        if client_ip not in scan_results:
            scan_results[client_ip] = []
        scan_results[client_ip].append({
            "timestamp": datetime.now().isoformat(),
            "filename": file.filename,
            "results": results,
            "discord_webhook_used": bool(discord_webhook)
        })
        
        return JSONResponse(content={
            "results": results,
            "discord_webhook_used": bool(discord_webhook),
            "verified_count": len([r for r in results if r.get("verified", False)]),
            "unverified_count": len([r for r in results if not r.get("verified", False)])
        })
        
    finally:
        # Cleanup
        if file_path.exists():
            file_path.unlink()
        if temp_dir.exists():
            temp_dir.rmdir()

@app.post("/scan/url")
async def scan_url(request: Request, url: str = Form(...), discord_webhook: str = Form(None)):
    client_ip = request.client.host
    
    # Create temporary directory
    temp_dir = Path("temp") / datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run scan using enhanced jshunter with Discord webhook support
        results = run_jshunter_scan(url, discord_webhook)
        
        # Store results for this IP
        if client_ip not in scan_results:
            scan_results[client_ip] = []
        scan_results[client_ip].append({
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "results": results,
            "discord_webhook_used": bool(discord_webhook)
        })
        
        return JSONResponse(content={
            "results": results,
            "discord_webhook_used": bool(discord_webhook),
            "verified_count": len([r for r in results if r.get("verified", False)]),
            "unverified_count": len([r for r in results if not r.get("verified", False)])
        })
        
    finally:
        # Cleanup
        if temp_dir.exists():
            for file in temp_dir.glob("*"):
                file.unlink()
            temp_dir.rmdir()

@app.get("/results")
async def get_results(request: Request):
    client_ip = request.client.host
    return JSONResponse(content={
        "results": scan_results.get(client_ip, [])
    })

def main():
    uvicorn.run(
        "jshunter.web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()
