-- Database Performance Optimization Indexes for Enhanced Media Scraper
-- Generated from DATABASE_QUERY_ANALYSIS.md
-- 
-- Execute these indexes to improve query performance by 50-80%
-- Test in development environment first!

-- =====================================================
-- 1. FOREIGN KEY INDEXES (Critical for JOIN performance)
-- =====================================================

-- Assets table foreign keys
CREATE NONCLUSTERED INDEX idx_assets_user_id 
ON assets(user_id) 
WHERE is_deleted = 0;

CREATE NONCLUSTERED INDEX idx_assets_job_id 
ON assets(job_id) 
WHERE is_deleted = 0;

-- Scrape jobs foreign key
CREATE NONCLUSTERED INDEX idx_scrape_jobs_user_id 
ON scrape_jobs(user_id);

-- User roles junction table (both directions needed)
CREATE NONCLUSTERED INDEX idx_user_roles_user_id 
ON user_roles(user_id);

CREATE NONCLUSTERED INDEX idx_user_roles_role_id 
ON user_roles(role_id);

-- Media blobs foreign keys
CREATE NONCLUSTERED INDEX idx_media_blobs_asset_id 
ON media_blobs(asset_id);

CREATE NONCLUSTERED INDEX idx_media_blobs_user_id 
ON media_blobs(user_id);

-- OAuth table
CREATE NONCLUSTERED INDEX idx_oauth_user_id 
ON oauth(user_id);

-- =====================================================
-- 2. QUERY OPTIMIZATION INDEXES
-- =====================================================

-- Asset queries often order by downloaded_at DESC
CREATE NONCLUSTERED INDEX idx_assets_downloaded_at_desc 
ON assets(downloaded_at DESC) 
WHERE is_deleted = 0;

-- Job queries filter by status frequently
CREATE NONCLUSTERED INDEX idx_scrape_jobs_status 
ON scrape_jobs(status)
INCLUDE (user_id, job_type, progress);

-- Job listing queries order by start_time
CREATE NONCLUSTERED INDEX idx_scrape_jobs_start_time_desc 
ON scrape_jobs(start_time DESC)
INCLUDE (status, user_id);

-- =====================================================
-- 3. COMPOSITE INDEXES FOR COMMON QUERY PATTERNS
-- =====================================================

-- Assets filtered by user and type
CREATE NONCLUSTERED INDEX idx_assets_user_type 
ON assets(user_id, file_type, downloaded_at DESC) 
WHERE is_deleted = 0
INCLUDE (filename, file_size, source_name);

-- Jobs filtered by user and status
CREATE NONCLUSTERED INDEX idx_jobs_user_status 
ON scrape_jobs(user_id, status, start_time DESC)
INCLUDE (progress, downloaded, job_type);

-- Active jobs query optimization
CREATE NONCLUSTERED INDEX idx_jobs_active 
ON scrape_jobs(status)
WHERE status IN ('starting', 'running')
INCLUDE (user_id, start_time, progress);

-- =====================================================
-- 4. SPECIALIZED INDEXES FOR SPECIFIC QUERIES
-- =====================================================

-- User email lookups (for admin)
CREATE UNIQUE NONCLUSTERED INDEX idx_users_email 
ON users(email)
INCLUDE (name, subscription_plan, credits);

-- Asset statistics queries
CREATE NONCLUSTERED INDEX idx_assets_stats 
ON assets(user_id, is_deleted, file_type)
INCLUDE (file_size)
WHERE is_deleted = 0;

-- Job statistics queries  
CREATE NONCLUSTERED INDEX idx_jobs_stats
ON scrape_jobs(user_id, status, end_time)
INCLUDE (downloaded, images, videos);

-- =====================================================
-- 5. COVERING INDEXES FOR HEAVY QUERIES
-- =====================================================

-- Asset listing with all needed columns (prevents key lookups)
CREATE NONCLUSTERED INDEX idx_assets_listing_covered
ON assets(user_id, is_deleted, downloaded_at DESC)
INCLUDE (
    filename, file_path, file_type, file_size, 
    file_extension, source_name, source_url,
    width, height, duration, thumbnail_path,
    job_id, stored_in_db
)
WHERE is_deleted = 0;

-- =====================================================
-- 6. MAINTENANCE QUERIES
-- =====================================================

-- Rebuild fragmented indexes (run weekly)
/*
SELECT 
    OBJECT_NAME(ps.object_id) AS TableName,
    i.name AS IndexName,
    ps.avg_fragmentation_in_percent
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ps
INNER JOIN sys.indexes i ON ps.object_id = i.object_id AND ps.index_id = i.index_id
WHERE ps.avg_fragmentation_in_percent > 30
ORDER BY ps.avg_fragmentation_in_percent DESC;
*/

-- Update statistics (run daily)
/*
UPDATE STATISTICS assets WITH FULLSCAN;
UPDATE STATISTICS scrape_jobs WITH FULLSCAN;
UPDATE STATISTICS users WITH FULLSCAN;
UPDATE STATISTICS media_blobs WITH FULLSCAN;
*/

-- =====================================================
-- 7. MONITORING QUERIES
-- =====================================================

-- Check index usage after implementation
/*
SELECT 
    OBJECT_NAME(s.[object_id]) AS TableName,
    i.name AS IndexName,
    s.user_seeks + s.user_scans + s.user_lookups AS TotalReads,
    s.user_updates AS TotalWrites,
    CAST(s.user_seeks + s.user_scans + s.user_lookups AS FLOAT) / 
        NULLIF(s.user_updates, 0) AS ReadWriteRatio
FROM sys.dm_db_index_usage_stats s
INNER JOIN sys.indexes i ON s.[object_id] = i.[object_id] 
    AND s.index_id = i.index_id
WHERE OBJECTPROPERTY(s.[object_id],'IsUserTable') = 1
    AND i.name IS NOT NULL
ORDER BY TotalReads DESC;
*/

-- =====================================================
-- 8. PERFORMANCE IMPACT NOTES
-- =====================================================
/*
Expected improvements after applying these indexes:

1. Asset listing queries: 60-80% faster
2. Job status checks: 50-70% faster  
3. User permission checks: 40-60% faster
4. Admin asset views: 70-90% faster (eliminates N+1 queries)
5. Statistics queries: 80-95% faster

Storage impact:
- Estimated 200-500 MB additional storage for indexes
- Slight write performance impact (5-10%) during inserts/updates
- Significantly improved read performance outweighs write cost

Maintenance:
- Run index rebuild weekly during low-usage hours
- Update statistics daily
- Monitor index fragmentation monthly
*/