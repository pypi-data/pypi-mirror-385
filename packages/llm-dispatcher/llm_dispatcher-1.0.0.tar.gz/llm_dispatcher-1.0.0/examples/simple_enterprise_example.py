"""
Simple Enterprise Example for LLM-Dispatcher.

This example demonstrates basic enterprise features integration with LLM switching.
"""

import asyncio
import os
from datetime import datetime

from llm_dispatcher import LLMSwitch, TaskType, llm_dispatcher
from llm_dispatcher.enterprise import (
    SecurityManager,
    AuditLogger,
    ComplianceManager,
    UserManager,
)


async def simple_enterprise_example():
    """Simple enterprise example with LLM switching."""

    print("=== Simple Enterprise LLM-Dispatcher Example ===\n")

    # 1. Initialize enterprise components
    print("1. Initializing enterprise components...")

    security_manager = SecurityManager(
        encryption_enabled=True, audit_logging=True, compliance_mode="SOC2"
    )

    audit_logger = AuditLogger(
        log_level="detailed", retention_period=2555, compliance_mode="SOC2"
    )

    compliance_manager = ComplianceManager(
        frameworks=["SOC2", "GDPR"], continuous_monitoring=True
    )

    user_manager = UserManager(
        authentication_method="local",
        mfa_required=False,  # Simplified for demo
        password_policy="basic",
    )

    print("✓ Enterprise components initialized\n")

    # 2. Create enterprise LLM switch
    print("2. Creating enterprise LLM switch...")

    enterprise_switch = LLMSwitch(
        providers={
            "openai": {"api_key": os.getenv("OPENAI_API_KEY", "sk-test")},
            "anthropic": {"api_key": os.getenv("ANTHROPIC_API_KEY", "sk-ant-test")},
            "google": {"api_key": os.getenv("GOOGLE_API_KEY", "test")},
        },
        config={
            "enterprise_mode": True,
            "security_manager": security_manager,
            "audit_logger": audit_logger,
            "compliance_manager": compliance_manager,
            "user_manager": user_manager,
            "prefer_cost_efficiency": True,
            "max_latency_ms": 2000,
            "fallback_enabled": True,
        },
    )

    print("✓ Enterprise LLM switch created\n")

    # 3. Create a user and tenant
    print("3. Setting up user and tenant...")

    # Create a tenant
    tenant = user_manager.create_tenant(
        name="demo-enterprise",
        admin_user="admin@demo.com",
        resource_limits={
            "max_requests_per_hour": 100,
            "max_tokens_per_month": 10000,
            "max_concurrent_requests": 5,
        },
    )

    # Create a user
    user = user_manager.create_user(
        email="admin@demo.com", name="Demo Admin", tenant_id=tenant.id, role="admin"
    )

    print(f"✓ Created tenant: {tenant.name} (ID: {tenant.id})")
    print(f"✓ Created user: {user.email} (ID: {user.id})\n")

    # 4. Authenticate user
    print("4. Authenticating user...")

    auth_result = user_manager.authenticate(
        email="admin@demo.com", password="demo_password"
    )

    if auth_result.success:
        print(f"✓ User authenticated: {auth_result.user_id}")

        # Log authentication event
        await audit_logger.log_event(
            event_type="authentication",
            user_id=auth_result.user_id,
            tenant_id=auth_result.tenant_id,
            details={
                "method": "password",
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
    else:
        print(f"✗ Authentication failed: {auth_result.error}")
        return

    user_id = auth_result.user_id
    tenant_id = auth_result.tenant_id
    print()

    # 5. Generate content with enterprise security
    print("5. Generating content with enterprise security...")

    # Check user permissions
    has_permission = user_manager.check_permission(
        user_id=user_id, permission="generate_content", resource=tenant_id
    )

    if not has_permission:
        print("✗ User lacks permission to generate content")
        return

    print("✓ User has permission to generate content")

    # Check compliance
    compliance_check = await compliance_manager.check_compliance(
        user_id=user_id,
        tenant_id=tenant_id,
        data_type="generated_content",
        operation="create",
    )

    if not compliance_check.compliant:
        print(f"✗ Compliance check failed: {compliance_check.violations}")
        return

    print("✓ Compliance check passed")

    # Encrypt prompt
    prompt = "Write a brief security policy for our organization"
    encrypted_prompt = security_manager.encrypt_data(
        data=prompt, context={"user_id": user_id, "tenant_id": tenant_id}
    )

    print("✓ Prompt encrypted")

    # Generate content using enterprise switch
    @enterprise_switch.route(task_type=TaskType.TEXT_GENERATION)
    def generate_content(prompt: str) -> str:
        # In a real implementation, this would call the actual LLM
        return f"Generated security policy content for: {prompt}"

    result = generate_content(encrypted_prompt)

    # Decrypt result
    decrypted_result = security_manager.decrypt_data(
        encrypted_data=result, context={"user_id": user_id, "tenant_id": tenant_id}
    )

    print("✓ Content generated and decrypted")
    print(f"Generated content: {decrypted_result}\n")

    # Log successful generation
    await audit_logger.log_event(
        event_type="content_generation",
        user_id=user_id,
        tenant_id=tenant_id,
        details={
            "task_type": "text_generation",
            "prompt_length": len(prompt),
            "result_length": len(decrypted_result),
            "compliance_checked": True,
            "encryption_applied": True,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

    print("✓ Generation event logged")

    # 6. Get enterprise metrics
    print("6. Getting enterprise metrics...")

    # Get audit logs
    audit_logs = await audit_logger.query_logs(
        filters={
            "tenant_id": tenant_id,
            "start_date": (
                datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).isoformat(),
            "end_date": datetime.utcnow().isoformat(),
        }
    )

    # Get compliance status
    compliance_status = await compliance_manager.get_compliance_status(
        tenant_id=tenant_id, framework="SOC2"
    )

    # Get user activity
    user_activity = user_manager.get_user_activity(tenant_id=tenant_id, time_range="1d")

    print(f"✓ Audit events today: {len(audit_logs)}")
    print(f"✓ Compliance score: {compliance_status.overall_score}")
    print(f"✓ Active users: {user_activity.active_users}")
    print()

    # 7. Summary
    print("=== Enterprise Example Summary ===")
    print(f"✓ Enterprise components initialized")
    print(f"✓ User authenticated: {user_id}")
    print(f"✓ Tenant created: {tenant_id}")
    print(f"✓ Content generated with security and compliance")
    print(f"✓ Audit logging active")
    print(f"✓ Enterprise metrics collected")
    print()
    print("=== Simple Enterprise Example Completed Successfully! ===")


if __name__ == "__main__":
    asyncio.run(simple_enterprise_example())
