import time
import requests
import logging
from typing import Any, Dict, Optional
from .exceptions import MondayAPIError


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# def monday_request(
#     query: str,
#     api_key: str,
#     max_retries: int = 5,
#     retry_delay: int = 3,
# ) -> Dict[str, Any]:
#     """
#     Ejecuta una petición GraphQL a Monday.com con:
#       - Reintentos ante fallos HTTP graves o ComplexityException
#       - Error inmediato ante errores GraphQL no retriables
#     """
#     api_url = "https://api.monday.com/v2"
#     headers = {
#         "Authorization": api_key,
#         "API-Version": "2025-07",
#         "Content-Type": "application/json",
#     }
#     payload = {"query": query}

#     for attempt in range(1, max_retries + 1):
        
#         logger.debug("[Intento %d/%d] Query:\n%s", attempt, max_retries, query)
#         try:
#             r = requests.post(api_url, json=payload, headers=headers, timeout=10)
#             logger.debug("Status=%d Body=%s", r.status_code, r.text)
            
            
#             # --- NUEVO: reintentar si nos da 403 Forbidden ---
#             if r.status_code == 403:
#                 logger.warning("HTTP 403 Forbidden (intento %d/%d). Reintentando tras %ds",
#                                attempt, max_retries, retry_delay)
#                 time.sleep(retry_delay)
#                 continue
            

#             # Reintentar ante HTTP 5xx
#             if 500 <= r.status_code < 600:
#                 logger.warning("HTTP %d — retry %d/%d", r.status_code, attempt, max_retries)
#                 time.sleep(retry_delay)
#                 continue

#             # Parseo JSON
#             try:
#                 resp = r.json()
#             except ValueError as e:
#                 logger.error("Respuesta no JSON. retry %d/%d", attempt, max_retries)
#                 time.sleep(retry_delay)
#                 continue

#             # Si hay errores GraphQL:
#             if "errors" in resp:
#                 errs = resp["errors"]
#                 code = resp.get("error_code") or errs[0].get("extensions", {}).get("code")
#                 # ComplexityException → reintentar
#                 if code in ("ComplexityException", "COMPLEXITY_BUDGET_EXHAUSTED"):
#                     wait_secs = 10
#                     try:
#                         wait_secs = (
#                             int(errs[0].get("extensions", {}).get("retry_in_seconds"))  # para COMPLEXITY_BUDGET_EXHAUSTED
#                             or int(errs[0]["message"].split()[-2]) + 1  # fallback por si es ComplexityException clásico
#                         )
#                     except Exception:
#                         pass
#                     logger.info("%s — waiting %ds", code, wait_secs)
#                     time.sleep(wait_secs)
#                     continue
#                 # Cualquier otro error GraphQL → levantar YA
#                 logger.error("GraphQL error no retriable: %s", errs)
#                 raise MondayAPIError(errs)

#             # Éxito
#             return resp

#         except requests.RequestException as e:
#             logger.warning("RequestException: %s — retry %d/%d", e, attempt, max_retries)
#             time.sleep(retry_delay)

#     # Si agotamos reintentos de HTTP/Complexity
#     raise MondayAPIError([{"message": "Max retries reached"}])



