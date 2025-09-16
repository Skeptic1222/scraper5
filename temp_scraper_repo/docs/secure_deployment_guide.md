# Secure Deployment Guide

This guide walks through deploying the secure version of the Scraper application.

## Pre-Deployment Checklist

### 1. Environment Setup

1. **Create secure .env file**:
   ```bash
   python secure_env_migration.py
   ```
   
2. **Update credentials in .env**:
   - Google OAuth Client ID and Secret
   - PayPal Client ID and Secret (use sandbox for testing)
   - Generate new SECRET_KEY (done automatically by migration script)

3. **Regenerate all exposed API keys**:
   - Google OAuth: https://console.cloud.google.com/apis/credentials
   - PayPal: https://developer.paypal.com/dashboard/
   - OpenAI: https://platform.openai.com/api-keys

### 2. Database Migration

1. **Backup existing database**:
   ```sql
   BACKUP DATABASE [Scraped] 
   TO DISK = 'C:\Backups\Scraped_backup_YYYYMMDD.bak'
   WITH FORMAT, INIT;
   ```

2. **Apply security migrations**:
   ```bash
   python migrate_app.py
   ```

3. **Verify migrations**:
   ```bash
   python verify_sqlserver.py
   ```

### 3. Code Deployment

1. **Replace insecure files with secure versions**:
   ```bash
   # Backup originals
   cp app.py app_original.py
   cp models.py models_original.py
   cp auth.py auth_original.py
   cp subscription.py subscription_original.py
   
   # Deploy secure versions
   cp app_secure.py app.py
   cp models_secure.py models.py
   cp auth_secure.py auth.py
   cp subscription_secure.py subscription.py
   ```

2. **Install new dependencies**:
   ```bash
   pip install -r requirements_secure.txt
   ```

### 4. Configuration Updates

1. **Update IIS configuration** (if using IIS):
   - Enable HTTPS
   - Set secure headers
   - Configure URL rewriting for HTTPS redirect

2. **Update firewall rules**:
   - Close unnecessary ports
   - Allow only HTTPS (443) for web traffic

### 5. Testing

1. **Test authentication flow**:
   - Sign in with Google OAuth
   - Verify session security
   - Check CSRF protection

2. **Test payment flow** (sandbox):
   - Create test subscription
   - Verify webhook handling
   - Check signature verification

3. **Test security features**:
   - Rate limiting
   - Input validation
   - File upload restrictions

### 6. Production Settings

1. **Update .env for production**:
   ```
   FLASK_ENV=production
   DEBUG=False
   SESSION_COOKIE_SECURE=True
   SESSION_COOKIE_HTTPONLY=True
   WTF_CSRF_ENABLED=True
   ```

2. **Configure logging**:
   - Set appropriate log levels
   - Configure log rotation
   - Set up monitoring

### 7. Post-Deployment

1. **Monitor application**:
   - Check error logs
   - Monitor performance
   - Watch for security alerts

2. **Regular maintenance**:
   - Update dependencies
   - Rotate secrets periodically
   - Review access logs

## Rollback Plan

If issues occur:

1. **Restore database backup**:
   ```sql
   RESTORE DATABASE [Scraped] 
   FROM DISK = 'C:\Backups\Scraped_backup_YYYYMMDD.bak'
   WITH REPLACE;
   ```

2. **Restore original code**:
   ```bash
   cp app_original.py app.py
   cp models_original.py models.py
   cp auth_original.py auth.py
   cp subscription_original.py subscription.py
   ```

3. **Restart application**:
   ```bash
   python restart_app.py
   ```

## Security Best Practices

1. **Never commit .env to version control**
2. **Use environment variables in production**
3. **Enable HTTPS everywhere**
4. **Keep dependencies updated**
5. **Monitor for security vulnerabilities**
6. **Implement proper backup strategy**
7. **Use least privilege principle for database access**
8. **Enable audit logging**

## Support

For issues or questions:
- Check logs in `/logs` directory
- Review error messages in browser console
- Verify all environment variables are set correctly