import sys
import os
from mcp.server.fastmcp import FastMCP  # Import FastMCP, the quickstart server base
mcp = FastMCP("Strava")  # Initialize an MCP server instance with a descriptive name
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import requests
import urllib.parse
import json
from typing import Any, Dict

TOKEN_STORE_FILENAME = "strava_mcp_tokens.json"

def _get_token_store_path() -> str:
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, TOKEN_STORE_FILENAME)

def _save_tokens_to_disk(tokens: Dict[str, Any]) -> dict:
    try:
        path = _get_token_store_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tokens, f)
        return {"ok": True, "path": path}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def _load_tokens_from_disk() -> dict:
    try:
        path = _get_token_store_path()
        if not os.path.exists(path):
            return {"ok": False, "error": "token store not found", "path": path}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"ok": True, "tokens": data, "path": path}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool("strava://auth/url")
async def get_auth_url(client_id: int | None = None):
    """Return the Strava OAuth authorization URL. If client_id is not provided,
    read it from the STRAVA_CLIENT_ID environment variable."""
    if client_id is None:
        client_id_env = os.getenv("STRAVA_CLIENT_ID")
        if not client_id_env:
            return {"error": "STRAVA_CLIENT_ID environment variable is not set"}
        try:
            client_id = int(client_id_env)
        except ValueError:
            return {"error": "STRAVA_CLIENT_ID must be an integer"}

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": "https://developers.strava.com/oauth2-redirect/",
        "approval_prompt": "force",
        "scope": "read,activity:read_all",
    }
    # Always return whole URL and not part of it
    return "https://www.strava.com/oauth/authorize?" + urllib.parse.urlencode(params)

@mcp.tool("strava://auth/refresh")
async def refresh_access_token(
    
    refresh_token: str,
    client_id: int | None = None,
    client_secret: str | None = None,
) -> dict:
    """Refresh an access token using a refresh token."""
    if not refresh_token:
        return {"error": "refresh token is required"}
    
    if client_id is None:
        client_id_env = os.getenv("STRAVA_CLIENT_ID")
        if not client_id_env:
            return {"error": "STRAVA_CLIENT_ID environment variable is not set"}
        try:
            client_id = int(client_id_env)
        except ValueError:
            return {"error": "STRAVA_CLIENT_ID must be an integer"}

    if client_secret is None:
        client_secret_env = os.getenv("STRAVA_CLIENT_SECRET")
        if not client_secret_env:
            return {"error": "STRAVA_CLIENT_SECRET environment variable is not set"}
        try:
            client_secret = str(client_secret_env)
        except ValueError:
            return {"error": "STRAVA_CLIENT_SECRET must be a string"}

    resp = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )
    
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return {"error": "token refresh failed", "status_code": resp.status_code, "response": resp.text}
    except Exception as e:
        return {"error": "token refresh failed", "status_code": resp.status_code, "response": resp.text, "error": str(e)}

    tokens = resp.json()
    print(tokens)  # Print tokens for debugging (optional)
    
    return {
        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
        "expires_at": tokens.get("expires_at"),
        "expires_in": tokens.get("expires_in")
    }

