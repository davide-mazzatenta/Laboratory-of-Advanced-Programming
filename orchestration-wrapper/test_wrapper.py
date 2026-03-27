#!/usr/bin/env python3
# test_wrapper.py
#
# Smoke test per "orchestration-wrapper": health, OpenAPI discovery e chiamate minime.
# Requisiti: requests (pip install requests)

import os
import sys
import time
import json
import argparse
from typing import Any, Dict, List, Optional, Tuple
import requests

DEFAULT_BASE_URL = os.getenv("WRAPPER_BASE_URL", "http://localhost:8010")

# Alcuni endpoint comuni da provare se OpenAPI non è disponibile
FALLBACK_ENDPOINTS = [
    ("GET", "/health", None),
    ("GET", "/version", None),
    ("GET", "/readyz", None),
    ("GET", "/livez", None),
    ("GET", "/metrics", None),
    ("POST", "/orchestrate", {"query": "Test rapido orchestrazione, rispondi con una frase."}),
    ("POST", "/generate", {"prompt": "Scrivi 'hello'."}),
    ("POST", "/search", {"query": "docker compose"}),
]

HEADERS_JSON = {"accept": "application/json", "content-type": "application/json"}

def wait_for_health(base_url: str, path: str = "/health", timeout_s: int = 90) -> None:
    print(f"⏳ Attendo health su {base_url}{path} (timeout {timeout_s}s)...")
    deadline = time.time() + timeout_s
    last_err = None
    while time.time() < deadline:
        try:
            r = requests.get(base_url + path, timeout=5)
            if r.ok:
                print(f"✅ Health OK ({r.status_code})")
                return
            last_err = f"HTTP {r.status_code}"
        except Exception as e:
            last_err = str(e)
        time.sleep(2)
    raise RuntimeError(f"Health non OK su {base_url}{path}: {last_err}")

def fetch_openapi(base_url: str, timeout_s: int = 10) -> Optional[Dict[str, Any]]:
    # FastAPI di solito espone /openapi.json; alcuni setup usano /_/openapi.json
    for path in ("/openapi.json", "/_/openapi.json"):
        url = base_url + path
        try:
            r = requests.get(url, headers={"accept": "application/json"}, timeout=timeout_s)
            if r.ok and r.headers.get("content-type", "").startswith("application/json"):
                print(f"📜 OpenAPI trovato su {path}")
                return r.json()
        except Exception:
            pass
    print("ℹ️ OpenAPI non disponibile (procedo con fallback).")
    return None

def resolve_ref(schema: Dict[str, Any], ref: str) -> Optional[Dict[str, Any]]:
    # Supporta $ref: "#/components/schemas/Name"
    if not ref.startswith("#/"):
        return None
    parts = ref.lstrip("#/").split("/")
    node: Any = schema
    for p in parts:
        if isinstance(node, dict) and p in node:
            node = node[p]
        else:
            return None
    return node if isinstance(node, dict) else None

def synth_value_from_schema(root_schema: Dict[str, Any], schema: Dict[str, Any], depth: int = 0) -> Any:
    """Costruisce un valore minimo per il tipo indicato dallo schema (best effort)."""
    if depth > 5:
        return None
    if not schema:
        return None

    if "$ref" in schema:
        target = resolve_ref(root_schema, schema["$ref"])
        if target:
            return synth_value_from_schema(root_schema, target, depth + 1)

    # Gestione oneOf/anyOf minimale: prendi il primo
    for k in ("oneOf", "anyOf", "allOf"):
        if k in schema and isinstance(schema[k], list) and schema[k]:
            return synth_value_from_schema(root_schema, schema[k][0], depth + 1)

    t = schema.get("type")
    if t == "string" or (not t and schema.get("format") in ("date-time", "uuid", "email")):
        fmt = schema.get("format")
        if fmt == "date-time":
            return "2025-01-01T00:00:00Z"
        if fmt == "uuid":
            return "00000000-0000-4000-8000-000000000000"
        if fmt == "email":
            return "test@example.com"
        # esempio per campi noti
        name = (schema.get("title") or "").lower()
        if "query" in name or "question" in name:
            return "Test: che ore sono?"
        if "prompt" in name or "text" in name or "content" in name:
            return "Scrivi una frase di prova."
        return "test"

    if t == "integer":
        return 1
    if t == "number":
        return 1.0
    if t == "boolean":
        return True
    if t == "array":
        item_schema = schema.get("items", {})
        return [synth_value_from_schema(root_schema, item_schema, depth + 1)]
    if t == "object" or "properties" in schema:
        out = {}
        props: Dict[str, Any] = schema.get("properties", {})
        required = schema.get("required", list(props.keys()))
        for k in required:
            sub = props.get(k, {})
            out[k] = synth_value_from_schema(root_schema, sub, depth + 1)
        # anche opzionali (solo se pochi)
        for k, sub in list(props.items())[:5]:
            if k not in out:
                out[k] = synth_value_from_schema(root_schema, sub, depth + 1)
        return out

    # default
    return "test"

