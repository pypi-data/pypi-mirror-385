import pytest
from aws_cdk import App, Stack
from aws_cdk.assertions import Template, Match
from alb_listener_rule import AlbListenerRuleStack


def test_alb_listener_rule_creation():
    """Test that AlbListenerRuleStack can be created with required parameters."""
    app = App()
    stack = Stack(app, "TestStack")
    
    listener_rule = AlbListenerRuleStack(
        stack, "TestListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=100,
        host_name="api.example.com",
        listener_type="External"
    )
    
    # Test that the construct was created successfully
    assert listener_rule is not None
    assert listener_rule.node.id == "TestListenerRule"
    assert listener_rule.listener_rule is not None
    assert listener_rule.listener_rule.priority == 100


def test_alb_listener_rule_template():
    """Test that the CloudFormation template contains the expected resources."""
    app = App()
    stack = Stack(app, "TestStack")
    
    AlbListenerRuleStack(
        stack, "TestListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=100,
        host_name="api.example.com"
    )
    
    # Generate CloudFormation template
    template = Template.from_stack(stack)
    
    # Check that a listener rule is created
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::ListenerRule", {
        "Priority": 100,
        "Conditions": [
            {
                "Field": "host-header",
                "Values": ["api.example.com"]
            }
        ]
    })
    
    # Check that outputs are created - look for any outputs with these descriptions
    template_json = template.to_json()
    outputs = template_json.get("Outputs", {})
    
    # Find outputs by description
    arn_output_found = False
    priority_output_found = False
    
    for output_key, output_value in outputs.items():
        if output_value.get("Description") == "ARN of the created ALB listener rule":
            arn_output_found = True
        elif output_value.get("Description") == "Priority of the created ALB listener rule":
            priority_output_found = True
    
    assert arn_output_found, "ALB listener rule ARN output not found"
    assert priority_output_found, "ALB listener rule priority output not found"


def test_alb_listener_rule_template_comprehensive():
    """Test the complete CloudFormation template structure."""
    app = App()
    stack = Stack(app, "TestStack")
    
    AlbListenerRuleStack(
        stack, "TestListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=100,
        host_name="api.example.com"
    )
    
    template = Template.from_stack(stack)
    
    # Verify the listener rule has correct properties
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::ListenerRule", {
        "ListenerArn": {
            "Fn::ImportValue": {
                "Fn::Sub": [
                    "${ECSStackName}-ALBListenerHTTPS",
                    {
                        "ECSStackName": "test-ecs-stack"
                    }
                ]
            }
        },
        "Priority": 100,
        "Conditions": [
            {
                "Field": "host-header",
                "Values": ["api.example.com"]
            }
        ],
        "Actions": [
            {
                "Type": "forward",
                "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890"
            }
        ]
    })
    
    # Count resources to ensure we have exactly what we expect
    template.resource_count_is("AWS::ElasticLoadBalancingV2::ListenerRule", 1)


def test_alb_listener_rule_with_different_host():
    """Test that the construct works with different host names."""
    app = App()
    stack = Stack(app, "TestStack")
    
    listener_rule = AlbListenerRuleStack(
        stack, "TestListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=200,
        host_name="www.example.com"
    )
    
    template = Template.from_stack(stack)
    
    # Verify the host header condition
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::ListenerRule", {
        "Priority": 200,
        "Conditions": [
            {
                "Field": "host-header",
                "Values": ["www.example.com"]
            }
        ]
    })


def test_multiple_listener_rules():
    """Test that multiple listener rules can be created in the same stack."""
    app = App()
    stack = Stack(app, "TestStack")
    
    # Create two different listener rules
    AlbListenerRuleStack(
        stack, "ApiListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/api-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=100,
        host_name="api.example.com"
    )
    
    AlbListenerRuleStack(
        stack, "WebListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/web-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=200,
        host_name="www.example.com"
    )
    
    template = Template.from_stack(stack)
    
    # Should have exactly 2 listener rules
    template.resource_count_is("AWS::ElasticLoadBalancingV2::ListenerRule", 2)
    
    # Verify both rules exist with different priorities
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::ListenerRule", {
        "Priority": 100
    })
    
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::ListenerRule", {
        "Priority": 200
    })


def test_internal_listener_rule_creation():
    """Test that AlbListenerRuleStack can be created with Internal listener type."""
    app = App()
    stack = Stack(app, "TestStack")
    
    listener_rule = AlbListenerRuleStack(
        stack, "TestInternalListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=100,
        host_name="api.internal.example.com",
        listener_type="Internal",
        name="api"
    )
    
    # Test that the construct was created successfully
    assert listener_rule is not None
    assert listener_rule.listener_type == "Internal"
    assert hasattr(listener_rule, 'record_set')