@mcp.tool("strava://athlete/stats")
async def get_athlete_stats(
    code: str,
    client_id: int | None = None,
    client_secret: str | None = None,
    after: int | None = None,
    before: int | None = None,
    page: int | None = None,
    per_page: int | None = None,
) -> dict:
    """Exchange an authorization code for access + refresh tokens and get athlete activities with optional filters.
    
    Args:
        code: Authorization code from Strava OAuth
        client_id: Strava client ID
        client_secret: Strava client secret
        after: An epoch timestamp to use for filtering activities that have taken place after a certain time
        before: An epoch timestamp to use for filtering activities that have taken place before a certain time
        page: The page of activities (default=1)
        per_page: How many activities per page (default=30)
    """
    if not code:
        return {"error": "authorization code is required"}

    if client_id is None:
        client_id_env = os.getenv("STRAVA_CLIENT_ID")
        if not client_id_env:
            return {"error": "STRAVA_CLIENT_ID environment variable is not set"}
        try:
            client_id = int(client_id_env)
        except ValueError:
            return {"error": "STRAVA_CLIENT_ID must be an integer"}

    if client_secret is None:
        client_secret_env = os.getenv("STRAVA_CLIENT_SECRET")
        if not client_secret_env:
            return {"error": "STRAVA_CLIENT_SECRET environment variable is not set"}
        try:
            client_secret = str(client_secret_env)
        except ValueError:
            return {"error": "STRAVA_CLIENT_SECRET must be a string"}

    resp = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
        },
    )
    
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return {"error": "token request failed", "status_code": resp.status_code, "response": resp.text}
    except Exception as e:
        return {"error": "token request failed", "status_code": resp.status_code, "response": resp.text, "error": str(e)}

    tokens = resp.json()
    # Print tokens for debugging (optional)
    print(tokens)

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    
    # Persist tokens for later refresh usage via the public save tool
    save_result = await save_tokens({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": tokens.get("expires_at"),
        "expires_in": tokens.get("expires_in"),
        "athlete": tokens.get("athlete"),
        "token_type": tokens.get("token_type"),
        "scope": tokens.get("scope"),
    })

    # return {"tokens": tokens, "access_token": access_token, "refresh_token": refresh_token}

    # Build URL with query parameters
    params = []
    if after is not None:
        params.append(f"after={after}")
    if before is not None:
        params.append(f"before={before}")
    if page is not None:
        params.append(f"page={page}")
    if per_page is not None:
        params.append(f"per_page={per_page}")
    
    # Default per_page to 30 if not specified (Strava API default)
    if per_page is None:
        params.append("per_page=30")
    
    query_string = "&".join(params) if params else ""
    url = f"https://www.strava.com/api/v3/athlete/activities?{query_string}"
    
    # Debug output
    print(f"DEBUG: Requesting URL: {url}")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    activities_data = response.json()
    print(f"DEBUG: Response status: {response.status_code}, Activities count: {len(activities_data) if isinstance(activities_data, list) else 0}")
    
    return {
        "activities": activities_data,
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": tokens.get("expires_at"),
            "expires_in": tokens.get("expires_in"),
        },
        "save": save_result
    }

@mcp.tool("strava://athlete/stats-with-token")
async def get_athlete_stats_with_token(
    access_token: str,
    after: int | None = None,
    before: int | None = None,
    page: int | None = None,
    per_page: int | None = None
) -> dict:
    """Get athlete activities using an existing access token with optional filters.
    
    Args:
        access_token: Strava access token
        after: An epoch timestamp to use for filtering activities that have taken place after a certain time
        before: An epoch timestamp to use for filtering activities that have taken place before a certain time
        page: The page of activities (default=1)
        per_page: How many activities per page (default=30)
    """
    if not access_token:
        return {"error": "access token is required"}
    
    # Build URL with query parameters
    params = []
    if after is not None:
        params.append(f"after={after}")
    if before is not None:
        params.append(f"before={before}")
    if page is not None:
        params.append(f"page={page}")
    if per_page is not None:
        params.append(f"per_page={per_page}")
    
    # Default per_page to 30 if not specified (Strava API default)
    if per_page is None:
        params.append("per_page=30")
    
    query_string = "&".join(params) if params else ""
    url = f"https://www.strava.com/api/v3/athlete/activities?{query_string}"
    
    # Debug output
    print(f"DEBUG: Requesting URL: {url}")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    
    try:
        response.raise_for_status()
    except requests.HTTPError:
        return {"error": "API request failed", "status_code": response.status_code, "response": response.text}
    except Exception as e:
        return {"error": "API request failed", "status_code": response.status_code, "response": response.text, "error": str(e)}

    activities_data = response.json()
    print(f"DEBUG: Response status: {response.status_code}, Activities count: {len(activities_data) if isinstance(activities_data, list) else 0}")
    return {
        "activities": activities_data,
        "count": len(activities_data) if isinstance(activities_data, list) else 0,
        "status": "success"
    }

