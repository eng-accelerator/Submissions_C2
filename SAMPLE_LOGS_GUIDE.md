# 📋 Sample Logs Testing Guide

## Available Sample Scenarios

### 1. General DevOps (`sample_logs.txt`) 
**Best for:** Initial demos and general testing

- **20 log entries** | 3 CRITICAL | 10+ ERRORS | 5 WARNINGS
- **Categories:** Database, Network, Memory, Disk, Security, Application
- **Highlights:**
  - Database connection timeouts
  - OutOfMemory errors (4GB heap)
  - HTTP 500/503 service errors
  - Disk space full (100%)
  - JWT token expiration
  - SQL injection detection

### 2. Kubernetes (`sample_logs_kubernetes.txt`)
**Best for:** Container orchestration issues

- **15 log entries** | 4 CRITICAL | 8 ERRORS | 3 WARNINGS
- **Categories:** Scheduling, etcd, Pods, Nodes, Storage, Networking
- **Highlights:**
  - Pod scheduling failures (insufficient memory)
  - etcd cluster unhealthy (quorum lost)
  - CrashLoopBackOff (15 restarts)
  - Node NotReady status
  - PersistentVolume in Lost state
  - Image pull authentication failures
  - CNI network plugin failures

### 3. Microservices (`sample_logs_microservices.txt`)
**Best for:** Distributed systems architecture

- **15 log entries** | 4 CRITICAL | 9 ERRORS | 2 WARNINGS
- **Categories:** Service Mesh, Message Queues, Circuit Breakers, gRPC
- **Highlights:**
  - Circuit breaker OPEN (50% failure rate)
  - Consul split-brain scenario
  - RabbitMQ queue at capacity (50K messages)
  - Distributed transaction failures
  - gRPC connection refused
  - Kafka broker down (45 under-replicated partitions)
  - Service mesh proxy OOMKilled

### 4. Cloud Infrastructure (`sample_logs_cloud_infra.txt`)
**Best for:** AWS/Azure/GCP cloud issues

- **15 log entries** | 5 CRITICAL | 8 ERRORS | 2 WARNINGS
- **Categories:** Compute, Storage, Networking, Serverless, Databases
- **Highlights:**
  - EC2 hardware failure
  - RDS storage full
  - Lambda throttling (1000 concurrent limit)
  - S3 IAM permission denied
  - CloudFront 502 errors
  - Auto-scaling capacity issues
  - DynamoDB throttling (RCU exceeded)
  - Multi-region replication lag (15 min)

### 5. Security & Compliance (`sample_logs_security.txt`)
**Best for:** Security incident response

- **15 log entries** | 7 CRITICAL | 6 ERRORS | 2 WARNINGS
- **Categories:** WAF, Authentication, Encryption, Malware, DDoS
- **Highlights:**
  - SQL injection (250 attempts/min)
  - Brute force attacks (500 failed logins)
  - Certificate expiration (3 days)
  - Malware/crypto-miner detection
  - Token leakage in logs
  - DDoS attack (50K req/sec)
  - Privilege escalation attempts
  - Data breach detection (10GB export)
  - Ransomware file encryption

### 6. Database & Data Layer (`sample_logs_database.txt`)
**Best for:** Database and data persistence issues

- **15 log entries** | 5 CRITICAL | 8 ERRORS | 2 WARNINGS
- **Categories:** SQL, NoSQL, Cache, Replication, Performance
- **Highlights:**
  - PostgreSQL replication lag (45 min)
  - MySQL deadlock detection
  - MongoDB replica set down
  - Redis master failover
  - Elasticsearch cluster RED status
  - Slow queries (45s without index)
  - Data corruption (checksum mismatch)
  - Connection pool exhaustion (200/200)
  - Cassandra node DOWN
  - DynamoDB hot partition (90% traffic)

## 🎯 How to Test Each Scenario

### Method 1: Web UI Upload
```bash
1. Open http://localhost:8502
2. Go to "Upload Logs" tab
3. Click "Upload log file"
4. Select any sample_logs_*.txt file
5. Click "🚀 Analyze Incident"
```

### Method 2: Copy-Paste
```bash
# Copy any sample file
cat sample_logs_kubernetes.txt | pbcopy  # macOS
# or
cat sample_logs_kubernetes.txt

# Then paste in the web UI text area
```

### Method 3: Command Line Test
```bash
# Display a sample
cat sample_logs_security.txt

# Count issues
grep -c "CRITICAL" sample_logs_security.txt
grep -c "ERROR" sample_logs_security.txt
```

