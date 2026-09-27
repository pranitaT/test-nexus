/*
  Centralized Gig Garage App-ID routing.
  Supplied participant text requires App ID on every network route,
  but does not specify exact URL syntax.

  Default:
      /<BACKEND_APP_ID>/api/...

  Change buildBackendUrl() only if the official deployment guide
  specifies a different route shape.
*/
window.APP_CONFIG = window.APP_CONFIG || {
  backendAppId: "",
  routeStyle: "prefix"
};

function buildBackendUrl(path) {
  const appId = window.APP_CONFIG.backendAppId;
  if (!appId || appId === "local") return path;

  if (window.APP_CONFIG.routeStyle === "query") {
    const join = path.includes("?") ? "&" : "?";
    return `${path}${join}appId=${encodeURIComponent(appId)}`;
  }

  return `/${encodeURIComponent(appId)}${path}`;
}

async function api(path, options = {}) {
  const response = await fetch(buildBackendUrl(path), {
    ...options,
    headers: {"Content-Type": "application/json", ...(options.headers || {})}
  });

  const text = await response.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; }
  catch (_) { data = {error: text}; }

  if (!response.ok) {
    throw new Error(data.error || data.detail || `Request failed: ${response.status}`);
  }
  return data;
}

window.api = api;