@mcp.tool("strava://auth/save")
async def save_tokens(tokens: dict | None = None) -> dict:
    """Save tokens to local disk at ~/.strava_mcp_tokens.json. If tokens is not provided, no-op with error."""
    if not tokens or not isinstance(tokens, dict):
        return {"error": "tokens dict is required"}
    result = _save_tokens_to_disk(tokens)
    if not result.get("ok"):
        return {"error": "failed to save tokens", **result}
    return {"ok": True, "path": result.get("path")}


@mcp.tool("strava://auth/load")
async def load_tokens() -> dict:
    """Load tokens from local disk at ~/.strava_mcp_tokens.json"""
    result = _load_tokens_from_disk()
    if not result.get("ok"):
        return {"error": result.get("error"), "path": result.get("path")}
    return {"ok": True, "tokens": result.get("tokens"), "path": result.get("path")}

@mcp.tool("strava://athlete/refresh-and-stats")
async def refresh_and_get_stats(
    client_id: int | None = None, 
    client_secret: str | None = None,
    after: int | None = None,
    before: int | None = None,
    page: int | None = None,
    per_page: int | None = None
) -> dict:
    """Load saved refresh token, refresh access token, save it, then fetch activities with optional filters.
    
    Args:
        client_id: Strava client ID
        client_secret: Strava client secret
        after: An epoch timestamp to use for filtering activities that have taken place after a certain time
        before: An epoch timestamp to use for filtering activities that have taken place before a certain time
        page: The page of activities (default=1)
        per_page: How many activities per page (default=30)
    """
    load_result = await load_tokens()
    if not load_result.get("ok"):
        return {"error": "no saved tokens", "details": load_result}
    saved = load_result.get("tokens", {})
    refresh_token = saved.get("refresh_token")
    if not refresh_token:
        return {"error": "refresh_token not found in saved tokens"}

    refreshed = await refresh_access_token(refresh_token=refresh_token, client_id=client_id, client_secret=client_secret)
    if "error" in refreshed:
        return {"error": "refresh failed", "details": refreshed}

    # Save refreshed tokens
    await save_tokens(refreshed)

    access_token = refreshed.get("access_token")
    if not access_token:
        return {"error": "no access_token after refresh"}

    # Fetch activities with new token and filters
    activities = await get_athlete_stats_with_token(
        access_token=access_token,
        after=after,
        before=before,
        page=page,
        per_page=per_page
    )
    return {"activities": activities, "tokens": refreshed}

@mcp.tool("strava://session/start")
async def start_session(
    client_id: int | None = None, 
    client_secret: str | None = None,
    after: int | None = None,
    before: int | None = None,
    page: int | None = None,
    per_page: int | None = None
) -> dict:
    """Start a session: if a refresh token exists, refresh and fetch; otherwise return auth URL.
    
    Args:
        client_id: Strava client ID
        client_secret: Strava client secret
        after: An epoch timestamp to use for filtering activities that have taken place after a certain time
        before: An epoch timestamp to use for filtering activities that have taken place before a certain time
        page: The page of activities (default=1)
        per_page: How many activities per page (default=30)
    """
    token_path = _get_token_store_path()
    if os.path.exists(token_path):
        loaded = _load_tokens_from_disk()
        if loaded.get("ok"):
            saved = loaded.get("tokens", {})
            refresh_token = saved.get("refresh_token")
            if isinstance(refresh_token, str) and refresh_token.strip():
                result = await refresh_and_get_stats(
                    client_id=client_id, 
                    client_secret=client_secret,
                    after=after,
                    before=before,
                    page=page,
                    per_page=per_page
                )
                return {**result, "used_token_file": token_path}
    # Fall back to auth URL flow
    else:
        url = await get_auth_url(client_id=client_id)
        return {"auth_url": url, "token_file_checked": token_path}

#@mcp.prompt
#def greet_user_prompt(question: str) -> str:
    #"""Generates a message orchestrating mcp tools"""
    #return f"""
    #Return a message for a user called '{question}'. 
    #if the user is asking, use a formal style, else use a street style.
    #"""

if __name__ == "__main__":
    mcp.run(transport="stdio")  # Run the server, using standard input/output for communication