/**
 * serpapi-google-jobs.mjs — SerpAPI Google Jobs provider for career-ops scanner.
 *
 * Queries Google Jobs via SerpAPI to aggregate results from LinkedIn, Indeed,
 * Glassdoor, Bayt.com, GulfTalent, and other portals in a single API call.
 *
 * Requires SERPAPI_KEY in .env or environment.
 *
 * Provider interface:
 *   - id: 'serpapi-google-jobs'
 *   - detect(entry): matches entries with `provider: serpapi-google-jobs`
 *   - fetch(entry, ctx): returns [{title, url, company, location}]
 */

import { readFileSync, existsSync } from 'fs';

// Load .env for SERPAPI_KEY
try {
  const { config } = await import('dotenv');
  config();
} catch {
  // dotenv not available, fall back to process.env
}

const SERPAPI_KEY = process.env.SERPAPI_KEY;

/**
 * Query SerpAPI Google Jobs endpoint.
 * @param {string} query - Job search query (e.g. "Marketing Manager Dubai")
 * @param {object} options - Additional options
 * @param {string} options.location - Location filter (e.g. "Dubai, UAE")
 * @param {number} options.start - Pagination start (0, 10, 20, ...)
 * @returns {Promise<Array>} Array of job objects
 */
async function searchGoogleJobs(query, { location = '', start = 0 } = {}) {
  if (!SERPAPI_KEY) {
    throw new Error('SERPAPI_KEY not set in environment. Get a free key at https://serpapi.com');
  }

  const params = new URLSearchParams({
    engine: 'google_jobs',
    q: query,
    api_key: SERPAPI_KEY,
    start: String(start),
  });

  if (location) {
    params.set('location', location);
  }

  // Add chips for date filter (past week keeps results fresh)
  params.set('chips', 'date_posted:week');

  const url = `https://serpapi.com/search.json?${params}`;

  const response = await fetch(url, {
    headers: { 'Accept': 'application/json' },
    signal: AbortSignal.timeout(30000),
  });

  if (!response.ok) {
    const body = await response.text().catch(() => '');
    throw new Error(`SerpAPI returned ${response.status}: ${body.slice(0, 200)}`);
  }

  const data = await response.json();

  if (data.error) {
    throw new Error(`SerpAPI error: ${data.error}`);
  }

  return data.jobs_results || [];
}

/**
 * Extract a clean apply URL from SerpAPI job result.
 * SerpAPI provides apply_options with direct links.
 */
function extractApplyUrl(job) {
  // Try apply_options first (direct application links)
  if (job.apply_options && job.apply_options.length > 0) {
    // Prefer LinkedIn, then Indeed, then first available
    const preferred = ['linkedin.com', 'indeed.com', 'glassdoor.com', 'bayt.com'];
    for (const pref of preferred) {
      const match = job.apply_options.find(opt => (opt.link || '').includes(pref));
      if (match) return match.link;
    }
    return job.apply_options[0].link || '';
  }

  // Fallback to share_link or related_links
  if (job.share_link) return job.share_link;
  if (job.related_links && job.related_links.length > 0) {
    return job.related_links[0].link || '';
  }

  // Last resort: construct a Google Jobs search URL
  return `https://www.google.com/search?q=${encodeURIComponent(job.title + ' ' + job.company_name)}&ibp=htl;jobs`;
}

/**
 * Convert SerpAPI job result to career-ops format.
 */
function normalizeJob(job) {
  return {
    title: job.title || 'Unknown Title',
    company: job.company_name || 'Unknown Company',
    location: job.location || '',
    url: extractApplyUrl(job),
    description_snippet: (job.description || '').slice(0, 300),
    source_portal: (job.via || '').replace('via ', ''),
    posted: job.detected_extensions?.posted_at || '',
    salary: job.detected_extensions?.salary || '',
    schedule: job.detected_extensions?.schedule_type || '',
  };
}

export default {
  id: 'serpapi-google-jobs',

  /**
   * Detect if this provider should handle an entry.
   * Matches entries with explicit `provider: serpapi-google-jobs` or
   * entries that have a `search_query` field.
   */
  detect(entry) {
    if (entry.provider === 'serpapi-google-jobs') return { url: 'serpapi' };
    if (entry.search_query) return { url: 'serpapi' };
    return null;
  },

  /**
   * Fetch jobs from Google Jobs via SerpAPI.
   * Supports both single-company and multi-query modes.
   *
   * Entry format in portals.yml:
   * ```yaml
   * - name: "Google Jobs - Marketing Dubai"
   *   provider: serpapi-google-jobs
   *   search_query: "Marketing Manager"
   *   search_location: "Dubai, United Arab Emirates"
   *   max_pages: 3
   * ```
   */
  async fetch(entry, ctx) {
    const query = entry.search_query || entry.name;
    const location = entry.search_location || entry.location || '';
    const maxPages = entry.max_pages || 3;

    const allJobs = [];

    for (let page = 0; page < maxPages; page++) {
      try {
        const results = await searchGoogleJobs(query, {
          location,
          start: page * 10,
        });

        if (!results || results.length === 0) break;

        for (const job of results) {
          const normalized = normalizeJob(job);
          if (normalized.url) {
            allJobs.push(normalized);
          }
        }

        // SerpAPI returns ~10 results per page; if fewer, we've exhausted results
        if (results.length < 10) break;

        // Rate limit: small delay between pages
        if (page < maxPages - 1) {
          await new Promise(r => setTimeout(r, 1000));
        }
      } catch (err) {
        // Log error but continue with results we have
        console.error(`  ⚠️  SerpAPI page ${page} error for "${query}": ${err.message}`);
        break;
      }
    }

    return allJobs;
  },
};
