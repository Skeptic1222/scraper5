# Download Debugging Guide

This guide helps verify end-to-end downloading, filesystem permissions, and API wiring.

## Quick Checks

1. Verify sources include Adult Content (always visible):

   - GET `/scraper/api/sources?safe_search=false`
   - Should include a category `Adult Content` with: EroGarga, Pornhub, XVideos, RedTube, Motherless, Rule34, e621, XHamster, YouPorn, SpankBang, RedGifs.

2. Check write permissions for the downloads directory:

   - GET `/scraper/api/debug/check-permissions`
   - Response should indicate `writable: true` and a `downloads_dir` path.

3. Test a direct download (no scraping):

   - POST `/scraper/api/debug/download-direct`
   - JSON: `{ "url": "https://picsum.photos/400" }`
   - The endpoint creates a debug job, streams progress, and returns a `file` object with `filepath` on success.

## Common Causes

- If per-file messages do not appear in the dashboard, refresh the UI. Both enhanced and comprehensive paths now post per-file updates.
- If files do not appear in `downloads/`, check the IIS app pool identity has write permissions to `C:\inetpub\wwwroot\scraper\downloads`.

## Notes

- Safe Search default is OFF across all source-loading code paths. Adult Content is always included by the API.
- EroGarga is implemented via site-restricted image search; for richer results, implement the thread crawler (Firecrawl helps).


## Safe Search Status
- The sources legend shows a ‘Safe Search: ON/OFF’ pill. Click it to toggle Safe Search and reload sources (Adult Content is always included from the API).
- In templates, default Safe Search is OFF. Ensure views do not default-check hidden toggles that run early.
