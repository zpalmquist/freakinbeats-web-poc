# 📊 Access Logging System

## Overview

The Freakinbeats application now includes a comprehensive access logging system that automatically tracks all HTTP requests to the website in a SQLite database.

## Features

### ✅ Automatic Logging
Every HTTP request is automatically logged to the database including:
- **Timestamp**: When the request occurred
- **HTTP Method**: GET, POST, PUT, DELETE, etc.
- **Path**: The requested URL path
- **Query String**: URL parameters
- **IP Address**: Client's IP address
- **User Agent**: Browser and device information
- **Referrer**: Where the request came from
- **Status Code**: HTTP response status (200, 404, 500, etc.)
- **Response Time**: How long the request took (milliseconds)
- **Endpoint**: Flask endpoint name

### 📊 Analytics & Statistics
Built-in API endpoints provide insights:
- Total request counts
- Requests by HTTP method
- Requests by status code
- Top visited paths
- Average response times
- Filterable access logs

## Database Schema

### `access_logs` Table

| Column | Type | Description | Indexed |
|--------|------|-------------|---------|
| id | INTEGER | Primary key | ✓ |
| timestamp | DATETIME | Request timestamp | ✓ |
| method | VARCHAR(10) | HTTP method | |
| path | VARCHAR(500) | URL path | ✓ |
| query_string | VARCHAR(500) | URL parameters | |
| full_url | VARCHAR(1000) | Complete URL | |
| ip_address | VARCHAR(50) | Client IP | ✓ |
| user_agent | VARCHAR(500) | Browser info | |
| referrer | VARCHAR(500) | Referrer URL | |
| status_code | INTEGER | HTTP status | ✓ |
| response_time_ms | FLOAT | Response time | |
| endpoint | VARCHAR(100) | Flask endpoint | |

## API Endpoints

### Get Access Logs
```
GET /api/logs
```

**Parameters:**
- `limit` (default: 100) - Number of logs to return
- `path` - Filter by path (partial match)
- `method` - Filter by HTTP method (GET, POST, etc.)
- `ip` - Filter by IP address

**Example:**
```bash
# Get last 10 logs
curl http://localhost:3000/api/logs?limit=10

# Get all GET requests
curl http://localhost:3000/api/logs?method=GET

# Get logs for specific path
curl http://localhost:3000/api/logs?path=/api/data

# Get logs from specific IP
curl http://localhost:3000/api/logs?ip=127.0.0.1
```

**Response:**
```json
[
  {
    "id": 123,
    "timestamp": "2025-10-10T15:30:00",
    "method": "GET",
    "path": "/api/data",
    "query_string": "q=DJ",
    "full_url": "http://localhost:3000/api/data?q=DJ",
    "ip_address": "127.0.0.1",
    "user_agent": "Mozilla/5.0...",
    "referrer": "http://localhost:3000/",
    "status_code": 200,
    "response_time_ms": 45.3,
    "endpoint": "api.get_data"
  }
]
```

### Get Access Log Statistics
```
GET /api/logs/stats
```

Returns aggregated statistics about access patterns.

**Example:**
```bash
curl http://localhost:3000/api/logs/stats
```

**Response:**
```json
{
  "total_requests": 1523,
  "by_method": {
    "GET": 1450,
    "POST": 73
  },
  "by_status": {
    "200": 1402,
    "304": 98,
    "404": 15,
    "500": 8
  },
  "top_paths": [
    {"path": "/", "count": 450},
    {"path": "/api/data", "count": 320},
    {"path": "/api/search", "count": 180}
  ],
  "avg_response_time_ms": 42.5
}
```

## Usage Examples

### Python
```python
import requests

# Get recent logs
response = requests.get('http://localhost:3000/api/logs?limit=20')
logs = response.json()

for log in logs:
    print(f"{log['timestamp']}: {log['method']} {log['path']} [{log['status_code']}]")

# Get statistics
stats = requests.get('http://localhost:3000/api/logs/stats').json()
print(f"Total requests: {stats['total_requests']}")
print(f"Average response time: {stats['avg_response_time_ms']}ms")
```

### JavaScript
```javascript
// Fetch access logs
fetch('/api/logs?limit=50')
  .then(res => res.json())
  .then(logs => {
    console.log(`Retrieved ${logs.length} access logs`);
    logs.forEach(log => {
      console.log(`${log.timestamp}: ${log.method} ${log.path}`);
    });
  });

// Fetch statistics
fetch('/api/logs/stats')
  .then(res => res.json())
  .then(stats => {
    console.log('Total requests:', stats.total_requests);
    console.log('Top paths:', stats.top_paths);
  });
```