def build_min_body_for_operation(openapi: Dict[str, Any], op: Dict[str, Any]) -> Optional[Tuple[Dict[str, Any], str]]:
    """Ritorna (payload, content_type) se possibile."""
    rb = op.get("requestBody")
    if not rb:
        return None
    content: Dict[str, Any] = rb.get("content") or {}
    # preferisci JSON
    for ctype in ("application/json", "application/*+json"):
        if ctype in content:
            schema = content[ctype].get("schema") or {}
            payload = synth_value_from_schema(openapi, schema)
            return payload, ctype
    # multipart/form-data non lo gestiamo qui
    return None

def synth_query_params(op: Dict[str, Any]) -> Dict[str, str]:
    out = {}
    for p in op.get("parameters", []) or []:
        if p.get("in") == "query" and p.get("required"):
            schema = p.get("schema") or {}
            t = schema.get("type")
            if t in (None, "string"):
                out[p["name"]] = "test"
            elif t == "integer":
                out[p["name"]] = "1"
            elif t == "number":
                out[p["name"]] = "1.0"
            elif t == "boolean":
                out[p["name"]] = "true"
    return out

def test_endpoint(base_url: str, method: str, path: str, op: Optional[Dict[str, Any]], timeout: int, verbose: bool) -> Tuple[bool, str]:
    url = base_url + path
    if "{" in path and "}" in path:
        return False, "skip path params"

    try:
        if method == "get":
            params = synth_query_params(op or {})
            r = requests.get(url, params=params, headers={"accept":"application/json"}, timeout=timeout)
        elif method == "post":
            payload_ct = build_min_body_for_operation(openapi, op) if op else None  # type: ignore[name-defined]
            if payload_ct:
                payload, ctype = payload_ct
                r = requests.post(url, headers={"accept":"application/json","content-type":ctype}, json=payload, timeout=timeout)
            else:
                # Prova senza body
                r = requests.post(url, headers=HEADERS_JSON, timeout=timeout)
        else:
            return False, "skip method"
    except Exception as e:
        return False, f"EXC {e}"

    ok = r.status_code < 400
    if verbose:
        print(f"→ {method.upper()} {path} -> {r.status_code}")
        snippet = r.text[:300].replace("\n"," ")
        print(f"   body: {snippet}{'…' if len(r.text)>300 else ''}")
    return ok, f"HTTP {r.status_code}"

def run_openapi_tests(base_url: str, openapi: Dict[str, Any], max_endpoints: int, timeout: int, verbose: bool) -> List[Tuple[str, bool, str]]:
    results = []
    tested = 0
    paths: Dict[str, Any] = openapi.get("paths", {})
    # Priorità: GET health-like, poi POST orchestrate-like, poi il resto
    def priority(item):
        path, methods = item
        score = 0
        if "health" in path: score -= 50
        if "ready" in path or "live" in path: score -= 40
        if "orchestr" in path: score -= 30
        if "generate" in path: score -= 20
        if "search" in path: score -= 10
        return score
    for path, methods in sorted(paths.items(), key=priority):
        if tested >= max_endpoints: break
        for method, op in methods.items():
            if method.lower() not in ("get","post"):
                continue
            ok, msg = test_endpoint(base_url, method.lower(), path, op, timeout, verbose)
            results.append((f"{method.upper()} {path}", ok, msg))
            tested += 1
            if tested >= max_endpoints: break
    return results

def run_fallback_tests(base_url: str, timeout: int, verbose: bool) -> List[Tuple[str, bool, str]]:
    rs = []
    for method, path, body in FALLBACK_ENDPOINTS:
        url = base_url + path
        try:
            if method == "GET":
                r = requests.get(url, headers={"accept":"application/json"}, timeout=timeout)
            else:
                r = requests.post(url, headers=HEADERS_JSON, json=body, timeout=timeout)
            ok = r.status_code < 400
            if verbose:
                print(f"→ {method} {path} -> {r.status_code}")
                print((r.text[:300] + ("…" if len(r.text)>300 else "")).replace("\n"," "))
            rs.append((f"{method} {path}", ok, f"HTTP {r.status_code}"))
        except Exception as e:
            rs.append((f"{method} {path}", False, f"EXC {e}"))
    return rs

def summarize(results: List[Tuple[str, bool, str]]) -> int:
    passed = sum(1 for _,ok,_ in results if ok)
    total = len(results)
    print("\n============== RISULTATI ==============")
    for name, ok, msg in results:
        print(f"{'✅' if ok else '❌'} {name}: {msg}")
    print(f"---------------------------------------")
    print(f"Totale: {passed}/{total} OK")
    return 0 if passed == total and total > 0 else 1

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Smoke-test per orchestration-wrapper")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL del wrapper (default: %(default)s)")
    ap.add_argument("--timeout", type=int, default=20, help="timeout per richiesta HTTP (s)")
    ap.add_argument("--max-endpoints", type=int, default=12, help="max endpoint da testare via OpenAPI")
    ap.add_argument("--verbose", action="store_true", help="log risposta endpoint")
    args = ap.parse_args()

    try:
        wait_for_health(args.base_url, "/health", timeout_s=max(10, args.timeout))
    except Exception as e:
        print(f"⚠️ Health check fallito: {e}")

    openapi = fetch_openapi(args.base_url, timeout_s=10)
    results: List[Tuple[str, bool, str]] = []
    if openapi:
        results.extend(run_openapi_tests(args.base_url, openapi, args.max_endpoints, args.timeout, args.verbose))
    else:
        results.extend(run_fallback_tests(args.base_url, args.timeout, args.verbose))

    sys.exit(summarize(results))
