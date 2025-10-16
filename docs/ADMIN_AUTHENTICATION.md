# Admin Authentication Setup

This document explains how to set up and use the secure admin authentication system for the Freakin Beats web application.

## Overview

The admin authentication system provides secure access to the admin panel using a passphrase-based authentication system. It includes:

- **Passphrase-only authentication** (no username required)
- **Secure session management** with automatic timeout
- **Rate limiting** to prevent brute force attacks
- **Constant-time comparison** to prevent timing attacks
- **Secure cookie configuration**

## Setup Instructions

### 1. Configure Admin Passphrase

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Edit the `.env` file and set a strong admin passphrase:
   ```bash
   # Admin Authentication
   ADMIN_PASSPHRASE=your_very_secure_passphrase_here
   ```

3. **Important Security Notes:**
   - Use a strong, unique passphrase (at least 16 characters)
   - Include a mix of uppercase, lowercase, numbers, and special characters
   - Never use common passwords or dictionary words
   - Consider using a password manager to generate a secure passphrase

### 2. Production Security Configuration

For production deployment, update the following settings in your environment:

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false

# Admin Authentication
ADMIN_PASSPHRASE=your_production_passphrase_here

# Session Security (set these in production)
SECRET_KEY=your_very_secure_secret_key_here
```

## Usage

### Accessing the Admin Panel

1. Navigate to `/admin-login` in your browser
2. Enter the admin passphrase
3. Upon successful authentication, you'll be redirected to `/admin`

### Admin Panel Features

Once authenticated, you can:
- View access logs with filtering and pagination
- Trigger Discogs synchronization
- Clear AI-generated label overview cache
- Regenerate label overviews
- Export access logs

### Logout

Click the "🚪 Logout" button in the admin panel to securely log out.

## Security Features

### Rate Limiting
- Maximum 5 failed login attempts
- 15-minute lockout after failed attempts
- Automatic reset after successful login

### Session Security
- Sessions expire after 1 hour of inactivity
- Secure cookie configuration
- HTTP-only cookies to prevent XSS attacks
- SameSite cookie protection

### Authentication Security
- Constant-time passphrase comparison (prevents timing attacks)
- No username enumeration (passphrase-only)
- Secure session management
- Automatic logout on session expiry

## Troubleshooting

### Common Issues

1. **"ADMIN_PASSPHRASE not configured" warning**
   - Ensure the `ADMIN_PASSPHRASE` is set in your `.env` file
   - Restart the application after adding the environment variable

2. **"Too many failed attempts" error**
   - Wait 15 minutes before trying again
   - Or restart the application to reset the rate limiting

3. **Session expires quickly**
   - Sessions are configured to last 1 hour
   - This is a security feature to prevent unauthorized access

### Security Best Practices

1. **Regular Passphrase Updates**
   - Change the admin passphrase regularly
   - Use a unique passphrase for each environment (dev/staging/production)

2. **Environment Security**
   - Never commit the `.env` file to version control
   - Use environment variables in production
   - Consider using a secrets management system

3. **Access Monitoring**
   - Monitor access logs for suspicious activity
   - Review failed login attempts regularly

## Development vs Production

### Development
- Rate limiting is active but more lenient
- Sessions last 1 hour
- Debug mode may show additional information

### Production
- All security features are fully active
- Consider setting `SESSION_COOKIE_SECURE=True` for HTTPS
- Use a strong, unique `SECRET_KEY`
- Monitor logs for security events

## API Endpoints

The following admin endpoints require authentication:

- `GET /admin` - Admin panel page
- `GET /admin/access-logs` - Fetch access logs
- `POST /admin/sync-discogs` - Trigger Discogs sync
- `POST /admin/clear-label-cache` - Clear label cache
- `POST /admin/regenerate-label-overview` - Regenerate label overview

All these endpoints will redirect to `/admin-login` if the user is not authenticated.
