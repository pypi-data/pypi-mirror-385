from fastapi import FastAPI, HTTPException, Request as FastAPIRequest
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import fastapi
from typing import TYPE_CHECKING, Optional, Union
import threading
from Hql.Helpers import can_thread
from Hql.Exceptions import HqlExceptions as hqle
import json
from pydantic import BaseModel
from pathlib import Path
import logging

if TYPE_CHECKING:
    from Hql.Hac.Engine import HacEngine

class HqlRequest(BaseModel):
    hql: str
    run: bool = True
    save: bool = False
    plan: bool = False

class Apiserver():
    def __init__(self, hacengine:'HacEngine', host='127.0.0.1', port=8081):
        if not can_thread():
            raise hqle.CompilerException('Cannot start the api server as free threading is not supported, use the container?')

        self.hacengine = hacengine
        self.app = FastAPI()
        self.host = host
        self.port = port
        self.thread = None

        # Add CORS middleware for development
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Serve static frontend files
        # Try container path first, then development path
        static_dir = Path("/opt/Hql/Hql-Interface/dist")
        if not static_dir.exists():
            static_dir = Path(__file__).parent.parent.parent / "Hql-Interface" / "dist"

        if static_dir.exists() and (static_dir / "assets").exists():
            self.app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

        @self.app.get("/")
        def read_root():
            # Serve index.html if it exists, otherwise return API info
            index_file = static_dir / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            return {"I'm serving a": "youthful porpoise 🐬"}

        # API endpoints
        @self.app.get('/api/detections/{detection_id}/history')
        def get_detection_history(detection_id:str):
            if detection_id not in self.hacengine.detections:
                raise HTTPException(status_code=404, detail=f'Detection {detection_id} not found')
            return self.hacengine.detections[detection_id].run_history

        @self.app.get('/api/detections')
        def get_detections():
            detections = []
            for i in self.hacengine.detections:
                det = self.hacengine.detections[i]
                if not det.hac:
                    continue
                detections.append(det.hac.asm)
            return detections
        
        @self.app.get('/api/detections/{detection_id}')
        def get_detections(detection_id:str):
            detection = self.hacengine.detections[detection_id]
            return detection.to_dict()

        @self.app.post('/api/detections')
        async def save_detection(request: fastapi.Request):
            query_body = await request.body()
            query_text = query_body.decode('utf-8')

            if not query_text.strip():
                raise HTTPException(status_code=400, detail='Query body cannot be empty')

            try:
                detection = self.hacengine.write_detection(query_text)

                # Reload detections
                self.hacengine.files = self.hacengine.scan_files()
                self.hacengine.detections = self.hacengine.load_files()

                return {'id': detection.id}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f'Failed to save detection: {str(e)}')

        @self.app.get('/api/schema')
        def get_schema():
            # Return available fields from data sources
            # This is a simplified version - could be enhanced to introspect actual data sources
            schema = []

            # Get schema from config if available
            if hasattr(self.hacengine.config, 'schema') and self.hacengine.config.schema:
                for field_name, field_type in self.hacengine.config.schema.items():
                    schema.append({
                        'name': field_name,
                        'type': str(field_type) if hasattr(field_type, '__name__') else str(type(field_type).__name__)
                    })

            return schema

        @self.app.get('/api/hql/runs/{tid}')
        def get_run_by_id(tid:str):
            run = self.hacengine.get_by_id(tid)
            if run == None:
                raise HTTPException(status_code=404, detail=f'Run {tid} not found')
            return run.to_dict()

        @self.app.get('/api/hql/runs')
        def get_runs():
            return self.hacengine.get_runs()

        @self.app.post('/api/hql/runs')
        def submit_hql_query(hql:HqlRequest):
            from Hql.Hac.Engine import Detection
            if not hql.run:
                return {'id': ''}

            det = Detection(hql.hql, 'api', self.hacengine.config, no_hac=True)
            rid = self.hacengine.run_detection(det)
            return {'id': rid}

        def reparse_hql(hql:HqlRequest):
            from Hql.Hac.Engine import Detection

            det = Detection(hql.hql, 'api', self.hacengine.config)
            deparsed = det.deparse()

            return {
                'hql': deparsed
            }

        def add_hac(hql:HqlRequest):
            from Hql.Hac.Engine import Detection, Hac

            det = Detection(hql.hql, 'api', self.hacengine.config)
            if not det.hac:
                det.hac = Hac({}, 'api')


    def start(self):
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        logging.info(f'Starting api server on http://{self.host}:{self.port}')
        uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")

    def join(self):
        if self.thread:
            self.thread.join()
