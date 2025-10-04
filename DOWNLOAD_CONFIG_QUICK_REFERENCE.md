# Download Configuration Quick Reference

**Last Updated**: 2025-10-02

Quick reference guide for tuning download robustness settings based on your environment.

---

## Configuration Variables

### Core Settings

| Variable | Default | Range | Description |
|----------|---------|-------|-------------|
| `MAX_CONCURRENT_SOURCES` | 5 | 1-10 | Number of sources to download from simultaneously |
| `SOURCE_TIMEOUT` | 30 | 10-120 | Max seconds per source before timeout |
| `GLOBAL_JOB_TIMEOUT` | 300 | 60-600 | Max seconds for entire job |
| `REQUEST_TIMEOUT` | 15 | 5-60 | Max seconds for HTTP request (connect + read) |

### Retry Settings

| Variable | Default | Range | Description |
|----------|---------|-------|-------------|
| `MAX_RETRIES_PER_SOURCE` | 3 | 0-10 | Retries at source level |
| `MAX_RETRIES_PER_ITEM` | 2 | 0-5 | Retries per individual URL |

### Stall Detection

| Variable | Default | Range | Description |
|----------|---------|-------|-------------|
| `MIN_DOWNLOAD_SPEED` | 1024 | 512-8192 | Minimum bytes/sec before considering stalled |
| `STALL_TIMEOUT` | 30 | 10-120 | Max seconds below minimum speed |

### Circuit Breaker

| Variable | Default | Range | Description |
|----------|---------|-------|-------------|
| `CIRCUIT_BREAKER_THRESHOLD` | 5 | 3-20 | Failures before opening circuit |
| `CIRCUIT_BREAKER_TIMEOUT` | 60 | 30-300 | Seconds before trying again |

---

## Preset Configurations

### Fast & Reliable Network
```bash
MAX_CONCURRENT_SOURCES=8
SOURCE_TIMEOUT=20
GLOBAL_JOB_TIMEOUT=240
REQUEST_TIMEOUT=10
MAX_RETRIES_PER_SOURCE=2
MIN_DOWNLOAD_SPEED=4096
STALL_TIMEOUT=15
CIRCUIT_BREAKER_THRESHOLD=3
CIRCUIT_BREAKER_TIMEOUT=30
```
**Use when**: Office network, fiber connection, low latency

---

### Standard Network (Default)
```bash
MAX_CONCURRENT_SOURCES=5
SOURCE_TIMEOUT=30
GLOBAL_JOB_TIMEOUT=300
REQUEST_TIMEOUT=15
MAX_RETRIES_PER_SOURCE=3
MIN_DOWNLOAD_SPEED=1024
STALL_TIMEOUT=30
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60
```
**Use when**: Home broadband, stable connection, moderate speed

---

### Slow or Unstable Network
```bash
MAX_CONCURRENT_SOURCES=3
SOURCE_TIMEOUT=60
GLOBAL_JOB_TIMEOUT=600
REQUEST_TIMEOUT=30
MAX_RETRIES_PER_SOURCE=5
MIN_DOWNLOAD_SPEED=512
STALL_TIMEOUT=60
CIRCUIT_BREAKER_THRESHOLD=8
CIRCUIT_BREAKER_TIMEOUT=120
```
**Use when**: Mobile hotspot, rural connection, high latency

---

### High-Volume Production
```bash
MAX_CONCURRENT_SOURCES=10
SOURCE_TIMEOUT=45
GLOBAL_JOB_TIMEOUT=900
REQUEST_TIMEOUT=20
MAX_RETRIES_PER_SOURCE=4
MIN_DOWNLOAD_SPEED=2048
STALL_TIMEOUT=40
CIRCUIT_BREAKER_THRESHOLD=7
CIRCUIT_BREAKER_TIMEOUT=90
```
**Use when**: Server deployment, high bandwidth, many concurrent jobs

---

## Tuning Guide

### Problem: Jobs timing out frequently
**Solution**: Increase timeouts
```bash
SOURCE_TIMEOUT=60        # Double from 30
GLOBAL_JOB_TIMEOUT=600   # Double from 300
REQUEST_TIMEOUT=30       # Double from 15
```

### Problem: Too many retries, jobs taking too long
**Solution**: Reduce retry attempts
```bash
MAX_RETRIES_PER_SOURCE=1
MAX_RETRIES_PER_ITEM=1
CIRCUIT_BREAKER_THRESHOLD=3  # Fail faster
```

### Problem: Downloads stalling on slow sources
**Solution**: More aggressive stall detection
```bash
MIN_DOWNLOAD_SPEED=2048  # Higher minimum
STALL_TIMEOUT=20         # Shorter timeout
```