def test_internal_listener_rule_template():
    """Test that Internal listener rule creates both listener rule and Route53 record."""
    app = App()
    stack = Stack(app, "TestStack")
    
    AlbListenerRuleStack(
        stack, "TestInternalListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=100,
        host_name="api.internal.example.com",
        listener_type="Internal",
        name="api"
    )
    
    template = Template.from_stack(stack)
    
    # Check that a listener rule is created with Internal listener ARN
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::ListenerRule", {
        "ListenerArn": {
            "Fn::ImportValue": {
                "Fn::Sub": [
                    "${ECSStackName}-ALBPrivateListener",
                    {
                        "ECSStackName": "test-ecs-stack"
                    }
                ]
            }
        },
        "Priority": 100
    })
    
    # Check that Route53 RecordSet is created
    template.has_resource_properties("AWS::Route53::RecordSet", {
        "Type": "A",
        "AliasTarget": {
            "DNSName": {
                "Fn::ImportValue": {
                    "Fn::Sub": [
                        "${ECSStackName}-ALBPrivateLoadBalancerUrl",
                        {
                            "ECSStackName": "test-ecs-stack"
                        }
                    ]
                }
            },
            "HostedZoneId": {
                "Fn::ImportValue": {
                    "Fn::Sub": [
                        "${ECSStackName}-ALBPrivateLoadBalancerCanonicalHostedZoneID",
                        {
                            "ECSStackName": "test-ecs-stack"
                        }
                    ]
                }
            }
        },
        "HostedZoneId": {
            "Fn::ImportValue": {
                "Fn::Sub": [
                    "${ECSStackName}-ALBPrivateHostedZoneId",
                    {
                        "ECSStackName": "test-ecs-stack"
                    }
                ]
            }
        }
    })
    
    # Check additional output for Route53 record is created
    template_json = template.to_json()
    outputs = template_json.get("Outputs", {})
    
    # Find Route53 record output by description
    route53_output_found = False
    
    for output_key, output_value in outputs.items():
        if output_value.get("Description") == "Name of the created Route53 record":
            route53_output_found = True
            break
    
    assert route53_output_found, "Route53 record name output not found"


def test_internal_listener_rule_without_name_raises_error():
    """Test that Internal listener rule without name parameter raises ValueError."""
    app = App()
    stack = Stack(app, "TestStack")
    
    with pytest.raises(ValueError, match="name parameter is required for Internal listener type"):
        AlbListenerRuleStack(
            stack, "TestInternalListenerRule",
            target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
            ecs_stack_name="test-ecs-stack",
            listener_priority=100,
            host_name="api.internal.example.com",
            listener_type="Internal"
        )


def test_external_vs_internal_listener_arns():
    """Test that External and Internal listener types use different listener ARNs."""
    app = App()
    stack = Stack(app, "TestStack")
    
    # Create External listener rule
    AlbListenerRuleStack(
        stack, "ExternalListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=100,
        host_name="api.example.com",
        listener_type="External"
    )
    
    # Create Internal listener rule
    AlbListenerRuleStack(
        stack, "InternalListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=200,
        host_name="api.internal.example.com",
        listener_type="Internal",
        name="api"
    )
    
    template = Template.from_stack(stack)
    
    # Should have 2 listener rules and 1 Route53 record
    template.resource_count_is("AWS::ElasticLoadBalancingV2::ListenerRule", 2)
    template.resource_count_is("AWS::Route53::RecordSet", 1)
    
    # Check External listener ARN
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::ListenerRule", {
        "ListenerArn": {
            "Fn::ImportValue": {
                "Fn::Sub": [
                    "${ECSStackName}-ALBListenerHTTPS",
                    {
                        "ECSStackName": "test-ecs-stack"
                    }
                ]
            }
        }
    })
    
    # Check Internal listener ARN
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::ListenerRule", {
        "ListenerArn": {
            "Fn::ImportValue": {
                "Fn::Sub": [
                    "${ECSStackName}-ALBPrivateListener",
                    {
                        "ECSStackName": "test-ecs-stack"
                    }
                ]
            }
        }
    })


def test_route53_record_name_format():
    """Test Route53 record name format: name.hostedzone."""
    app = App()
    stack = Stack(app, "TestStack")
    
    AlbListenerRuleStack(
        stack, "TestInternalListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=100,
        host_name="api.internal.example.com",
        listener_type="Internal",
        name="api"
    )
    
    template = Template.from_stack(stack)
    
    # Check Route53 record name uses format: ${name}.${HostedZone}
    template.has_resource_properties("AWS::Route53::RecordSet", {
        "Name": {
            "Fn::Sub": [
                "${Name}.${HostedZone}",
                {
                    "Name": "api",
                    "HostedZone": {
                        "Fn::ImportValue": {
                            "Fn::Sub": [
                                "${ECSStackName}-ALBPrivateHostedZoneName",
                                {
                                    "ECSStackName": "test-ecs-stack"
                                }
                            ]
                        }
                    }
                }
            ]
        }
    })


def test_route53_record_basic_properties():
    """Test basic Route53 record properties."""
    app = App()
    stack = Stack(app, "TestStack")
    
    AlbListenerRuleStack(
        stack, "TestInternalListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=100,
        host_name="api.internal.example.com",
        listener_type="Internal",
        name="api"
    )
    
    template = Template.from_stack(stack)
    
    # Just check that a Route53 record exists with basic properties
    template.has_resource_properties("AWS::Route53::RecordSet", {
        "Type": "A"
    })
    
    # Verify the record has the correct alias target structure
    template.has_resource_properties("AWS::Route53::RecordSet", 
        Match.object_like({
            "AliasTarget": Match.object_like({
                "DNSName": Match.any_value(),
                "HostedZoneId": Match.any_value()
            }),
            "HostedZoneId": Match.any_value(),
            "Name": Match.any_value(),
            "Type": "A"
        })
    )
