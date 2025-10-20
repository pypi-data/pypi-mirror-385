from aws_cdk import (
    aws_elasticloadbalancingv2 as elbv2,
    aws_route53 as route53,
    Stack,
    Fn,
    CfnOutput,
)
from constructs import Construct


class AlbListenerRuleStack(Construct):
    """CDK Construct for creating ALB listener rules with host-based routing."""
    
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        *,
        target_group_arn: str,
        ecs_stack_name: str,
        listener_priority: int, 
        host_name: str,
        listener_type: str = "External",
        name: str = None,
        **kwargs
    ):
        """
        Initialize ALB Listener Rule Stack.
        
        Args:
            scope: The scope in which to define this construct
            construct_id: The scoped construct ID
            target_group_arn: ARN of the target group to forward traffic to
            ecs_stack_name: Name of the ECS stack that exports the ALB listener ARN
            listener_priority: Priority for the listener rule (1-50000)
            host_name: Host header value to match for routing
            listener_type: Type of listener - "External" or "Internal"
            name: Service name for Route53 record (required for Internal type)
        """
        super().__init__(scope, construct_id, **kwargs)
        self.listener_type = listener_type

        if listener_type == "Internal" and not name:
            raise ValueError("name parameter is required for Internal listener type")

        if listener_type == "Internal":
            listener_arn = Fn.import_value(
                Fn.sub("${ECSStackName}-ALBPrivateListener", {
                    "ECSStackName": ecs_stack_name
                })
            )
        else:
            listener_arn = Fn.import_value(
                Fn.sub("${ECSStackName}-ALBListenerHTTPS", {
                    "ECSStackName": ecs_stack_name
                })
            )

        # Create the listener rule
        self.listener_rule = elbv2.CfnListenerRule(
            self, "AlbListenerRule",
            listener_arn=listener_arn,
            priority=listener_priority,
            conditions=[
                elbv2.CfnListenerRule.RuleConditionProperty(
                    field="host-header",
                    values=[host_name]
                )
            ],
            actions=[
                elbv2.CfnListenerRule.ActionProperty(
                    type="forward",
                    target_group_arn=target_group_arn
                )
            ],
        )

        # Create Route53 record for Internal listener type
        if self.listener_type == "Internal":
            self._create_route53_record(ecs_stack_name, name)
        self._create_outputs()

    def _create_route53_record(self, ecs_stack_name: str, name: str):
        """Create Route53 RecordSet for Internal listener type."""
        self.record_set = route53.CfnRecordSet(
            self, "RecordSet",
            type="A",
            alias_target=route53.CfnRecordSet.AliasTargetProperty(
                dns_name=Fn.import_value(
                    Fn.sub("${ECSStackName}-ALBPrivateLoadBalancerUrl", {
                        "ECSStackName": ecs_stack_name
                    })
                ),
                hosted_zone_id=Fn.import_value(
                    Fn.sub("${ECSStackName}-ALBPrivateLoadBalancerCanonicalHostedZoneID", {
                        "ECSStackName": ecs_stack_name
                    })
                )
            ),
            hosted_zone_id=Fn.import_value(
                Fn.sub("${ECSStackName}-ALBPrivateHostedZoneId", {
                    "ECSStackName": ecs_stack_name
                })
            ),
            name=Fn.sub("${Name}.${HostedZone}", {
                "Name": name,
                "HostedZone": Fn.import_value(
                    Fn.sub("${ECSStackName}-ALBPrivateHostedZoneName", {
                        "ECSStackName": ecs_stack_name
                    })
                )
            })
        )

    def _create_outputs(self):
        """Create CloudFormation outputs."""
        CfnOutput(
            self, "AlbListenerRuleArn",
            value=self.listener_rule.ref,
            export_name=f"{Stack.of(self).stack_name}-AlbListenerRuleArn",
            description="ARN of the created ALB listener rule"
        )
        CfnOutput(
            self, "AlbListenerRulePriority",
            value=str(self.listener_rule.priority),
            export_name=f"{Stack.of(self).stack_name}-AlbListenerRulePriority",
            description="Priority of the created ALB listener rule"
        )
        
        if self.listener_type == "Internal" and hasattr(self, 'record_set'):
            CfnOutput(
                self, "Route53RecordName",
                value=self.record_set.name,
                export_name=f"{Stack.of(self).stack_name}-Route53RecordName",
                description="Name of the created Route53 record"
            )
