pub mod cors;
pub mod rate_limit;
pub mod auth;

use actix_web::HttpResponse;
use ahash::AHashMap;
use pyo3::prelude::*;
use std::collections::HashMap;

/// Process middleware metadata and return early response if needed
pub async fn process_middleware(
    method: &str,
    _path: &str,
    headers: &AHashMap<String, String>,
    peer_addr: Option<&str>,
    handler_id: usize,
    metadata: &Py<PyAny>,
    global_cors_origins: Option<&[String]>,
) -> Option<HttpResponse> {
    // Check for OPTIONS preflight
    if method == "OPTIONS" {
        return Python::attach(|py| {
            if let Ok(meta) = metadata.extract::<HashMap<String, Py<PyAny>>>(py) {
                if let Some(middleware_list) = meta.get("middleware") {
                    // Check if CORS is enabled
                    if let Ok(middlewares) = middleware_list.extract::<Vec<HashMap<String, Py<PyAny>>>>(py) {
                        for mw in middlewares {
                            if let Some(mw_type) = mw.get("type") {
                                if let Ok(type_str) = mw_type.extract::<String>(py) {
                                    if type_str == "cors" {
                                        return Some(cors::handle_preflight(&mw, global_cors_origins, py));
                                    }
                                }
                            }
                        }
                    }
                }
            }
            None
        })
    }
    
    // Process other middleware (rate limiting only - auth is now handled via guards)
    Python::attach(|py| {
        if let Ok(meta) = metadata.extract::<HashMap<String, Py<PyAny>>>(py) {
            if let Some(middleware_list) = meta.get("middleware") {
                if let Ok(middlewares) = middleware_list.extract::<Vec<HashMap<String, Py<PyAny>>>>(py) {
                    for mw in middlewares {
                        if let Some(mw_type) = mw.get("type") {
                            if let Ok(type_str) = mw_type.extract::<String>(py) {
                                match type_str.as_str() {
                                    "rate_limit" => {
                                        if let Some(response) = rate_limit::check_rate_limit(handler_id, headers, peer_addr, &mw, py) {
                                            return Some(response);
                                        }
                                    }
                                    _ => {}
                                }
                            }
                        }
                    }
                }
            }
        }
        None
    })
}

/// Add CORS headers to response if needed
pub fn add_cors_headers(
    response: &mut HttpResponse,
    origin: Option<&str>,
    metadata: &Py<PyAny>,
    global_cors_origins: Option<&[String]>,
) {
    Python::attach(|py| {
        if let Ok(meta) = metadata.extract::<HashMap<String, Py<PyAny>>>(py) {
            if let Some(middleware_list) = meta.get("middleware") {
                if let Ok(middlewares) = middleware_list.extract::<Vec<HashMap<String, Py<PyAny>>>>(py) {
                    for mw in middlewares {
                        if let Some(mw_type) = mw.get("type") {
                            if let Ok(type_str) = mw_type.extract::<String>(py) {
                                if type_str == "cors" {
                                    cors::add_cors_headers_to_response(response, origin, &mw, global_cors_origins, py);
                                    break;
                                }
                            }
                        }
                    }
                }
            }
        }
    });
}