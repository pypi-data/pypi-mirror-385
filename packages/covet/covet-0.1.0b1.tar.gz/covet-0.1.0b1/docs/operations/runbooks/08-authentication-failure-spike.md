# Runbook: Authentication Failure Spike

## Alert Details
- **Alert Name:** `AuthenticationFailureSpike`
- **Severity:** MEDIUM (Can be CRITICAL if sustained)
- **Threshold:** Auth failures > 10/sec for 3 minutes
- **SLA:** 10 minutes to investigate, 30 minutes to mitigate

## Symptoms
- High rate of authentication failures
- Possible brute force attack
- Legitimate users unable to login
- Account lockouts

## Investigation
```bash
# Check failure rate
curl 'http://localhost:9090/api/v1/query?query=rate(covet_app_auth_failures_total[5m])*60'

# Check failure reasons
curl 'http://localhost:9090/api/v1/query?query=sum(rate(covet_app_auth_failures_total[5m]))by(reason)'

# Check source IPs
docker logs covetpy-app | grep "Auth failed" | awk '{print $NF}' | sort | uniq -c | sort -rn | head -20

# Check for suspicious patterns
docker logs covetpy-app | grep "Auth failed" | tail -100
```

## Resolution

### If Brute Force Attack
```bash
# 1. Block attacking IPs
# Add to firewall/WAF
iptables -A INPUT -s ATTACKER_IP -j DROP

# 2. Enable rate limiting
# Update application config
RATE_LIMIT_AUTH=10  # 10 attempts per minute

# 3. Enable CAPTCHA
# Deploy config with CAPTCHA enabled

# 4. Notify security team
# Slack: #security-alerts
```

### If Configuration Issue
```bash
# Check authentication service
curl http://localhost:8000/health | jq '.checks.auth'

# Verify JWT secrets
docker exec covetpy-app env | grep JWT_SECRET

# Check Redis (session store)
docker exec redis redis-cli PING
```

### If User Error
```bash
# Check for password expiration events
# Check for recent password policy changes
# Send communication to users
```

## Immediate Actions
1. **Monitor attack pattern**
2. **Block malicious IPs** at firewall/WAF level
3. **Enable additional authentication controls**
   - Rate limiting
   - CAPTCHA
   - Account lockout
4. **Notify security team** if attack is sophisticated

## Prevention
- Implement progressive delays on failed attempts
- Use CAPTCHA after 3 failed attempts
- Monitor for distributed attacks
- Implement account lockout policies
- Alert security team on suspicious patterns

## Verification
```bash
# Verify auth failure rate normalized
curl 'http://localhost:9090/api/v1/query?query=rate(covet_app_auth_failures_total[5m])*60'
# Should be < 1/sec for normal operations

# Verify legitimate users can login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password"}'
```

## Escalation
**Security Team**
- Slack: `#security-alerts`
- Email: `security@covetpy.io`
- Phone: +1-XXX-XXX-XXXX (for active attacks)

**Escalate immediately if:**
- Attack persists > 15 minutes
- Successful breaches detected
- Distributed attack across many IPs
- Credential stuffing patterns observed

## Post-Incident
1. **Security Review**
   - Analyze attack patterns
   - Review affected accounts
   - Check for any successful breaches

2. **Enhance Defenses**
   - Implement IP reputation checking
   - Add geographic rate limiting
   - Enhance monitoring and alerting
   - Review password policies

3. **Communication**
   - Notify affected users if needed
   - Document attack patterns
   - Share IOCs with security community

## References
- [Security Dashboard](http://localhost:3000/d/covetpy-security)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
