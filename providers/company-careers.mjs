/**
 * company-careers.mjs — Provider for searching company career pages directly
 *
 * Searches company career pages configured in portals.yml with:
 *   - careers_url: The company's career page URL
 *   - search_keywords: Array of keywords to search for on the page
 *   - job_selector: CSS selector to find job listings
 *
 * Uses Playwright for dynamic content loading and keyword matching.
 *
 * Example portals.yml entry:
 *   - name: "Company Name"
 *     careers_url: "https://company.com/careers"
 *     provider: "company-careers"
 *     search_keywords: ["Marketing", "Dubai", "AI"]
 *     job_selector: ".job-listing"
 */

import { chromium } from 'playwright';

export default {
  id: 'company-careers',

  detect(entry) {
    if (entry.careers_url && (entry.provider === 'company-careers' || !entry.provider)) {
      return { url: entry.careers_url };
    }
    return null;
  },

  async fetch(entry, ctx) {
    const careersUrl = entry.careers_url;
    const keywords = entry.search_keywords || [];
    const jobSelector = entry.job_selector || '.job-listing, [data-job-id], .job-card, li[data-job]';

    if (!careersUrl) {
      throw new Error(`${entry.name}: careers_url not configured`);
    }

    let browser;
    let jobs = [];

    try {
      // Launch headless browser
      browser = await chromium.launch({ headless: true });
      const page = await browser.newPage();

      // Set timeout and navigate
      page.setDefaultTimeout(15000);
      await page.goto(careersUrl, { waitUntil: 'networkidle' });

      // Wait for job listings to load
      try {
        await page.waitForSelector(jobSelector, { timeout: 5000 });
      } catch {
        // Selector not found, try to extract what's available
      }

      // Extract all job listings
      const jobElements = await page.$$(jobSelector);

      for (const el of jobElements) {
        try {
          // Extract title
          let title = await el.$eval('[data-job-title], .title, h2, h3, a', (el) => el.textContent.trim()).catch(() => '');
          
          // Extract company (fallback to entry.name if not found)
          const company = entry.name || careersUrl.split('/')[2];

          // Extract location
          let location = await el.$eval('[data-location], .location, [data-job-location]', (el) => el.textContent.trim()).catch(() => '');

          // Extract URL
          let url = '';
          try {
            const linkEl = await el.$('a[href]');
            if (linkEl) {
              url = await linkEl.getAttribute('href');
              // Convert relative URLs to absolute
              if (url && !url.startsWith('http')) {
                const baseUrl = new URL(careersUrl);
                url = new URL(url, baseUrl).href;
              }
            }
          } catch {
            // URL extraction failed
          }

          // Extract job description/snippet
          let description = await el.$eval('[data-description], .description, .summary, p', (el) => el.textContent.trim()).catch(() => '');

          // Check if job matches search keywords
          const jobText = `${title} ${location} ${description}`.toLowerCase();
          let matchesKeywords = keywords.length === 0; // If no keywords, include all
          if (keywords.length > 0) {
            matchesKeywords = keywords.some((kw) => jobText.includes(kw.toLowerCase()));
          }

          if (!matchesKeywords) {
            continue;
          }

          // Only include if we have at least title and URL
          if (title && url) {
            jobs.push({
              title: title,
              company: company,
              location: location || 'Not specified',
              url: url,
              description: description || 'No description available',
              source: `${entry.name} Careers`,
            });
          }
        } catch (err) {
          // Skip this job element if extraction fails
          console.error(`Error extracting job: ${err.message}`);
          continue;
        }
      }

      if (jobs.length === 0) {
        console.warn(`${entry.name}: No jobs found matching keywords ${keywords.join(', ')}`);
      }

    } catch (err) {
      throw new Error(`${entry.name}: Failed to fetch careers page — ${err.message}`);
    } finally {
      if (browser) {
        await browser.close();
      }
    }

    return jobs;
  },
};
