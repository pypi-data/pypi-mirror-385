# Code Developer Monitoring

This module provides monitoring, metrics collection, and alerting for the code_developer daemon running on GCP.

## Components

### 1. Metrics Collection (`metrics.py`)

Tracks daemon performance and costs:

- Task completion metrics
- Anthropic API usage and costs
- Duration and throughput
- Success/failure rates

**Usage:**
```python
from coffee_maker.monitoring.metrics import get_metrics_collector

collector = get_metrics_collector()

# Start tracking a task
metrics = collector.start_task("task-123", "PRIORITY 1")

# Record API calls
collector.record_api_call("task-123", tokens_input=1000, tokens_output=500, cost_usd=0.05)

# Complete task
collector.complete_task("task-123", status="completed")
```

### 2. Alerting (`alerts.py`)

Sends alerts when issues are detected:

- Daemon crashes
- High error rates
- Cost thresholds exceeded
- Low disk space

**Notification Channels:**
- Email (via SendGrid or SMTP)
- Slack webhooks
- GCP Cloud Monitoring alerts

**Configuration:**
```bash
export ALERT_EMAIL="your-email@example.com"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**Usage:**
```python
from coffee_maker.monitoring.alerts import get_alert_manager, AlertSeverity

alert_manager = get_alert_manager()

# Send alert
alert_manager.send_alert(
    title="Daemon Error",
    message="Failed to implement PRIORITY 1",
    severity=AlertSeverity.ERROR,
    metadata={"priority": "PRIORITY 1", "error": "API timeout"}
)
```

### 3. GCP Dashboards

Pre-configured Cloud Monitoring dashboards:

- **Daemon Health** (`dashboards/daemon_health.json`): Uptime, errors, latency
- **Cost Tracking** (`dashboards/cost_tracking.json`): Daily/monthly costs, API usage

**Deploy dashboards:**
```bash
gcloud monitoring dashboards create --config-from-file=coffee_maker/monitoring/dashboards/daemon_health.json
gcloud monitoring dashboards create --config-from-file=coffee_maker/monitoring/dashboards/cost_tracking.json
```

## Metrics Tracked

### Task Metrics
- `task_duration_seconds`: Time to complete each priority
- `task_status`: completed, failed, in_progress
- `tasks_completed_total`: Total completed tasks
- `tasks_failed_total`: Total failed tasks

### API Metrics
- `anthropic_api_calls_total`: Total API calls
- `anthropic_tokens_input`: Input tokens used
- `anthropic_tokens_output`: Output tokens generated
- `anthropic_cost_usd`: Cost in USD

### System Metrics
- `cpu_usage_percent`: CPU utilization
- `memory_usage_percent`: Memory utilization
- `disk_usage_percent`: Disk utilization

## Alert Rules

### Critical Alerts
- **Daemon Crash**: Daemon stopped unexpectedly
- **API Rate Limit**: Anthropic API rate limit reached

### Error Alerts
- **High Error Rate**: >10% of tasks failing
- **Task Timeout**: Task running >2 hours

### Warning Alerts
- **Cost Threshold**: Daily cost >$50 or monthly >$1500
- **Low Disk Space**: Disk usage >90%

## Integration with Daemon

The daemon automatically reports metrics during operation:

```python
# In coffee_maker/autonomous/daemon.py
from coffee_maker.monitoring import get_metrics_collector, get_alert_manager

collector = get_metrics_collector()
alert_manager = get_alert_manager()

def implement_priority(priority):
    task_id = f"priority-{priority['name']}"
    metrics = collector.start_task(task_id, priority['name'])

    try:
        # Implement priority...
        collector.complete_task(task_id, status="completed")
    except Exception as e:
        collector.complete_task(task_id, status="failed", error=str(e))
        alert_manager.send_alert(
            title=f"Failed to implement {priority['name']}",
            message=str(e),
            severity=AlertSeverity.ERROR
        )
```

## Viewing Metrics

### Via API
```bash
curl https://code-developer-xxx.run.app/api/status/metrics
```

### Via GCP Console
1. Navigate to Cloud Monitoring
2. Select "Dashboards"
3. Open "Code Developer" dashboard

### Via CLI
```bash
project-manager cloud metrics
```

## Troubleshooting

### Metrics not appearing
1. Check GCP project ID is set: `echo $GCP_PROJECT_ID`
2. Verify service account has `monitoring.metricWriter` role
3. Check logs: `project-manager cloud logs | grep metrics`

### Alerts not sending
1. Verify environment variables: `ALERT_EMAIL`, `SLACK_WEBHOOK_URL`
2. Test Slack webhook: `curl -X POST -H 'Content-type: application/json' --data '{"text":"Test"}' $SLACK_WEBHOOK_URL`
3. Check alert manager logs

## Cost Analysis

The monitoring system tracks Anthropic API costs in real-time:

- **Per-task cost**: Cost to implement each priority
- **Daily cost**: Total cost per day
- **Monthly projection**: Projected monthly cost
- **Cost per token**: Average cost per 1K tokens

**View cost report:**
```bash
project-manager cloud metrics --costs
```
