# AWS CDK Public Listener Role

A CDK construct for creating Application Load Balancer (ALB) listener rules that route traffic based on host headers to target groups.

## Overview

This module provides a reusable CDK construct (`AlbListenerRuleStack`) that creates ALB listener rules for routing HTTP/HTTPS traffic to specific target groups based on host header conditions.

## Features

- Creates ALB listener rules with host-based routing
- Configurable priority for rule evaluation order
- Integrates with existing ALB listeners via CloudFormation exports
- Outputs rule ARN and priority for cross-stack references

## Installation
```pip install alb-listener-rule ```
## Usage

```python
from alb_listener_rule.alb_listener_rule_stack import AlbListenerRuleStack

# Create listener rule in your CDK stack
listener_rule = AlbListenerRuleStack(
    self, "MyListenerRule",
    target_group_arn="arn:aws:elasticloadbalancing:region:account:targetgroup/my-tg/1234567890",
    ecs_stack_name="my-ecs-stack",
    listener_priority=100,
    listener_type="Internal",
    host_name="api.example.com"
)
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target_group_arn` | str | Yes | - | ARN of the target group to forward traffic to |
| `ecs_stack_name` | str | Yes | - | Name of the ECS stack that exports the ALB listener ARN |
| `listener_priority` | int | Yes | - | Priority for the listener rule (1-50000, lower = higher priority) |
| `host_name` | str | Yes | - | Host header value to match for routing |
| `listener_type` | str | No | "External" | Type of listener ("External" or "Internal") |
| `name` | str | No* | - | Service name for DNS record (*Required for Internal type) |



## Prerequisites

### For External Listeners
- An existing ALB with HTTPS listener that exports its ARN as `${ECSStackName}-ALBListenerHTTPS`
- A target group (e.g., ECS service target group) to route traffic to

### For Internal Listeners
- An existing private ALB with HTTPS listener that exports its ARN as `${ECSStackName}-ALBPrivateListener`
- The following CloudFormation exports from your ECS stack:
  - `${ECSStackName}-ALBPrivateLoadBalancerUrl`: Private ALB DNS name
  - `${ECSStackName}-ALBPrivateLoadBalancerCanonicalHostedZoneID`: Private ALB hosted zone ID
  - `${ECSStackName}-ALBPrivateHostedZoneId`: Route53 private hosted zone ID
  - `${ECSStackName}-ALBPrivateHostedZoneName`: Route53 private hosted zone name
- A target group for internal traffic routing

## Outputs

### Common Outputs (Both External and Internal)
- `${StackName}-AlbListenerRuleArn`: ARN of the created listener rule
- `${StackName}-AlbListenerRulePriority`: Priority of the created listener rule

### Additional Outputs (Internal Only)
- `${StackName}-Route53RecordName`: DNS name of the created Route53 record

## DNS Record Format

For internal listeners, DNS records are created with the following format:

- **Production** (no channel specified): `${name}.${HostedZoneName}`
- **Non-production** (channel specified): `${channel}.${name}.${HostedZoneName}`



## Example Scenarios

### Scenario 1: Public API Service
```python
# Route public traffic to an API service
api_listener_rule = AlbListenerRuleStack(
    self, "PublicAPIRule",
    target_group_arn=api_target_group.target_group_arn,
    ecs_stack_name="production-ecs",
    listener_priority=100,
    host_name="api.mycompany.com"
)
```

### Scenario 2: Internal Microservice
```python
# Route internal traffic with automatic DNS setup
internal_service_rule = AlbListenerRuleStack(
    self, "InternalServiceRule",
    target_group_arn=internal_service_target_group.target_group_arn,
    ecs_stack_name="production-ecs",
    listener_priority=150,
    host_name="user-service.internal.mycompany.com",
    listener_type="Internal",
    name="user-service"
)
```

### Scenario 3: Development Environment
```python
# Development environment with channel-based DNS
dev_service_rule = AlbListenerRuleStack(
    self, "DevServiceRule",
    target_group_arn=dev_target_group.target_group_arn,
    ecs_stack_name="dev-ecs",
    listener_priority=200,
    host_name="dev.auth-service.internal.mycompany.com",
    listener_type="Internal",
    name="auth-service",
)
```

## File Structure

```
aws_cdk-public-listener-role/
├── README.md
├── setup.py
├── alb_listener_rule/
│   ├── __init__.py
│   └── alb_listener_rule_stack.py
└── tests/
    └── test_alb_listener_rule_stack.py
```

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

## License

This project is licensed under the MIT License.
