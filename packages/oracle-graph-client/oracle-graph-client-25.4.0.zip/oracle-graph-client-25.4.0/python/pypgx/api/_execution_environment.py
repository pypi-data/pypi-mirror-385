#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from typing import List, TYPE_CHECKING, Dict, Any

import pypgx._utils.conversion as conversion
from pypgx._utils.error_handling import java_handler
from pypgx._utils.error_messages import INVALID_OPTION
from pypgx._utils.pgx_types import task_priorities, update_consistency_models


if TYPE_CHECKING:
    from pypgx.api._pgx_session import PgxSession


class CpuEnvironment:
    """A sub environment for CPU bound tasks"""

    _java_class = "oracle.pgx.api.executionenvironment.CpuEnvironment"

    def __init__(self, java_cpu_environment) -> None:
        self._cpu_environment = java_cpu_environment

    def get_weight(self) -> int:
        """Get the weight of the CPU environment.

        :returns: the weight of the CPU environment.
        """
        return java_handler(self._cpu_environment.getWeight, [])

    def get_priority(self) -> str:
        """Get the priority of the CPU environment.

        :returns: the environment priority.
        """
        priority = java_handler(self._cpu_environment.getPriority, [])
        return conversion.enum_to_python_str(priority)

    def get_max_num_threads(self) -> int:
        """Get the maximum number of threads that can be used by the CPU environment.

        :returns: the maximum number of threads.
        """
        return java_handler(self._cpu_environment.getMaxNumThreads, [])

    def set_weight(self, weight: int) -> None:
        """Set the weight of the CPU environment.

        :param weight: the weight of the CPU environment.
        """
        java_handler(self._cpu_environment.setWeight, [weight])

    def set_priority(self, priority: str) -> None:
        """Set the priority of the CPU environment.

        :param priority: the environment priority.
        """
        if priority not in task_priorities:
            raise ValueError(
                INVALID_OPTION.format(var='unit', opts=list(task_priorities.keys()))
            )
        java_priority = task_priorities[priority]
        java_handler(self._cpu_environment.setPriority, [java_priority])

    def set_max_num_threads(self, max_num_threads: int) -> None:
        """Set the maximum number of threads that can be used by the CPU environment.

        :param max_num_threads: the maximum number of threads.
        """
        java_handler(self._cpu_environment.setMaxNumThreads, [max_num_threads])

    def get_relevant_fields(self) -> List[str]:
        """Get the relevant fields of the CPU environment.

        :returns: the relevant fields of the CPU environment.
        """
        java_fields = java_handler(self._cpu_environment.getRelevantFields, [])
        return [conversion.enum_to_python_str(field) for field in java_fields]

    def get_values(self) -> Dict[Any, Any]:
        """Return values of class

        :return: values
        """
        return conversion.map_to_python(java_handler(self._cpu_environment.getValues, []))

    def reset(self) -> None:
        """Reset environment"""
        java_handler(self._cpu_environment.reset, [])

    def __repr__(self) -> str:
        return "{}()".format(self.__class__.__name__)

    def __str__(self) -> str:
        return repr(self)


class IoEnvironment:
    """A sub environment for IO tasks"""

    _java_class = "oracle.pgx.api.executionenvironment.IoEnvironment"

    def __init__(self, java_io_environment) -> None:
        self._io_environment = java_io_environment

    def get_num_threads_per_task(self) -> int:
        """Get the number of threads per task.

        :returns: the number of threads per task.
        """
        return java_handler(self._io_environment.getNumThreadsPerTask, [])

    def set_num_threads_per_task(self, num_threads_per_task: int) -> None:
        """Set the number of threads per task.

        :param num_threads_per_task: the number of threads per task.
        """
        java_handler(self._io_environment.setNumThreadsPerTask, [num_threads_per_task])

    def get_relevant_fields(self) -> List[str]:
        """Get the relevant fields of the IO environment.

        :returns: the relevant fields of the IO environment.
        """
        java_fields = java_handler(self._io_environment.getRelevantFields, [])
        return [conversion.enum_to_python_str(field) for field in java_fields]

    def get_values(self) -> Dict[Any, Any]:
        """Return values of class

        :return: values
        """
        return conversion.map_to_python(java_handler(self._io_environment.getValues, []))

    def reset(self) -> None:
        """Reset environment"""
        java_handler(self._io_environment.reset, [])

    def __repr__(self) -> str:
        return "{}()".format(self.__class__.__name__)

    def __str__(self) -> str:
        return repr(self)


class ExecutionEnvironment:
    """A session bound environment holding the execution configuration for each task type."""

    _java_class = "oracle.pgx.api.executionenvironment.ExecutionEnvironment"

    def __init__(self, java_environment, session: "PgxSession") -> None:
        self._environment = java_environment
        self._session = session

    def get_session(self) -> "PgxSession":
        """Get the PGX session associated with this execution environment.

        :returns: the PGX session associated with this execution environment.
        """
        return self._session

    def get_io_environment(self) -> IoEnvironment:
        """Get the IO environment.

        :returns: the IO environment.
        """
        java_io_env = java_handler(self._environment.getIoEnvironment, [])
        return IoEnvironment(java_io_env)

    def get_analysis_environment(self) -> CpuEnvironment:
        """Get the analysis environment.

        :returns: the analysis environment.
        """
        java_cpu_env = java_handler(self._environment.getAnalysisEnvironment, [])
        return CpuEnvironment(java_cpu_env)

    def get_fast_analysis_environment(self) -> CpuEnvironment:
        """Get the fast analysis environment.

        :returns: the fast analysis environment.
        """
        java_cpu_env = java_handler(self._environment.getFastAnalysisEnvironment, [])
        return CpuEnvironment(java_cpu_env)

    def allows_concurrent_tasks(self) -> bool:
        """Check if the session allows the tasks to run concurrently.

        :returns: True if the session allows the tasks to run concurrently.
        """
        return bool(java_handler(self._environment.allowsConcurrentTasks, []))

    def get_update_consistency_model(self) -> str:
        """Get the update consistency model.

        :returns: the update consistency model.
        """
        model = java_handler(self._environment.getUpdateConsistencyModel, [])
        return conversion.enum_to_python_str(model)

    def set_update_consistency_model(self, model: str) -> None:
        """Set the update consistency model.

        :param model: the update consistency model.
        """
        if model not in update_consistency_models:
            raise ValueError(
                INVALID_OPTION.format(var='unit', opts=list(update_consistency_models.keys()))
            )
        java_model = update_consistency_models[model]
        java_handler(self._environment.setUpdateConsistencyModel, [java_model])

    def reset_update_consistency_model(self) -> None:
        """Reset the update consistency model."""
        java_handler(self._environment.resetUpdateConsistencyModel, [])

    def get_values(self) -> Dict[Any, Any]:
        """Get the values of class

        :return: values
        """
        values = java_handler(self._environment.getValues, [])
        list_values = conversion.collection_to_python_list(values)

        def get_convert(e, k):
            return conversion.call_and_convert_to_python(e, k)
        return {
            get_convert(v, 'getKey'): get_convert(v, 'getValue')
            for v in list_values
        }

    def reset(self) -> None:
        """Reset environment"""
        java_handler(self._environment.reset, [])

    def __repr__(self) -> str:
        return "{}(session id: {})".format(self.__class__.__name__, self._session.id)

    def __str__(self) -> str:
        return repr(self)
