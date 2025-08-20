import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import google.generativeai as genai
from google.generativeai import types
from mcp import ClientSession
from mcp.client.tcp import tcp_client
from typing import List, Dict
import datetime

# --- Configuration ---
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY environment variable not set.")
genai.configure(api_key=api_key)

MCP_TOOLS = {
    "puppeteer": 8001, "sequentialthinking": 8002, "memory": 8003,
    "docker": 8004, "sandbox": 8005, "time": 8006, "fetch": 8007,
    "duckduckgo": 8008, "desktop": 8009,
}
tool_sessions: Dict[str, ClientSession] = {}

# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to MCP tool servers...")
    for name, port in MCP_TOOLS.items():
        try:
            reader, writer = await asyncio.open_connection(name, port)
            session = ClientSession(reader, writer)
            await session.initialize()
            tool_sessions[name] = session
            print(f"Connected to MCP tool: {name}")
        except Exception as e:
            print(f"Failed to connect to MCP tool: {name}. Error: {e}")
    yield
    print("Closing MCP connections...")
    for session in tool_sessions.values():
        await session.close()

# --- Pydantic Models ---
class AgentRequest(BaseModel):
    prompt: str = Field(..., example="What is the capital of France?")

class AgentResponse(BaseModel):
    response: str = Field(..., example="The capital of France is Paris.")

class BatchRequest(BaseModel):
    prompts: List[str] = Field(..., min_items=1, max_items=100, example=["What is 2+2?", "Summarize 'Dune'"])

class BatchSubmissionResponse(BaseModel):
    job_name: str = Field(..., example="batches/123456789")
    status: str = Field(..., example="JOB_STATE_PENDING")

class BatchStatusResponse(BaseModel):
    job_name: str
    status: str
    results: List[Dict] | None = None

class CacheRequest(BaseModel):
    content: str = Field(..., description="Large text content to cache.")
    ttl_minutes: int = Field(60, description="Time-to-live for the cache in minutes.")

class CacheResponse(BaseModel):
    cache_name: str = Field(..., example="cachedContents/abc-123")

# --- FastAPI App ---
app = FastAPI(lifespan=lifespan, title="SheikhBox Multi-Tool AI Agent", version="3.0.0")

# --- Endpoints ---
@app.post("/agent", response_model=AgentResponse, summary="Interact with the agent in real-time")
async def agent_endpoint(request: AgentRequest):
    # ... (implementation from previous step)
    if not tool_sessions:
        raise HTTPException(status_code=503, detail="Agent is offline, no tools connected.")
    try:
        tools = list(tool_sessions.values())
        model_response = await genai.GenerativeModel('gemini-2.5-pro').generate_content_async(contents=request.prompt, tools=tools)
        return AgentResponse(response=model_response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/batch", response_model=BatchSubmissionResponse, summary="Submit prompts for asynchronous processing")
async def agent_batch_endpoint(request: BatchRequest):
    # ... (implementation from previous step)
    try:
        inline_requests = [{'contents': [{'parts': [{'text': prompt}]}]} for prompt in request.prompts]
        batch_job = genai.GenerativeModel('gemini-2.5-flash').batch_generate_content(requests=inline_requests)
        return BatchSubmissionResponse(job_name=batch_job.name, status=batch_job.state.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create batch job: {str(e)}")

@app.get("/agent/batch/{job_name}", response_model=BatchStatusResponse, summary="Check status and retrieve results of a batch job")
async def get_batch_status(job_name: str):
    # ... (implementation from previous step)
    try:
        if not job_name.startswith("batches/"):
            job_name = f"batches/{job_name}"
        batch_job = genai.get_batch_generate_content_job(name=job_name)
        results = None
        if batch_job.state.name == 'JOB_STATE_SUCCEEDED':
            results = [{"response": r.text if r else "No response"} for r in batch_job.responses]
        return BatchStatusResponse(job_name=batch_job.name, status=batch_job.state.name, results=results)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job not found or error: {str(e)}")

@app.post("/agent/cache", response_model=CacheResponse, summary="Create a context cache for repeated use")
async def create_cache(request: CacheRequest):
    try:
        ttl = datetime.timedelta(minutes=request.ttl_minutes)
        cache = genai.CachedContent.create(
            model="models/gemini-2.5-pro-001",
            contents=[request.content],
            ttl=ttl,
        )
        return CacheResponse(cache_name=cache.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create cache: {str(e)}")

@app.post("/agent/cached/{cache_name}", response_model=AgentResponse, summary="Interact with the agent using a context cache")
async def cached_agent_endpoint(cache_name: str, request: AgentRequest):
    if not cache_name.startswith("cachedContents/"):
        cache_name = f"cachedContents/{cache_name}"
    
    if not tool_sessions:
        raise HTTPException(status_code=503, detail="Agent is offline, no tools connected.")
        
    try:
        tools = list(tool_sessions.values())
        model = genai.GenerativeModel.from_cached_content(cached_content=genai.CachedContent(name=cache_name))
        model_response = await model.generate_content_async(contents=request.prompt, tools=tools)
        return AgentResponse(response=model_response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with cached session: {str(e)}")