### Problem: Circuit breaker too sensitive
**Solution**: Increase threshold or timeout
```bash
CIRCUIT_BREAKER_THRESHOLD=10   # More failures allowed
CIRCUIT_BREAKER_TIMEOUT=180    # Wait longer before retry
```

### Problem: Not enough parallelism
**Solution**: Increase concurrency
```bash
MAX_CONCURRENT_SOURCES=8   # More parallel sources
```

### Problem: Too much memory/CPU usage
**Solution**: Reduce concurrency
```bash
MAX_CONCURRENT_SOURCES=3   # Fewer parallel sources
```

---

## Monitoring and Adjustment

### Watch These Log Messages

**Good Signs**:
```
[SUCCESS] Downloaded: file.jpg (245,678 bytes in 2.3s at 104.5 KB/s)
[INFO] DOWNLOAD STATS | Attempts: 50, Successes: 48, Failures: 2, Retries: 3
[INFO] SOURCE STATS | google: Circuit=CLOSED
```

**Warning Signs**:
```
[RETRY] Attempt 3/4 for https://...
[TIMEOUT] https://... : Timeout after 15s
[CIRCUIT BREAKER] Circuit opened for bing after 5 failures
```

**Bad Signs**:
```
[FAILED] Failed to download ... after 4 attempts
[GLOBAL TIMEOUT] Job abc123 exceeded 300s
[INFO] DOWNLOAD STATS | Successes: 10, Failures: 40
```

### Adjustment Strategy

1. **Monitor for 1 week** with default settings
2. **Check success rate** in logs
   - If < 80%: Increase retries and timeouts
   - If > 95%: Can reduce retries for faster completion
3. **Check average job time**
   - If too long: Reduce retries, increase stall detection
   - If too short with low success: Increase timeouts
4. **Check circuit breaker events**
   - If too frequent: Increase threshold
   - If never triggered: Decrease threshold

---

## Performance Impact

### Increasing Concurrency
- **Benefit**: Faster job completion
- **Cost**: More CPU, memory, network bandwidth
- **Recommendation**: Don't exceed 10 on typical hardware

### Increasing Retries
- **Benefit**: Higher success rate
- **Cost**: Longer job completion time
- **Recommendation**: 3-5 retries is optimal

### Decreasing Timeouts
- **Benefit**: Faster failure detection
- **Cost**: May fail on slow but working downloads
- **Recommendation**: Match to your network speed

### Circuit Breaker Threshold
- **Lower (3-5)**: Fail faster, less wasted time
- **Higher (8-10)**: More patient, better for flaky sources
- **Recommendation**: 5 is balanced for most cases

---

## Examples by Use Case

### Development Environment
```bash
# Fast iteration, don't wait forever
MAX_CONCURRENT_SOURCES=5
SOURCE_TIMEOUT=20
REQUEST_TIMEOUT=10
MAX_RETRIES_PER_SOURCE=1
CIRCUIT_BREAKER_THRESHOLD=3
```

### Automated Testing
```bash
# Fast failure, predictable timing
MAX_CONCURRENT_SOURCES=3
SOURCE_TIMEOUT=15
REQUEST_TIMEOUT=8
MAX_RETRIES_PER_SOURCE=0
CIRCUIT_BREAKER_THRESHOLD=1
```

### Production Web Service
```bash
# Balanced reliability and performance
MAX_CONCURRENT_SOURCES=5
SOURCE_TIMEOUT=30
REQUEST_TIMEOUT=15
MAX_RETRIES_PER_SOURCE=3
CIRCUIT_BREAKER_THRESHOLD=5
```

### Batch Processing Overnight
```bash
# Maximum reliability, time is less critical
MAX_CONCURRENT_SOURCES=10
SOURCE_TIMEOUT=120
REQUEST_TIMEOUT=60
MAX_RETRIES_PER_SOURCE=10
CIRCUIT_BREAKER_THRESHOLD=15
```

---

## Quick Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| All downloads failing | Network issue or invalid config | Check network, verify settings |
| Some sources always fail | Dead source or wrong API key | Check circuit breaker logs |
| Jobs never complete | Timeout too high | Reduce GLOBAL_JOB_TIMEOUT |
| High CPU usage | Too many concurrent sources | Reduce MAX_CONCURRENT_SOURCES |
| Low success rate | Timeouts too short | Increase REQUEST_TIMEOUT |
| Circuit always open | Threshold too low | Increase CIRCUIT_BREAKER_THRESHOLD |

---

**Remember**: Start with defaults, monitor for a week, then adjust based on actual performance.
