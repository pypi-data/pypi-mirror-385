# log_group.py

import pulumi


def log_group(
    scope: Construct, name: str, retention_in_days: int = 3
) -> CloudwatchLogGroup:
    """
    Creates a CloudWatch log group.

    Args:
        name (str): The name of the log group.
        retention_in_days (int, optional): Default retention period in days. Defaults to 3 days.

    Returns:
        CloudwatchLogGroup: The created CloudWatch log group.
    """
    return pulumi.CloudwatchLogGroup(
        scope,
        make_id(scope, name),
        name=f"{scope.config.get('environment')}/{scope.config.get('product')}/{scope.config.get('domain')}/{name}",
        retention_in_days=retention_in_days,
        tags=make_tags(scope, name),
    )
