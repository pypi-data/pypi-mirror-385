from datetime import datetime, time, timedelta
from unittest.mock import patch

import pytest
from pydantic import TypeAdapter
from pytest import fixture

from airflow_pydantic import (
    BalancerConfiguration,
    BalancerHostQueryConfiguration,
    BashCommands,
    BashSensor,
    BashSensorArgs,
    BashTask,
    BashTaskArgs,
    Dag,
    DagArgs,
    Host,
    Pool,
    Port,
    PythonSensor,
    PythonSensorArgs,
    PythonTask,
    PythonTaskArgs,
    SSHTask,
    SSHTaskArgs,
    TaskArgs,
    TriggerDagRunTask,
    TriggerDagRunTaskArgs,
    Variable,
)
from airflow_pydantic.airflow import SSHHook
from airflow_pydantic.testing import pools, variables

has_supervisor = False
try:
    from airflow_supervisor import (
        ProgramConfiguration,
        SupervisorAirflowConfiguration,
        SupervisorSSHAirflowConfiguration,
        SupervisorSSHTask,
        SupervisorTask,
    )

    has_supervisor = True
except ImportError:
    ...


def foo(**kwargs): ...


def hook(**kwargs):
    return SSHHook(remote_host="test", username="test")


@fixture
def load_config():
    try:
        from airflow_config import load_config
    except ImportError:
        pytest.skip("airflow_config is not installed, skipping load_config fixture")
    return load_config


@fixture
def python_operator_args():
    return PythonTaskArgs(
        python_callable="airflow_pydantic.tests.conftest.foo",
        op_args=["test"],
        op_kwargs={"test": "test"},
        templates_dict={"test": "test"},
        templates_exts=[".sql", ".hql"],
        show_return_value_in_logs=True,
        pool=Pool(pool="test-pool-model"),
    )


@fixture
def python_sensor_args():
    return PythonSensorArgs(
        python_callable="airflow_pydantic.tests.conftest.foo",
        op_args=["test"],
        op_kwargs={"test": "test"},
    )


@fixture
def python_operator(python_operator_args):
    return PythonTask(
        task_id="test-python-operator",
        **python_operator_args.model_dump(exclude_unset=True),
    )


@fixture
def python_sensor(python_sensor_args):
    return PythonSensor(
        task_id="test-python-sensor",
        **python_sensor_args.model_dump(exclude_unset=True),
    )


@fixture
def bash_operator_args():
    return BashTaskArgs(
        bash_command="test",
        env={"test": "test"},
        append_env=True,
        pool=TypeAdapter(Pool).validate_python({"pool": "test", "slots": 5}),
        output_encoding="utf-8",
        skip_on_exit_code=99,
        cwd="test",
        output_processor="airflow_pydantic.tests.conftest.foo",
    )


@fixture
def bash_sensor_args():
    return BashSensorArgs(
        bash_command="test",
    )


@fixture
def bash_operator(bash_operator_args):
    return BashTask(
        task_id="test-bash-operator",
        **bash_operator_args.model_dump(exclude_unset=True),
    )


@fixture
def bash_sensor(bash_sensor_args):
    return BashSensor(
        task_id="test-bash-sensor",
        **bash_sensor_args.model_dump(exclude_unset=True),
    )


@fixture
def trigger_dagrun_args():
    return TriggerDagRunTaskArgs(trigger_dag_id="test_dag")


@fixture
def trigger_dagrun(trigger_dagrun_args):
    return TriggerDagRunTask(
        task_id="test-trigger-dagrun",
        **trigger_dagrun_args.model_dump(exclude_unset=True),
    )


@fixture
def ssh_operator_args():
    return SSHTaskArgs(
        ssh_conn_id="test",
        ssh_hook="airflow_pydantic.tests.conftest.hook",
        pool="blerg",
        command=["test1", "test2"],
        do_xcom_push=True,
        cmd_timeout=10,
        get_pty=True,
        environment={"test": "test"},
    )


@fixture
def ssh_operator(ssh_operator_args):
    return SSHTask(
        task_id="test-ssh-operator",
        **ssh_operator_args.model_dump(exclude_unset=True),
    )


@fixture
def balancer():
    with pools():
        return BalancerConfiguration(
            hosts=[
                Host(
                    name="test_host",
                    username="test_user",
                    password=Variable(key="VAR", deserialize_json=True),
                ),
            ]
        )


@fixture
def ssh_operator_balancer(ssh_operator_args, balancer):
    ssh_operator_args.command = BashCommands(commands=["test1", "test2"], login=True, cwd="/tmp", env={"var": "{{ ti.blerg }}"})
    with pools(), variables({"user": "test", "password": "password"}):
        return SSHTask(
            task_id="test-ssh-operator",
            **ssh_operator_args.model_dump(exclude_unset=True, exclude=["ssh_hook", "pool"]),
            ssh_hook=BalancerHostQueryConfiguration(
                kind="select",
                balancer=balancer,
                name="test_host",
            ),
        )


@fixture
def ssh_operator_balancer_template(ssh_operator_balancer):
    with pools(), variables({"user": "test", "password": "password"}):
        return SSHTask(
            task_id="test-ssh-operator",
            template=ssh_operator_balancer,
        )


@fixture
def supervisor_cfg():
    if not has_supervisor:
        pytest.skip("airflow_supervisor is not installed, skipping supervisor fixtures")
    with (
        patch("supervisor_pydantic.config.supervisor.gettempdir") as p1,
    ):
        path = "/an/arbitrary/path"
        p1.return_value = str(path)
        cfg = SupervisorAirflowConfiguration(
            port="*:1234",
            endtime=time(23, 59),
            working_dir=path,
            path=path,
            program={
                "test": ProgramConfiguration(
                    command="bash -c 'sleep 60; exit 1'",
                )
            },
        )
        yield cfg


