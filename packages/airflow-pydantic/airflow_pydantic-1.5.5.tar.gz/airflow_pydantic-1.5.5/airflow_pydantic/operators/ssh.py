from logging import getLogger
from types import FunctionType, MethodType
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import Field, TypeAdapter, field_validator, model_validator

from ..airflow import SSHHook as BaseSSHHook
from ..core import Task, TaskArgs
from ..extras import BalancerHostQueryConfiguration, Host
from ..utils import BashCommands, CallablePath, ImportPath, SSHHook, get_import_path

__all__ = (
    "SSHOperatorArgs",
    "SSHTaskArgs",
    "SSHOperator",
    "SSHTask",
)

_log = getLogger(__name__)


class SSHTaskArgs(TaskArgs):
    # ssh operator args
    # https://airflow.apache.org/docs/apache-airflow-providers-ssh/stable/_api/airflow/providers/ssh/operators/ssh/index.html
    ssh_hook: Optional[Union[SSHHook, CallablePath, BalancerHostQueryConfiguration, Host]] = Field(
        default=None, description="predefined ssh_hook to use for remote execution. Either ssh_hook or ssh_conn_id needs to be provided."
    )
    ssh_hook_host: Optional[Host] = Field(default=None, exclude=True)

    # Track source of hook in order to defer
    ssh_hook_foo: Optional[CallablePath] = Field(default=None, exclude=True)
    ssh_hook_external: Optional[bool] = Field(
        default=False, exclude=True, description="Whether to force the ssh_hook to be an external call or not. Only works when ssh_hook is a Callable"
    )

    ssh_conn_id: Optional[str] = Field(
        default=None, description="ssh connection id from airflow Connections. ssh_conn_id will be ignored if ssh_hook is provided."
    )
    remote_host: Optional[str] = Field(
        default=None,
        description="remote host to connect (templated) Nullable. If provided, it will replace the remote_host which was defined in ssh_hook or predefined in the connection of ssh_conn_id.",
    )
    command: Union[str, List[str], BashCommands] = Field(default=None, description="command to execute on remote host. (templated)")
    conn_timeout: Optional[int] = Field(
        default=None,
        description="timeout (in seconds) for maintaining the connection. The default is 10 seconds. Nullable. If provided, it will replace the conn_timeout which was predefined in the connection of ssh_conn_id.",
    )
    cmd_timeout: Optional[int] = Field(
        default=None,
        description="timeout (in seconds) for executing the command. The default is 10 seconds. Nullable, None means no timeout. If provided, it will replace the cmd_timeout which was predefined in the connection of ssh_conn_id.",
    )
    environment: Optional[Dict[str, str]] = Field(
        default=None,
        description="a dict of shell environment variables. Note that the server will reject them silently if AcceptEnv is not set in SSH config. (templated)",
    )
    get_pty: Optional[bool] = Field(
        default=None,
        description="request a pseudo-terminal from the server. Set to True to have the remote process killed upon task timeout. The default is False but note that get_pty is forced to True when the command starts with sudo.",
    )
    banner_timeout: Optional[int] = Field(default=None, description="timeout to wait for banner from the server in seconds")
    skip_on_exit_code: Optional[int] = Field(
        default=None,
        description="If command exits with this exit code, leave the task in skipped state (default: None). If set to None, any non-zero exit code will be treated as a failure.",
    )

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v
        elif isinstance(v, list) and all(isinstance(item, str) for item in v):
            return BashCommands(commands=v)
        elif isinstance(v, BashCommands):
            return v
        else:
            raise ValueError("command must be a string, list of strings, or a BashCommands model")

    @model_validator(mode="before")
    @classmethod
    def _extract_host_from_ssh_hook(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "ssh_hook" in data:
                ssh_hook = data["ssh_hook"]
                if isinstance(ssh_hook, (BalancerHostQueryConfiguration, Host)):
                    if isinstance(ssh_hook, BalancerHostQueryConfiguration):
                        # Ensure that the BalancerHostQueryConfiguration is of kind 'select'
                        if not ssh_hook.kind == "select":
                            raise ValueError("BalancerHostQueryConfiguration must be of kind 'select'")

                        # Execute the query to get the Host, just set as it will
                        # be handled by the field validator
                        data["ssh_hook"] = ssh_hook.execute()

                        # Save the host for later use
                        data["ssh_hook_host"] = data["ssh_hook"]
                    else:
                        # If it's a Host instance, set it for later use
                        data["ssh_hook_host"] = ssh_hook

                    # Override pool from host if not otherwise set
                    if data["ssh_hook_host"].pool and not data.get("pool"):
                        data["pool"] = data["ssh_hook"].pool

                if isinstance(ssh_hook, str):
                    # If ssh_hook is a string, we assume it's an import path
                    data["ssh_hook_foo"] = get_import_path(ssh_hook)

                    try:
                        data["ssh_hook"] = data["ssh_hook_foo"]()
                    except Exception:
                        # Skip, might only run in situ
                        data["ssh_hook"] = None

                if isinstance(ssh_hook, (FunctionType, MethodType)):
                    # If ssh_hook is a callable, we need to call it to get the SSHHook instance
                    data["ssh_hook_foo"] = get_import_path(ssh_hook)

                    try:
                        data["ssh_hook"] = data["ssh_hook_foo"]()
                    except Exception:
                        # Skip, might only run in situ
                        data["ssh_hook"] = None
        return data

    @field_validator("ssh_hook", mode="before")
    @classmethod
    def _validate_ssh_hook(cls, v):
        if v:
            if isinstance(v, str):
                v = get_import_path(v)

            if isinstance(v, (FunctionType, MethodType)):
                try:
                    # If it's a callable, we need to call it to get the SSHHook instance
                    v = v()
                except Exception:
                    # Skip, might only run in situ
                    _log.info("Failed to call ssh_hook callable: %s", v)
                    v = None

            try:
                if isinstance(v, BalancerHostQueryConfiguration):
                    if not v.kind == "select":
                        raise ValueError("BalancerHostQueryConfiguration must be of kind 'select'")
                    v = v.execute().hook()
                if isinstance(v, (Host,)):
                    v = v.hook()
            except Exception:
                # Skip, might only run in situ
                _log.info("Failed to execute BalancerHostQueryConfiguration or Host: %s", v)
                v = None

            if isinstance(v, dict):
                v = TypeAdapter(SSHHook).validate_python(v)
            assert v is None or isinstance(v, BaseSSHHook), f"ssh_hook must be an instance of SSHHook, got: {type(v)}"
        return v

    # @field_serializer("ssh_hook", when_used="json")
    # def _serialize_ssh_hook(self, v: Optional[BaseSSHHook]) -> Optional[Dict[str, Any]]:
    #     import pdb; pdb.set_trace()
    #     if v is None:
    #         return None
    #     return SSHHook.__get_pydantic_core_schema__().serialization.serialize_json(SSHHook, v)


# Alias
SSHOperatorArgs = SSHTaskArgs


class SSHTask(Task, SSHTaskArgs):
    operator: ImportPath = Field(default="airflow_pydantic.airflow.SSHOperator", description="airflow operator path", validate_default=True)

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: Type) -> Type:
        from airflow_pydantic.airflow import SSHOperator, _AirflowPydanticMarker

        if not isinstance(v, Type):
            raise ValueError(f"operator must be 'airflow.providers.ssh.operators.ssh.SSHOperator', got: {v}")
        if issubclass(v, _AirflowPydanticMarker):
            _log.info("SSHOperator is a marker class, returning as is")
            return v
        if not issubclass(v, SSHOperator):
            raise ValueError(f"operator must be 'airflow.providers.ssh.operators.ssh.SSHOperator', got: {v}")
        return v


# Alias
SSHOperator = SSHTask