### Method 4: Programmatic (Python)
```python
from orchestrator import IncidentOrchestrator
import asyncio

# Read sample logs
with open('sample_logs_kubernetes.txt', 'r') as f:
    logs = f.read()

# Analyze
orchestrator = IncidentOrchestrator(api_key="your-key")
results = asyncio.run(orchestrator.process_incident(logs))

print(f"Found {len(results['state']['issues_found'])} issues")
print(f"Generated {len(results['state']['remediations'])} remediations")
```

## 📊 Expected Results by Scenario

### General DevOps
- **Issues Found:** ~13-15
- **Critical:** Database corruption, OOM, Disk full
- **Remediations:** Connection pool tuning, memory scaling, disk cleanup
- **JIRA Tickets:** 3 (CRITICAL only)
- **Playbook Sections:** 7 categories

### Kubernetes
- **Issues Found:** ~12-14
- **Critical:** etcd failure, Node NotReady, Image pull, Control plane
- **Remediations:** Node recovery, storage repair, authentication fixes
- **JIRA Tickets:** 4
- **Playbook Sections:** K8s troubleshooting guide

### Microservices
- **Issues Found:** ~13-15
- **Critical:** Split-brain, Transaction failure, Kafka down, Event bus
- **Remediations:** Service mesh repair, queue management, circuit breaker reset
- **JIRA Tickets:** 4
- **Playbook Sections:** Distributed systems recovery

### Cloud Infrastructure
- **Issues Found:** ~13-15
- **Critical:** EC2 failure, Lambda throttle, Route53 down, Replication lag
- **Remediations:** Instance replacement, quota increase, failover procedures
- **JIRA Tickets:** 5
- **Playbook Sections:** Cloud provider specific

### Security
- **Issues Found:** ~13-15 (all security-related)
- **Critical:** SQL injection, DDoS, Malware, Data breach, Ransomware
- **Remediations:** Immediate containment, forensics, incident response
- **JIRA Tickets:** 7 (highest count)
- **Playbook Sections:** Security incident response

### Database
- **Issues Found:** ~13-15
- **Critical:** Replication lag, Data corruption, Redis failover, Backup failure
- **Remediations:** Replication repair, index creation, pool expansion
- **JIRA Tickets:** 5
- **Playbook Sections:** Database-specific recovery

## 🎨 Testing Tips

### For Demos
1. Start with **General DevOps** (most variety)
2. Show **Security** for dramatic effect (attacks, breaches)
3. Use **Kubernetes** for technical depth

### For Development
1. Test **Database** for performance issues
2. Use **Microservices** for distributed system testing
3. Try **Cloud** for infrastructure scenarios

### For Validation
1. Mix multiple samples together
2. Create custom scenarios
3. Test with real production logs (sanitized)

## 📈 Performance Benchmarks

| Sample File | Log Entries | Parse Time | Analysis Time | Total Time |
|-------------|-------------|------------|---------------|------------|
| General     | 20          | <1s        | 15-20s        | ~20s       |
| Kubernetes  | 15          | <1s        | 12-18s        | ~18s       |
| Microservices | 15        | <1s        | 12-18s        | ~18s       |
| Cloud       | 15          | <1s        | 12-18s        | ~18s       |
| Security    | 15          | <1s        | 15-20s        | ~20s       |
| Database    | 15          | <1s        | 12-18s        | ~18s       |

*With OpenAI API key and gpt-3.5-turbo*

## 🔄 Combining Scenarios

You can combine multiple sample files for complex scenarios:

```bash
# Combine Kubernetes + Database issues
cat sample_logs_kubernetes.txt sample_logs_database.txt > combined_test.txt

# Test in UI or via file upload
```

## 📝 Creating Custom Samples

Use this format:
```
YYYY-MM-DD HH:MM:SS SEVERITY [Component] Message with details
```

Example:
```
2024-11-07 10:30:00 ERROR [MyService] Custom error: specific details here
2024-11-07 10:30:01 CRITICAL [MyDB] Critical database issue description
```

## 🎯 Quick Test Commands

```bash
# View all samples
ls -lh sample_logs*.txt

# Preview each
for file in sample_logs*.txt; do
    echo "=== $file ==="
    head -5 $file
    echo ""
done

# Count by severity
for file in sample_logs*.txt; do
    echo "$file:"
    echo "  CRITICAL: $(grep -c CRITICAL $file)"
    echo "  ERROR: $(grep -c ERROR $file)"
    echo "  WARNING: $(grep -c WARNING $file)"
done
```

## 🎉 Ready to Test!

1. App is running at: **http://localhost:8502**
2. Choose a scenario from above
3. Upload or paste the logs
4. Watch the agents work their magic!

---

**Happy Testing! 🚀**