@fixture
def supervisor_ssh_cfg():
    if not has_supervisor:
        pytest.skip("airflow_supervisor is not installed, skipping supervisor fixtures")
    with (
        patch("supervisor_pydantic.config.supervisor.gettempdir") as p1,
    ):
        path = "/an/arbitrary/path"
        p1.return_value = str(path)
        cfg = SupervisorSSHAirflowConfiguration(
            working_dir=path,
            path=path,
            program={
                "test": ProgramConfiguration(
                    command="bash -c 'sleep 60; exit 1'",
                )
            },
        )
        yield cfg


@fixture
def supervisor_operator(supervisor_cfg):
    yield SupervisorTask(task_id="test-supervisor", cfg=supervisor_cfg)


@fixture
def supervisor_ssh_operator(supervisor_ssh_cfg):
    host = Host(name="test_host", username="test_user", password=Variable(key="VAR", deserialize_json=True))
    yield SupervisorSSHTask(
        task_id="test-supervisor",
        cfg=supervisor_ssh_cfg,
        host=host,
        port=Port(name="test_port", host=host, port=8080),
    )


@fixture
def dag_args():
    return DagArgs(
        description="",
        schedule="* * * * *",
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2026, 1, 1),
        max_active_tasks=1,
        max_active_runs=1,
        catchup=False,
        is_paused_upon_creation=True,
        tags=["a", "b"],
        dag_display_name="test",
        enabled=True,
    )


@fixture
def task_args():
    return TaskArgs(
        owner="airflow",
        email=["test@test.com"],
        email_on_failure=True,
        email_on_retry=True,
        retries=3,
        retry_delay=timedelta(minutes=5),
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2026, 1, 1),
        depends_on_past=True,
        queue="default",
        pool="default",
        pool_slots=1,
        do_xcom_push=True,
        task_display_name="test",
    )


@fixture
def dag(dag_args, task_args, python_operator, bash_operator, ssh_operator, bash_sensor, python_sensor):
    return Dag(
        dag_id="a-dag",
        **dag_args.model_dump(exclude_unset=True),
        default_args=task_args,
        tasks={
            "task1": python_operator,
            "task2": bash_operator,
            "task3": ssh_operator,
            "task4": bash_sensor,
            "task5": python_sensor,
        },
    )


@fixture
def dag_none_schedule(dag_args):
    return Dag(
        dag_id="a-dag",
        schedule=None,
        **dag_args.model_dump(exclude_unset=True, exclude={"schedule"}),
        tasks={},
    )


@fixture
def dag_with_external(dag_args, task_args, python_operator, bash_operator, ssh_operator, trigger_dagrun):
    ssh_operator.ssh_hook = hook
    ssh_operator.ssh_hook_external = True
    return Dag(
        dag_id="a-dag",
        **dag_args.model_dump(exclude_unset=True),
        default_args=task_args,
        tasks={
            "task1": python_operator,
            "task2": bash_operator,
            "task3": ssh_operator,
            "task4": trigger_dagrun,
        },
    )


@fixture
def dag_with_supervisor(dag_args, task_args, supervisor_operator):
    return Dag(
        dag_id="a-dag",
        **dag_args.model_dump(exclude_unset=True),
        default_args=task_args,
        tasks={
            "task": supervisor_operator,
        },
    )


@fixture
def dag_with_supervisor_ssh(dag_args, task_args, supervisor_ssh_operator):
    return Dag(
        dag_id="a-dag",
        **dag_args.model_dump(exclude_unset=True),
        default_args=task_args,
        tasks={
            "task": supervisor_ssh_operator,
        },
    )


def _null(**kwargs):
    return "test"


def fail():
    from airflow.exceptions import AirflowFailException

    raise AirflowFailException


def _choose(**kwargs):
    from airflow_ha import Action, Result

    return (Result.PASS, Action.CONTINUE)  # noqa: E731


@fixture
def dag_with_attribute_dependencies(dag_args, task_args, supervisor_operator):
    try:
        from airflow_ha import HighAvailabilityTask
    except ImportError:
        pytest.skip("airflow_ha is not installed, skipping HighAvailabilityTask fixtures")
        return

    pre = PythonTask(task_id="pre", python_callable=_null)
    ha = HighAvailabilityTask(task_id="ha", python_callable=_choose, dependencies=["pre"])
    retrigger_fail = PythonTask(task_id="retrigger_fail", python_callable=_null, dependencies=[(ha, "retrigger_fail")])
    stop_fail = PythonTask(task_id="stop_fail", python_callable=fail, trigger_rule="all_failed", dependencies=[(ha, "stop_fail")])
    retrigger_pass = PythonTask(task_id="retrigger_pass", python_callable=_null, dependencies=[(ha, "retrigger_pass")])
    stop_pass = PythonTask(task_id="lam-stop_pass", python_callable=_null, dependencies=[(ha, "stop_pass")])
    return Dag(
        dag_id="a-dag",
        **dag_args.model_dump(exclude_unset=True),
        default_args=task_args,
        tasks={
            "pre": pre,
            "ha": ha,
            "retrigger-fail": retrigger_fail,
            "stop-fail": stop_fail,
            "retrigger-pass": retrigger_pass,
            "stop-pass": stop_pass,
        },
    )


@fixture
def airflow_config_instance():
    try:
        from airflow_config import Configuration
    except ImportError:
        pytest.skip("airflow_config is not installed, skipping airflow_config fixtures")
        return
    return Configuration(
        default_task_args=TaskArgs(owner="test"),
        dags={"test-dag": Dag(tags=["test"])},
    )
