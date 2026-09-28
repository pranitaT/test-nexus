const BACKEND_APP_ID = '5c9e575a-cf40-4a77-ae1a-56e9c172656e';
const APP_ID_STYLE = 'path';
 
function api(path, options = {}) {
    let target = path;
 
    if (BACKEND_APP_ID && BACKEND_APP_ID !== 'local') {
        target =
            APP_ID_STYLE === 'query'
                ? `${path}${path.includes('?') ? '&' : '?'}app_id=${encodeURIComponent(BACKEND_APP_ID)}`
                : `/${encodeURIComponent(BACKEND_APP_ID)}${path}`;
    }
 
    return fetch(target, {
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        },
        ...options
    }).then(async r => {
        const data = await r.json().catch(() => ({ error: r.statusText }));
 
        if (!r.ok) {
            throw new Error(data.error || `Request failed (${r.status})`);
        }
 
        return data;
    });
}
