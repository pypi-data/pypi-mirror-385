# DRI Alarm Reporter

CloudWatch Alarm Daily Reporter with AI-powered root cause analysis using Claude.

Analyzes AWS CloudWatch alarms across multiple regions and correlates them with Lambda function logs. Generates Markdown reports compatible with Confluence DRI Diary pages.

## Features

- 🌏 **Multi-Region Support**: Queries 7 AWS regions across 3 production rings
- 🤖 **AI-Powered Analysis**: Optional Claude API integration for intelligent root cause analysis
- 📊 **Confluence-Ready**: Generates Markdown tables formatted for Confluence DRI pages
- 🔍 **Deep Log Analysis**: Collects complete Lambda execution logs for timeout errors
- ⏰ **Timezone-Aware**: Uses Taiwan time (Asia/Taipei) for report generation
- 🔗 **CloudWatch Links**: Includes direct links to alarms and log groups

## Installation

```bash
pip install dri-alarm-reporter
```

## Quick Start

### Basic Usage

```bash
# Generate report for today
dri-report

# Generate report for specific date
dri-report 2025-10-17
```

### AWS Credentials

Configure AWS credentials using any standard method:

```bash
# AWS CLI
aws configure

# Or environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=ap-northeast-1
```

### AI Analysis (Optional)

To enable AI-powered root cause analysis, create `~/.claude/settings.json`:
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://your-proxy-url",
    "ANTHROPIC_AUTH_TOKEN": "your-token",
    "ANTHROPIC_MODEL": "claude-4.5-sonnet"
  }
}
```

Without this configuration, the tool generates basic log reports without AI analysis.

## Output Format

Reports are saved to `reports/YYYYMMDD.md` with Confluence-compatible tables:

```markdown
| Alarm | Service | Status | Description | Note |
|-------|---------|--------|-------------|------|
| [production-service-5XX-Error](cloudwatch-link) | service-name | ALARM→OK | AI root cause analysis | AI recommendations |
```

## Monitored Regions

- **Ring1**: ap-southeast-2, ap-southeast-1
- **Ring2**: us-east-1, ap-south-1
- **Ring3**: ap-northeast-1, eu-central-1, me-central-1

## Architecture

The tool performs the following workflow:

1. Queries CloudWatch alarms with state changes during Taiwan working hours (9:00-18:00)
2. Extracts Lambda function names from alarm dimensions
3. Retrieves correlated error logs from CloudWatch Logs
4. For timeout errors: Collects complete execution logs (35s before + 5s after)
5. Sends logs to Claude API for root cause analysis (if configured)
6. Generates Markdown report with findings and recommendations

## Advanced Usage

### Custom Regions

```python
from alarm_reporter import AlarmReporter

# Query specific regions only
reporter = AlarmReporter(regions=['ap-northeast-1', 'us-east-1'])
reporter.run_daily_report()
```

### Programmatic Access

```python
from alarm_reporter import AlarmReporter
from datetime import datetime
from zoneinfo import ZoneInfo

reporter = AlarmReporter()

# Generate report for specific date
specific_date = datetime(2025, 10, 17, tzinfo=ZoneInfo('Asia/Taipei'))
report = reporter.run_daily_report(specific_date)
print(report)
```

## Supported Alarm Types

- **Lambda Errors**: Standard AWS/Lambda namespace alarms
- **Custom Metrics**: `vcs-inventory-production-*-logErrors`
- **Container Security**: `container-security/production` with LogErrorCount metrics
- **API Gateway**: 5XX error alarms with request correlation

## Development

```bash
# Clone repository
git clone https://github.com/trendmicro/dri-report.git
cd dri-report

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues or questions, please file an issue at: https://github.com/trendmicro/dri-report/issues
