import uvicorn
import os

if __name__ == "__main__":
    # Get configuration from environment or defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    print(f"Starting {os.getenv('PROJECT_NAME', 'StrategyOptimizer API')} on http://{host}:{port}")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload
    )