### SQL Query
```sql
-- View recent access logs
SELECT timestamp, method, path, status_code, response_time_ms
FROM access_logs
ORDER BY timestamp DESC
LIMIT 20;

-- Get request counts by path
SELECT path, COUNT(*) as count
FROM access_logs
GROUP BY path
ORDER BY count DESC
LIMIT 10;

-- Get slowest requests
SELECT timestamp, method, path, response_time_ms
FROM access_logs
WHERE response_time_ms IS NOT NULL
ORDER BY response_time_ms DESC
LIMIT 10;

-- Get error requests
SELECT timestamp, method, path, status_code, ip_address
FROM access_logs
WHERE status_code >= 400
ORDER BY timestamp DESC;
```

## Testing

Run the test suite to verify access logging:

```bash
python3 test_api.py
```

The test includes:
- ✅ Access logs retrieval
- ✅ Log statistics generation
- ✅ Sample log display

## Performance Considerations

### Database Size
Access logs can grow quickly. Monitor the database size:

```bash
# Check database size
ls -lh freakinbeats.db

# Count access logs
sqlite3 freakinbeats.db "SELECT COUNT(*) FROM access_logs;"
```

### Cleanup Old Logs

To prevent unlimited growth, you can periodically clean old logs:

```python
# Delete logs older than 30 days
from datetime import datetime, timedelta
from app.models.access_log import AccessLog
from app.extensions import db

cutoff_date = datetime.utcnow() - timedelta(days=30)
AccessLog.query.filter(AccessLog.timestamp < cutoff_date).delete()
db.session.commit()
```

Or via SQL:
```bash
sqlite3 freakinbeats.db "DELETE FROM access_logs WHERE timestamp < datetime('now', '-30 days');"
```

## Privacy Considerations

The access logs include:
- ✅ IP addresses (can identify users)
- ✅ User agents (device/browser info)
- ✅ Referrers (where users came from)
- ✅ Request paths (what pages they visited)

**Recommendations:**
- Implement log retention policies
- Consider anonymizing IP addresses
- Comply with privacy regulations (GDPR, CCPA)
- Don't log sensitive data in URLs
- Secure access to log endpoints

## Configuration

### Disable Logging (if needed)

To disable access logging, comment out in `app/__init__.py`:

```python
# Initialize access logging middleware
# from app.middleware.access_logger import init_access_logging
# init_access_logging(app)
```

### Custom Logging

Modify `app/middleware/access_logger.py` to customize what gets logged.

## Troubleshooting

### Logs not appearing?

1. **Check table exists:**
   ```bash
   sqlite3 freakinbeats.db ".tables"
   ```

2. **Verify middleware is loaded:**
   Look for log message: `Access logging middleware initialized`

3. **Check for errors:**
   Look in Flask logs for: `Error logging access:`

### High database growth?

Implement automatic cleanup or use log rotation.

## Future Enhancements

Potential improvements:
- 🔄 Automatic log rotation
- 📈 Real-time analytics dashboard
- 🔍 Advanced filtering and search
- 📊 Export to CSV/JSON
- 📧 Email alerts for errors
- 🎯 Custom event tracking
- 🗺️ Geographic IP tracking
- 📱 User session tracking

## Architecture

```
Request → Flask App → before_request hook
                          ↓
                   [Record start time]
                          ↓
                   Process request
                          ↓
                   after_request hook
                          ↓
            [Create AccessLog entry]
                          ↓
            [Save to database]
                          ↓
                   Return response
```

## Files Created

- `app/models/access_log.py` - AccessLog model
- `app/middleware/access_logger.py` - Logging middleware
- `app/middleware/__init__.py` - Middleware package
- Updated `app/routes/api.py` - Log API endpoints
- Updated `app/__init__.py` - Initialize middleware
- Updated `test_api.py` - Test log endpoints

## Summary

The access logging system provides:
- ✅ Automatic request tracking
- ✅ Performance monitoring
- ✅ Usage analytics
- ✅ Error tracking
- ✅ RESTful API access
- ✅ SQL query capability
- ✅ Zero configuration required

All requests are now automatically logged to the database for analysis and monitoring! 📊

