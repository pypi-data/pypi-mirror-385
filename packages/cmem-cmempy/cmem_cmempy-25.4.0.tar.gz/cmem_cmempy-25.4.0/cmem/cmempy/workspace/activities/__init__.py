"""API for working with activities."""

ACTIVITY_TYPE_EXECUTE_DEFAULTWORKFLOW = "ExecuteDefaultWorkflow"

ACTIVITY_TYPE_EXECUTE_LOCALWORKFLOW = "ExecuteLocalWorkflow"

ACTIVITY_TYPE_EXECUTE_WITH_PAYLOAD = "ExecuteWorkflowWithPayload"

VALID_ACTIVITY_STATUS = [
    "Idle",
    "Not executed",
    "Finished",
    "Cancelled",
    "Failed",
    "Successful",
    "Canceling",
    "Running",
    "Waiting",
]
