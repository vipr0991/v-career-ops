const fs = require('fs');
const path = 'c:/Users/ASUS/Downloads/Career-Ops/career-ops/dashboard-web/src/App.jsx';
let code = fs.readFileSync(path, 'utf8');

const fetchWithRetryCode = `
async function fetchWithRetry(url, options = {}, retries = 3) {
  const response = await fetch(url, options);
  if (response.status === 503 && retries > 0) {
    const delay = Math.pow(2, 4 - retries) * 1000;
    await new Promise(res => setTimeout(res, delay));
    return fetchWithRetry(url, options, retries - 1);
  }
  return response;
}
`;

code = code.replace("const API_BASE = 'http://localhost:5000'", "const API_BASE = 'http://localhost:5000'\n" + fetchWithRetryCode);
code = code.replaceAll('await fetch(', 'await fetchWithRetry(');

const oldErrBlock = "      // ✅ NEW: Specific handling for 503 Service Unavailable\n      if (res.status === 503) {\n        addToast(\n          'LiteLLM proxy offline. Start: python -m litellm.proxy.proxy --config litellm_config.yaml --port 4000',\n          'error'\n        )\n        setScoringJobId(null)\n        return\n      }";
code = code.replace(oldErrBlock, "");

const oldErrBlockWin = "      // ✅ NEW: Specific handling for 503 Service Unavailable\r\n      if (res.status === 503) {\r\n        addToast(\r\n          'LiteLLM proxy offline. Start: python -m litellm.proxy.proxy --config litellm_config.yaml --port 4000',\r\n          'error'\r\n        )\r\n        setScoringJobId(null)\r\n        return\r\n      }";
code = code.replace(oldErrBlockWin, "");

fs.writeFileSync(path, code);
console.log('Rewrite complete');