def monday_request(
    query: str,
    api_key: str,
    max_retries: int = 5,
    retry_delay: int = 3,
    retry_on_unauth_notfound: bool = True,
    max_unauth_notfound_retries: int = 2,
) -> Dict[str, Any]:
    """
    Ejecuta una petición GraphQL contra Monday (POST /v2) con reintentos inteligentes.

    Reintenta por defecto: 5xx, 403, 429, y errores GraphQL de complejidad.
    Opcionalmente reintenta 401/404 (útil si ves fallos transitorios por propagación).
    """
    import json, random, time, re
    import requests

    api_url = "https://api.monday.com/v2"
    headers = {
        "Authorization": api_key,
        "API-Version": "2025-07",
        "Content-Type": "application/json",
    }
    payload = {"query": query}

    def _sleep_with_backoff(attempt: int, base_delay: float, hint_seconds: float | None = None) -> None:
        if hint_seconds is not None and hint_seconds > 0:
            time.sleep(hint_seconds); return
        base = base_delay * (2 ** (attempt - 1))
        jitter = base * (0.3 * (2 * random.random() - 1))
        time.sleep(max(0.0, base + jitter))

    unauth_notfound_tries = 0

    for attempt in range(1, max_retries + 1):
        try:
            t0 = time.time()
            r = requests.post(api_url, json=payload, headers=headers, timeout=15)
            dt = (time.time() - t0) * 1000

            req_id = r.headers.get("X-Request-Id")
            rl_remaining = r.headers.get("X-RateLimit-Remaining")
            logger.debug("Monday request_id=%s status=%d time=%.1fms remain=%s",
                         req_id, r.status_code, dt, rl_remaining)

            # 429 Too Many Requests
            if r.status_code == 429:
                retry_after = r.headers.get("Retry-After")
                wait_secs = None
                try:
                    if retry_after is not None:
                        wait_secs = float(retry_after)
                except ValueError:
                    pass
                logger.warning("HTTP 429 — retry %d/%d (wait=%s)", attempt, max_retries, wait_secs)
                if attempt < max_retries:
                    _sleep_with_backoff(attempt, retry_delay, hint_seconds=wait_secs)
                    continue
                raise MondayAPIError([{"message": "HTTP 429 Too Many Requests"}])

            # 401/404 — reintentos acotados (opt-in)
            if r.status_code in (401, 404) and retry_on_unauth_notfound:
                unauth_notfound_tries += 1
                # Heurística: si la respuesta sugiere token inválido definitivo, no reintentes.
                body = r.text[:500]
                fatal_token = any(
                    s in body.lower()
                    for s in ("invalid token", "invalid api key", "unauthorized client")
                )
                if fatal_token:
                    logger.error("HTTP %d (fatal auth) — %s", r.status_code, body)
                    raise MondayAPIError([{"message": f"HTTP {r.status_code}", "body": body}])

                if unauth_notfound_tries <= max_unauth_notfound_retries and attempt < max_retries:
                    logger.warning("HTTP %d — transient? retry %d/%d (sub-unauth %d/%d)",
                                   r.status_code, attempt, max_retries,
                                   unauth_notfound_tries, max_unauth_notfound_retries)
                    # backoff más corto para 401/404
                    _sleep_with_backoff(unauth_notfound_tries, max(1, retry_delay // 2))
                    continue
                # Agotado presupuesto especial → fallar
                logger.error("HTTP %d — agotado presupuesto de reintentos 401/404", r.status_code)
                raise MondayAPIError([{"message": f"HTTP {r.status_code}", "body": r.text}])

            # 403 — a veces transitorio (WAF/permiso en propagación)
            if r.status_code == 403:
                logger.warning("HTTP 403 — retry %d/%d", attempt, max_retries)
                if attempt < max_retries:
                    _sleep_with_backoff(attempt, retry_delay)
                    continue
                raise MondayAPIError([{"message": "HTTP 403 Forbidden", "body": r.text}])

            # 5xx — transitorio
            if 500 <= r.status_code < 600:
                logger.warning("HTTP %d — retry %d/%d", r.status_code, attempt, max_retries)
                if attempt < max_retries:
                    _sleep_with_backoff(attempt, retry_delay)
                    continue
                raise MondayAPIError([{"message": f"HTTP {r.status_code}"}])

            # Parseo JSON
            try:
                resp = r.json()
            except ValueError:
                logger.error("Respuesta no JSON. status=%d body=%s", r.status_code, r.text[:500])
                if attempt < max_retries:
                    _sleep_with_backoff(attempt, retry_delay)
                    continue
                raise MondayAPIError([{"message": "Respuesta no JSON"}])

            # Errores GraphQL
            if resp.get("errors"):
                errs = resp["errors"]
                first = errs[0] or {}
                ext = first.get("extensions") or {}
                code = ext.get("code")
                path = ".".join(map(str, (first.get("path") or []))) or None

                # Complejidad/presupuesto → reintento
                if code in ("ComplexityException", "COMPLEXITY_BUDGET_EXHAUSTED"):
                    wait_secs = None
                    if "retry_in_seconds" in ext:
                        try: wait_secs = float(ext["retry_in_seconds"])
                        except Exception: pass
                    if wait_secs is None:
                        msg = first.get("message") or ""
                        m = re.findall(r"(\d+(?:\.\d+)?)\s*seconds?", msg)
                        if m:
                            try: wait_secs = float(m[-1])
                            except Exception: pass

                    logger.info("%s path=%s — waiting %ss (retry %d/%d)",
                                code, path, wait_secs, attempt, max_retries)
                    if attempt < max_retries:
                        _sleep_with_backoff(attempt, retry_delay, hint_seconds=wait_secs)
                        continue

                # Otros errores GraphQL → falla
                detail = {
                    "message": first.get("message") or "GraphQL error",
                    "code": code,
                    "path": path,
                    "request_id": req_id,
                }
                logger.error("GraphQL error: %s", detail)
                raise MondayAPIError([detail])

            return resp

        except requests.RequestException as e:
            logger.warning("RequestException: %s — retry %d/%d", e, attempt, max_retries)
            if attempt < max_retries:
                _sleep_with_backoff(attempt, retry_delay)
                continue
            raise MondayAPIError([{"message": f"RequestException: {e!s}"}])

    raise MondayAPIError([{"message": "Max retries reached"}])
