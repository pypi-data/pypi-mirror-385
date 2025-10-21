from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import base64
import httpx
import os
import json
from pathlib import Path
from huggingface_hub import InferenceClient, get_token, whoami


class TTSRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    text: str
    voice_id: str = "default"
    model_id: str = "coqui-tts"
    parameters: Dict[str, Any] = {}
    mode: str = "api"
    access_token: Optional[str] = None


class TTSResponse(BaseModel):
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    format: str = "wav"
    error: Optional[str] = None
    success: bool = True


app = FastAPI(title="HFStudio API", version="0.1.0")

static_dir = Path(__file__).parent / "static"
models_dir = Path(__file__).parent.parent / "models"


def load_model_spec(model_id: str) -> Optional[Dict[str, Any]]:
    """Load model specification from JSON file."""
    spec_path = models_dir / model_id / "spec.json"
    if spec_path.exists():
        try:
            with open(spec_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None


def generate_tts_with_client(
    client: InferenceClient, request: TTSRequest, model_spec: Dict[str, Any]
) -> TTSResponse:
    """Generate TTS using InferenceClient with model specifications."""
    try:
        # Build extra_body with parameters from spec
        extra_body = {}

        if request.parameters and "api" in model_spec:
            api_params = model_spec["api"].get("parameters", {})
            for param_name, param_value in request.parameters.items():
                if param_name in api_params:
                    extra_body[param_name] = param_value

        # Add voice URL from spec
        voice_urls = model_spec.get("api", {}).get("voice_urls", {})
        if request.voice_id.lower() in voice_urls:
            extra_body["audio_url"] = voice_urls[request.voice_id.lower()]

        # Generate audio
        audio_bytes = client.text_to_speech(
            request.text,
            extra_body=extra_body if extra_body else None,
        )

        # Convert to base64 data URL
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        audio_url = f"data:audio/wav;base64,{audio_base64}"

        # Estimate duration (simple heuristic)
        duration = len(request.text) * 0.05

        return TTSResponse(audio_url=audio_url, duration=duration, format="wav")
    except Exception as e:
        error_str = str(e)

        if "403 Forbidden" in error_str and "permissions" in error_str:
            return TTSResponse(
                success=False,
                error="Your HuggingFace token doesn't have permission to use Inference Providers. Please create a new token with 'Inference API' permissions at https://huggingface.co/settings/tokens",
            )
        elif "authentication" in error_str.lower():
            return TTSResponse(
                success=False,
                error="Authentication failed. Please check your HuggingFace token or log in again.",
            )
        else:
            return TTSResponse(
                success=False, error=f"TTS generation error: {error_str}"
            )


if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    app.mount("/_app", StaticFiles(directory=str(static_dir / "_app")), name="app")
    app.mount(
        "/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets"
    )
    app.mount(
        "/samples", StaticFiles(directory=str(static_dir / "samples")), name="samples"
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Voice(BaseModel):
    id: str
    name: str
    preview_url: Optional[str] = None
    supported_models: list[str] = []


class Model(BaseModel):
    id: str
    name: str
    type: str
    status: str


class OAuthTokenRequest(BaseModel):
    code: str


class OAuthTokenResponse(BaseModel):
    access_token: str
    token_type: str
    scope: str


@app.get("/")
async def root():
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    else:
        return {"message": "HFStudio API is running"}


@app.get("/api/status")
async def get_status():
    return {"mode": "api", "local_available": False, "api_configured": True}


@app.get("/api/auth/oauth-config")
async def get_oauth_config():
    scopes = os.getenv(
        "OAUTH_SCOPES", "read-repos write-repos manage-repos inference-api"
    )

    return {
        "client_id": os.getenv(
            "OAUTH_CLIENT_ID", "cdf32a17-e40f-4a84-b683-f66aa1105793"
        ),
        "scopes": scopes,
        "is_spaces": bool(os.getenv("SPACE_HOST")),
    }


@app.get("/api/auth/local-token")
async def get_local_token():
    try:
        if os.getenv("SPACE_HOST"):
            return {"available": False, "reason": "running_on_spaces"}

        token = get_token()
        if not token:
            return {"available": False, "reason": "no_local_token"}

        try:
            user_info = whoami(token=token)
            if user_info.get("type") != "user":
                return {"available": False, "reason": "invalid_token_type"}

            return {
                "available": True,
                "token": token,
                "user_info": {
                    "name": user_info.get("name"),
                    "fullname": user_info.get("fullname"),
                    "avatarUrl": user_info.get("avatarUrl"),
                },
            }
        except Exception as api_error:
            if "429" in str(api_error) or "rate limit" in str(api_error).lower():
                return {
                    "available": True,
                    "token": token,
                    "user_info": {
                        "name": "Local User",
                        "fullname": "Local User",
                        "avatarUrl": None,
                    },
                    "warning": "Token validation skipped due to rate limiting",
                }
            else:
                return {
                    "available": False,
                    "reason": f"token_validation_error: {str(api_error)}",
                }

    except Exception as e:
        return {"available": False, "reason": f"error: {str(e)}"}


@app.get("/api/voices")
async def get_voices():
    voices = []

    # Load voices from all model specifications
    for model_dir in models_dir.iterdir():
        if model_dir.is_dir():
            model_spec = load_model_spec(model_dir.name)
            if model_spec and "voices" in model_spec:
                for voice_spec in model_spec["voices"]:
                    voice = Voice(
                        id=voice_spec["id"],
                        name=voice_spec["name"],
                        preview_url=model_spec.get("api", {})
                        .get("voice_urls", {})
                        .get(voice_spec["id"]),
                        supported_models=[model_dir.name],
                    )
                    voices.append(voice)

    return {"voices": voices}


@app.get("/api/models")
async def get_models():
    models = []

    # Load models from specifications
    for model_dir in models_dir.iterdir():
        if model_dir.is_dir():
            model_spec = load_model_spec(model_dir.name)
            if model_spec:
                model_type = "api" if "api" in model_spec else "local"
                status = "available" if model_type == "api" else "downloadable"

                model = Model(
                    id=model_dir.name,
                    name=model_spec.get("name", model_dir.name),
                    type=model_type,
                    status=status,
                )
                models.append(model)

    return {"models": models}


@app.post("/api/tts/generate")
async def generate_tts(request: TTSRequest):
    try:
        # Load model specification
        model_spec = load_model_spec(request.model_id)
        if not model_spec:
            return TTSResponse(
                success=False,
                error=f"Model specification not found for {request.model_id}",
            )

        # Create client based on mode
        if request.mode == "api":
            if not request.access_token:
                return TTSResponse(
                    success=False, error="Please log in to HuggingFace to use the API."
                )

            # Get model endpoint from spec
            endpoint_model = model_spec.get("api", {}).get(
                "endpoint_model", request.model_id
            )
            client = InferenceClient(
                api_key=request.access_token,
                model=endpoint_model,
            )
        elif request.mode == "local":
            # Get local port from spec or use default
            local_config = model_spec.get("local", {})
            port = local_config.get("default_port", 7861)
            client = InferenceClient(base_url=f"http://localhost:{port}/api/v1")
        else:
            return TTSResponse(
                success=False, error="Invalid mode. Use 'api' or 'local'."
            )

        # Generate TTS using the unified helper function
        result = generate_tts_with_client(client, request, model_spec)

        # Add specific error handling for local mode
        if not result.success and request.mode == "local":
            result.error = f"Local server error: {result.error}. Make sure to run 'hfstudio start {request.model_id}' first."

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/token")
async def exchange_oauth_token(request: OAuthTokenRequest, http_request: Request):
    try:
        token_url = "https://huggingface.co/oauth/token"

        client_id = os.getenv("OAUTH_CLIENT_ID", "cdf32a17-e40f-4a84-b683-f66aa1105793")
        client_secret = os.getenv(
            "OAUTH_CLIENT_SECRET", "f590cb2d-6eac-4cef-a0cb-d0116825295c"
        )

        if os.getenv("SPACE_HOST"):
            space_host = os.getenv("SPACE_HOST").split(",")[0]
            redirect_uri = f"https://{space_host}/auth/callback"
        else:
            referer = http_request.headers.get("referer", "")
            if referer:
                from urllib.parse import urlparse

                parsed = urlparse(referer)
                redirect_uri = f"{parsed.scheme}://{parsed.netloc}/auth/callback"
            else:
                redirect_uri = "http://localhost:7860/auth/callback"

        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": request.code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url, data=token_data, headers={"Accept": "application/json"}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, detail=f"Token exchange failed: {response.text}"
                )

            token_response = response.json()

            return OAuthTokenResponse(
                access_token=token_response["access_token"],
                token_type=token_response.get("token_type", "Bearer"),
                scope=token_response.get("scope", ""),
            )

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/auth/callback")
async def oauth_callback(code: str = None, state: str = None, request: Request = None):
    if not code:
        return HTMLResponse(
            """
        <html>
            <head><title>OAuth Error</title></head>
            <body>
                <h1>OAuth Error</h1>
                <p>No authorization code received.</p>
                <script>window.close();</script>
            </body>
        </html>
        """,
            status_code=400,
        )

    try:
        token_url = "https://huggingface.co/oauth/token"

        client_id = os.getenv("OAUTH_CLIENT_ID", "cdf32a17-e40f-4a84-b683-f66aa1105793")
        client_secret = os.getenv(
            "OAUTH_CLIENT_SECRET", "f590cb2d-6eac-4cef-a0cb-d0116825295c"
        )

        if os.getenv("SPACE_HOST"):
            space_host = os.getenv("SPACE_HOST").split(",")[0]
            redirect_uri = f"https://{space_host}/auth/callback"
        else:
            redirect_uri = "http://localhost:7860/auth/callback"

        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url, data=token_data, headers={"Accept": "application/json"}
            )

            if response.status_code == 200:
                token_response = response.json()
                access_token = token_response["access_token"]

                return HTMLResponse(f"""
                <html>
                    <head><title>OAuth Success</title></head>
                    <body>
                        <h1>Sign in successful!</h1>
                        <p>Redirecting...</p>
                        <script>
                            localStorage.setItem('hf_access_token', '{access_token}');
                            window.location.href = '/';
                        </script>
                    </body>
                </html>
                """)
            else:
                return HTMLResponse(
                    f"""
                <html>
                    <head><title>OAuth Error</title></head>
                    <body>
                        <h1>OAuth Error</h1>
                        <p>Token exchange failed: {response.text}</p>
                        <a href="/">Return to app</a>
                    </body>
                </html>
                """,
                    status_code=400,
                )

    except Exception as e:
        return HTMLResponse(
            f"""
        <html>
            <head><title>OAuth Error</title></head>
            <body>
                <h1>OAuth Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/">Return to app</a>
            </body>
        </html>
        """,
            status_code=500,
        )


@app.get("/{path:path}")
async def serve_spa(path: str):
    if (
        path.startswith("api/")
        or path.startswith("docs")
        or path.startswith("openapi.json")
    ):
        raise HTTPException(status_code=404, detail="Not found")

    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    else:
        return HTMLResponse("""
        <html>
            <head><title>HFStudio</title></head>
            <body>
                <h1>HFStudio Backend</h1>
                <p>The backend is running, but the frontend hasn't been built yet.</p>
                <p>Visit <a href="/docs">/docs</a> for the API documentation.</p>
            </body>
        </html>
        """)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
