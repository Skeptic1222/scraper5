# Database File Storage and User Isolation

## Overview
The scraper now stores downloaded files in the database and ensures complete user isolation - users can only see and access their own downloaded files.

## Key Features

### 1. Database Storage
- Files are stored in the `MediaBlob` table as binary data
- Each file is linked to both an `Asset` record and a `User` record
- The `stored_in_db` field in the Asset model tracks whether a file is stored in the database

### 2. User Isolation
- Each downloaded file is associated with the user who initiated the download
- Users can only see and access their own files
- Admins can see all files
- Guest users can only see public files (where user_id is NULL)

### 3. File Tracking
- When files are downloaded, they are automatically tracked in the database
- The progress callback system reports each downloaded file
- Files are associated with the job and user who initiated the download

## How It Works

### During Download:
1. User starts a download job (authenticated users get their ID attached to the job)
2. As files are downloaded, the downloader reports them through the progress callback
3. The progress callback creates an Asset record with the user's ID
4. The file content is stored in a MediaBlob record, also linked to the user

### Viewing Assets:
```
GET /api/assets
```
- Authenticated users see only their own assets
- Admins see all assets
- Guests see only public assets (user_id = NULL)

### Accessing Files:
```
GET /api/media/<asset_id>
```
- Checks if the requesting user owns the asset
- Serves the file from the database blob
- Returns 403 Forbidden if the user doesn't own the file

## Database Schema

### Asset Table
- `user_id`: Links the asset to the user who downloaded it
- `stored_in_db`: Boolean indicating if the file is stored in MediaBlob
- Other metadata (filename, size, type, etc.)

### MediaBlob Table
- `asset_id`: Links to the Asset record
- `user_id`: Enforces user ownership at the blob level
- `media_data`: The actual file content as binary data
- `mime_type`: Content type for proper serving
- Access tracking fields

## Security Benefits

1. **Complete User Isolation**: Users cannot access each other's files
2. **No Direct File Access**: Files can be stored in the database instead of the filesystem
3. **Access Control**: Every file access is authenticated and authorized
4. **Audit Trail**: File access is tracked with timestamps and counters

## Configuration

To enable full database storage (remove files from filesystem after storing):
1. Edit `db_job_manager.py`
2. Uncomment the line `# os.remove(filepath)` in the `add_asset` method
3. This will delete files from disk after storing them in the database

## Future Enhancements

1. **Encryption**: Files could be encrypted before storing in the database
2. **Compression**: Large files could be compressed to save database space
3. **CDN Integration**: Frequently accessed files could be cached in a CDN
4. **Quota Management**: User storage quotas could be implemented 