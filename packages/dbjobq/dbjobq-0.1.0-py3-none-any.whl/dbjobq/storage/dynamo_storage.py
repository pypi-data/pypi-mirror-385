import asyncio
import time
import uuid
from decimal import Decimal
from typing import Any, Optional

import aioboto3
from boto3.dynamodb.conditions import Attr, Key

from ..models import Job as JobModel
from ..models import Schedule as ScheduleModel
from .base import BaseStorage


def python_to_dynamodb(obj: Any) -> Any:
    """Convert Python types to DynamoDB-compatible types."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: python_to_dynamodb(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [python_to_dynamodb(item) for item in obj]
    return obj


def dynamodb_to_python(obj: Any) -> Any:
    """Convert DynamoDB Decimal types to Python types."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    elif isinstance(obj, dict):
        return {k: dynamodb_to_python(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [dynamodb_to_python(item) for item in obj]
    return obj


class DynamoStorage(BaseStorage):
    """
    DynamoDB storage backend for jobs and schedules.

    Uses a single table with composite key:
    - PK (partition key): record_type (e.g., "job" or "schedule")
    - SK (sort key): id (unique identifier)

    GSIs for efficient queries:
    - jobs-status-priority-index: status (PK), priority_execute_at (SK)
    - schedules-enabled-nextrun-index: enabled (PK), next_run (SK)
    """

    def __init__(
        self,
        table_name: str = "dbjobq",
        region_name: str = "us-east-1",
        endpoint_url: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ) -> None:
        self.table_name = table_name
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.session = aioboto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        self._resource = None

    async def initialize(self) -> None:
        """Initialize DynamoDB table with GSIs if not exists."""
        self._resource = self.session.resource("dynamodb", endpoint_url=self.endpoint_url)
        async with self._resource as dynamodb:
            try:
                table = await dynamodb.Table(self.table_name)
                await table.load()
            except Exception:
                # Create table with composite key and GSIs
                await dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {"AttributeName": "PK", "KeyType": "HASH"},
                        {"AttributeName": "SK", "KeyType": "RANGE"},
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": "PK", "AttributeType": "S"},
                        {"AttributeName": "SK", "AttributeType": "S"},
                        {"AttributeName": "status", "AttributeType": "S"},
                        {"AttributeName": "priority_execute_at", "AttributeType": "S"},
                        {"AttributeName": "enabled", "AttributeType": "S"},
                        {"AttributeName": "next_run", "AttributeType": "N"},
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            "IndexName": "jobs-status-priority-index",
                            "KeySchema": [
                                {"AttributeName": "status", "KeyType": "HASH"},
                                {"AttributeName": "priority_execute_at", "KeyType": "RANGE"},
                            ],
                            "Projection": {"ProjectionType": "ALL"},
                            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                        },
                        {
                            "IndexName": "schedules-enabled-nextrun-index",
                            "KeySchema": [
                                {"AttributeName": "enabled", "KeyType": "HASH"},
                                {"AttributeName": "next_run", "KeyType": "RANGE"},
                            ],
                            "Projection": {"ProjectionType": "ALL"},
                            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                        },
                    ],
                    BillingMode="PAY_PER_REQUEST",
                )
                # Wait for table creation
                table = await dynamodb.Table(self.table_name)
                while True:
                    await table.reload()
                    if table.table_status == "ACTIVE":
                        break
                    await asyncio.sleep(1)

    async def close(self) -> None:
        """Close DynamoDB connection."""
        if self._resource:
            await self._resource.__aexit__(None, None, None)

    async def enqueue(
        self,
        job_type: str,
        job_data: dict,
        priority: int = 0,
        execute_at: Optional[float] = None,
        max_retries: int = 3,
    ) -> str:
        """Enqueue a job."""
        job_id = str(uuid.uuid4())
        now = time.time()
        execute_at = execute_at or now

        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)
            await table.put_item(
                Item=python_to_dynamodb(
                    {
                        "PK": "job",
                        "SK": job_id,
                        "id": job_id,
                        "type": job_type,
                        "data": job_data,
                        "status": "pending",
                        "priority": priority,
                        "execute_at": execute_at,
                        "created_at": now,
                        "updated_at": now,
                        "attempts": 0,
                        "max_retries": max_retries,
                        "priority_execute_at": f"{priority:010d}_{execute_at}",
                    }
                )
            )
        return job_id

    async def dequeue(self) -> Optional[JobModel]:
        """Dequeue a job using GSI for efficient query."""
        now = time.time()

        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)

            response = await table.query(
                IndexName="jobs-status-priority-index",
                KeyConditionExpression=Key("status").eq("pending"),
                FilterExpression=Attr("execute_at").lte(Decimal(str(now))),
                Limit=10,
                ScanIndexForward=True,
            )

            if not response.get("Items"):
                return None

            for item in response["Items"]:
                try:
                    await table.update_item(
                        Key={"PK": "job", "SK": item["SK"]},
                        UpdateExpression="SET #status = :running, updated_at = :now, priority_execute_at = :new_sort",
                        ConditionExpression="#status = :pending",
                        ExpressionAttributeNames={"#status": "status"},
                        ExpressionAttributeValues={
                            ":running": "running",
                            ":pending": "pending",
                            ":now": Decimal(str(now)),
                            ":new_sort": f"running_{now}",
                        },
                    )

                    item_data = dynamodb_to_python(item)
                    return JobModel(
                        id=item_data["id"],
                        type=item_data["type"],
                        data=item_data["data"],
                        status="running",
                        created_at=item_data.get("created_at"),
                        updated_at=now,
                        priority=item_data.get("priority", 0),
                        execute_at=item_data.get("execute_at"),
                        attempts=item_data.get("attempts", 0),
                        max_retries=item_data.get("max_retries", 3),
                    )
                except Exception:  # noqa: S112
                    continue

            return None

    async def complete(self, job_id: str) -> None:
        """Mark a job as completed."""
        now = time.time()
        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)
            await table.update_item(
                Key={"PK": "job", "SK": job_id},
                UpdateExpression="SET #status = :completed, updated_at = :now",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":completed": "completed",
                    ":now": Decimal(str(now)),
                },
            )

    async def fail(self, job_id: str, error: str) -> None:
        """Mark a job as failed."""
        now = time.time()
        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)
            await table.update_item(
                Key={"PK": "job", "SK": job_id},
                UpdateExpression="SET #status = :failed, #error = :error, updated_at = :now",
                ExpressionAttributeNames={"#status": "status", "#error": "error"},
                ExpressionAttributeValues={
                    ":failed": "failed",
                    ":error": error,
                    ":now": Decimal(str(now)),
                },
            )

    async def get_job(self, job_id: str) -> Optional[JobModel]:
        """Get a job by ID."""
        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)
            response = await table.get_item(Key={"PK": "job", "SK": job_id})

            if "Item" not in response:
                return None

            item = dynamodb_to_python(response["Item"])
            return JobModel(
                id=item["id"],
                type=item["type"],
                data=item["data"],
                status=item["status"],
                created_at=item.get("created_at"),
                updated_at=item.get("updated_at"),
                error=item.get("error"),
                priority=item.get("priority", 0),
                execute_at=item.get("execute_at"),
                attempts=item.get("attempts", 0),
                max_retries=item.get("max_retries", 3),
            )

    async def list_jobs(self, status: Optional[str] = None, limit: Optional[int] = None) -> list[JobModel]:
        """List jobs."""
        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)

            if status:
                query_kwargs = {
                    "IndexName": "jobs-status-priority-index",
                    "KeyConditionExpression": Key("status").eq(status),
                }
                if limit:
                    query_kwargs["Limit"] = limit
                response = await table.query(**query_kwargs)
            else:
                query_kwargs = {"FilterExpression": Attr("PK").eq("job")}
                if limit:
                    query_kwargs["Limit"] = limit
                response = await table.scan(**query_kwargs)

            jobs = []
            for item in response.get("Items", []):
                item_data = dynamodb_to_python(item)
                jobs.append(
                    JobModel(
                        id=item_data["id"],
                        type=item_data["type"],
                        data=item_data["data"],
                        status=item_data["status"],
                        created_at=item_data.get("created_at"),
                        updated_at=item_data.get("updated_at"),
                        error=item_data.get("error"),
                        priority=item_data.get("priority", 0),
                        execute_at=item_data.get("execute_at"),
                        attempts=item_data.get("attempts", 0),
                        max_retries=item_data.get("max_retries", 3),
                    )
                )
            return jobs

    async def retry_job(self, job_id: str, error: str, delay: float) -> None:
        """Retry a failed job with exponential backoff.

        Args:
            job_id (str): The ID of the job to retry.
            error (str): The error message from the failed attempt.
            delay (float): Delay in seconds before retry.
        """
        now = time.time()
        execute_at = now + delay

        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)

            response = await table.get_item(Key={"PK": "job", "SK": job_id})
            if "Item" not in response:
                return

            item = dynamodb_to_python(response["Item"])
            attempts = item.get("attempts", 0)
            max_retries = item.get("max_retries", 3)

            if attempts >= max_retries:
                return

            priority = item.get("priority", 0)
            await table.update_item(
                Key={"PK": "job", "SK": job_id},
                UpdateExpression="SET #status = :pending, attempts = :attempts, #error = :error, updated_at = :now, execute_at = :execute_at, priority_execute_at = :sort_key",
                ExpressionAttributeNames={"#status": "status", "#error": "error"},
                ExpressionAttributeValues={
                    ":pending": "pending",
                    ":attempts": Decimal(str(attempts + 1)),
                    ":error": error,
                    ":now": Decimal(str(now)),
                    ":execute_at": Decimal(str(execute_at)),
                    ":sort_key": f"{priority:010d}_{execute_at}",
                },
            )

    async def create_schedule(  # noqa: PLR0913
        self,
        job_type: str,
        job_data: dict,
        schedule_type: str,
        schedule_expression: str,
        next_run: float,
        enabled: bool = True,
        max_retries: int = 3,
        priority: int = 0,
    ) -> str:
        """Create a new schedule."""
        schedule_id = str(uuid.uuid4())
        now = time.time()

        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)
            await table.put_item(
                Item=python_to_dynamodb(
                    {
                        "PK": "schedule",
                        "SK": schedule_id,
                        "id": schedule_id,
                        "job_type": job_type,
                        "job_data": job_data,
                        "schedule_type": schedule_type,
                        "schedule_expression": schedule_expression,
                        "next_run": next_run,
                        "last_run": None,
                        "enabled": "true" if enabled else "false",
                        "max_retries": max_retries,
                        "priority": priority,
                        "created_at": now,
                    }
                )
            )
        return schedule_id

    async def get_due_schedules(self, current_time: float) -> list[ScheduleModel]:
        """Get all enabled schedules that are due."""
        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)

            response = await table.query(
                IndexName="schedules-enabled-nextrun-index",
                KeyConditionExpression=Key("enabled").eq("true") & Key("next_run").lte(Decimal(str(current_time))),
            )

            schedules = []
            for item in response.get("Items", []):
                item_data = dynamodb_to_python(item)
                schedules.append(
                    ScheduleModel(
                        id=item_data["id"],
                        job_type=item_data["job_type"],
                        job_data=item_data["job_data"],
                        schedule_type=item_data["schedule_type"],
                        schedule_expression=item_data["schedule_expression"],
                        next_run=item_data["next_run"],
                        last_run=item_data.get("last_run"),
                        enabled=item_data["enabled"] == "true",
                        max_retries=item_data.get("max_retries", 3),
                        priority=item.get("priority", 0),
                    )
                )
            return schedules

    async def update_schedule_next_run(self, schedule_id: str, next_run: float, last_run: float) -> None:
        """Update schedule next_run and last_run."""
        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)
            await table.update_item(
                Key={"PK": "schedule", "SK": schedule_id},
                UpdateExpression="SET next_run = :next_run, last_run = :last_run",
                ExpressionAttributeValues={
                    ":next_run": Decimal(str(next_run)),
                    ":last_run": Decimal(str(last_run)),
                },
            )

    async def get_schedule(self, schedule_id: str) -> Optional[ScheduleModel]:
        """Get a schedule by ID."""
        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)
            response = await table.get_item(Key={"PK": "schedule", "SK": schedule_id})

            if "Item" not in response:
                return None

            item = dynamodb_to_python(response["Item"])
            return ScheduleModel(
                id=item["id"],
                job_type=item["job_type"],
                job_data=item["job_data"],
                schedule_type=item["schedule_type"],
                schedule_expression=item["schedule_expression"],
                next_run=item["next_run"],
                last_run=item.get("last_run"),
                enabled=item["enabled"] == "true",
                max_retries=item.get("max_retries", 3),
                priority=item.get("priority", 0),
            )

    async def list_schedules(self, enabled: Optional[bool] = None) -> list[ScheduleModel]:
        """List all schedules."""
        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)

            if enabled is not None:
                response = await table.query(
                    IndexName="schedules-enabled-nextrun-index",
                    KeyConditionExpression=Key("enabled").eq("true" if enabled else "false"),
                )
            else:
                response = await table.scan(FilterExpression=Attr("PK").eq("schedule"))

            schedules = []
            for item in response.get("Items", []):
                item_data = dynamodb_to_python(item)
                schedules.append(
                    ScheduleModel(
                        id=item_data["id"],
                        job_type=item_data["job_type"],
                        job_data=item_data["job_data"],
                        schedule_type=item_data["schedule_type"],
                        schedule_expression=item_data["schedule_expression"],
                        next_run=item_data["next_run"],
                        last_run=item_data.get("last_run"),
                        enabled=item["enabled"] == "true",
                        max_retries=item.get("max_retries", 3),
                        priority=item.get("priority", 0),
                    )
                )
            return schedules

    async def delete_schedule(self, schedule_id: str) -> None:
        """Delete a schedule."""
        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)
            await table.delete_item(Key={"PK": "schedule", "SK": schedule_id})

    async def enable_schedule(self, schedule_id: str, enabled: bool) -> None:
        """Enable or disable a schedule."""
        async with self._resource as dynamodb:
            table = await dynamodb.Table(self.table_name)
            await table.update_item(
                Key={"PK": "schedule", "SK": schedule_id},
                UpdateExpression="SET enabled = :enabled",
                ExpressionAttributeValues={":enabled": "true" if enabled else "false"},
            )
