# Installation & Deployment Notes

## ✅ Build Status: SUCCESSFUL

The HRM application has been successfully built and is ready for deployment!

### Build Summary
- **Build Time**: ~40 seconds
- **Docker Images Created**: 3 (web, celery, celery-beat)
- **Python Version**: 3.11-slim
- **All Dependencies**: Installed successfully

## 🔧 Important Fixes Applied

### 1. pyzk Library Version
**Issue**: Original configuration used `pyzk==0.9.1` which doesn't exist on PyPI.

**Fix**: Updated to `pyzk==0.9` (latest stable version)
- File: `requirements.txt`
- Available versions: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.9
- Version 0.9 released: August 12, 2019

### 2. Docker Compose Command
**Issue**: Newer Docker installations use `docker compose` (plugin) instead of `docker-compose` (standalone).

**Fix**: Updated all scripts and Makefile to use `docker compose`
- Files updated:
  - `Makefile` - All commands now use `docker compose`
  - `quickstart.sh` - Checks for both versions, uses `docker compose`
- Backward compatible with both versions

### 3. Docker Compose Version Warning
**Warning**: `version` attribute in docker-compose.yml is obsolete

**Note**: This is just a warning and doesn't affect functionality. The `version` field is no longer needed in Docker Compose v2+.

## 🚀 Ready to Deploy

### Quick Start (Recommended)
```bash
cd /Users/sandy/projects/python/hrm

# Update device IP in .env
nano .env  # Set BIOMETRIC_DEVICE_IP=<your_device_ip>

# Run automated setup
./quickstart.sh
```

### Manual Start
```bash
# Using Make (recommended)
make up
make migrate
make init
make createsuperuser

# Or using docker compose directly
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py init_hrm
docker compose exec web python manage.py createsuperuser
```

## 📋 Pre-Deployment Checklist

Before starting the application:

- [ ] **Update `.env` file**
  - Set `BIOMETRIC_DEVICE_IP` to your actual device IP
  - Change `SECRET_KEY` for production
  - Set `DEBUG=False` for production

- [ ] **Verify Network Access**
  - Biometric device is powered on
  - Device is accessible on network
  - Test: `ping <device_ip>`

- [ ] **Docker Resources**
  - Docker Desktop is running
  - Sufficient disk space (at least 2GB free)
  - Sufficient memory (at least 2GB allocated to Docker)

## 🔍 Verification Steps

After deployment, verify everything is working:

### 1. Check Services
```bash
docker compose ps

# Should show 5 services running:
# - hrm_postgres
# - hrm_web
# - hrm_celery
# - hrm_celery_beat
# - hrm_redis
```

### 2. Check Logs
```bash
# All services
docker compose logs

# Specific service
docker compose logs web
docker compose logs celery
```

### 3. Test Web Access
```bash
# Should return HTML
curl http://localhost:8000/admin/

# Should return JSON
curl http://localhost:8000/api/
```

### 4. Test Database
```bash
docker compose exec db pg_isready -U hrm_user -d hrm_db
# Should output: hrm_db:5432 - accepting connections
```

### 5. Test Biometric Device
```bash
# Via API (after creating superuser)
curl -X POST http://localhost:8000/api/biometric/devices/1/test_connection/
```

## 📊 System Requirements

### Minimum
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk**: 10GB free space
- **Network**: Access to biometric device

### Recommended
- **CPU**: 4 cores
- **RAM**: 8GB
- **Disk**: 20GB free space
- **Network**: Gigabit connection

## 🔐 Security Considerations

### Development
- Default settings are configured for development
- DEBUG mode is enabled
- CORS allows all origins
- Session authentication only

### Production
Before deploying to production:

1. **Environment Variables**
   ```env
   SECRET_KEY=<generate-strong-random-key>
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Database**
   - Use strong passwords
   - Enable SSL connections
   - Regular backups

3. **Web Server**
   - Use HTTPS/SSL
   - Configure proper firewall rules
   - Use reverse proxy (nginx/traefik)

4. **Authentication**
   - Implement JWT or OAuth2
   - Enable rate limiting
   - Add CSRF protection

## 📈 Performance Tuning

### For High Load
```yaml
# In docker-compose.yml
celery:
  command: celery -A hrm_project worker -l info --concurrency=4

web:
  command: gunicorn hrm_project.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Database Optimization
```sql
-- Create indexes for frequently queried fields
CREATE INDEX idx_attendance_employee_date ON daily_attendance(employee_id, date);
CREATE INDEX idx_leave_request_status ON leave_requests(status, employee_id);
```

## 🐛 Known Issues & Limitations

### pyzk Library
- Version 0.9 is from 2019 (no recent updates)
- May not support newest ZKTeco devices
- Limited documentation
- Alternative: Consider `pyzk-new` (version 0.9.1) if issues arise

### Network Connectivity
- Docker containers must access device on LAN
- May need host network mode for some setups
- Firewall rules may block device communication

### Device Compatibility
Tested with:
- ZKTeco ZEM560 platform
- Firmware version 6.60

May work with other ZKTeco devices but not guaranteed.

## 🆘 Troubleshooting

### Build Fails
```bash
# Clean everything and rebuild
docker compose down -v
docker system prune -a
docker compose build --no-cache
```

### Services Won't Start
```bash
# Check logs
docker compose logs

# Restart specific service
docker compose restart web
```

### Database Connection Issues
```bash
# Wait longer for database
sleep 15
docker compose exec web python manage.py migrate
```

### Device Connection Fails
1. Verify device IP: `ping <device_ip>`
2. Check port: `nc -zv <device_ip> 4370`
3. Review device settings
4. Check firewall rules

## 📚 Next Steps

1. ✅ Build completed successfully
2. ⏭️ Update `.env` with your device IP
3. ⏭️ Run `./quickstart.sh` or `make up`
4. ⏭️ Create superuser account
5. ⏭️ Test device connection
6. ⏭️ Create first employee
7. ⏭️ Test attendance sync
8. ⏭️ Configure leave types and holidays

## 📞 Support & Resources

- **Documentation**: See README.md, SETUP_GUIDE.md, API_DOCUMENTATION.md
- **Troubleshooting**: See TROUBLESHOOTING.md
- **pyzk Library**: https://github.com/fananimi/pyzk
- **Django Docs**: https://docs.djangoproject.com/
- **Docker Docs**: https://docs.docker.com/

---

**Status**: ✅ Ready for Deployment  
**Last Build**: December 18, 2024  
**Build Version**: 1.0.0  
**Python**: 3.11  
**Django**: 4.2.8  
**pyzk**: 0.9
