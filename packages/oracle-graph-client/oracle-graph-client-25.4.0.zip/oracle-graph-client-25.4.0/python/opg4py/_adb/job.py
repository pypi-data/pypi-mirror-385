#
# Copyright (C) 2013 - 2025, Oracle and/or its affiliates. All rights reserved.
# ORACLE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
from jnius import autoclass
from opg4py._utils.error_handling import java_handler

JavaJob = autoclass('oracle.pg.rdbms.Job')


class Job:
    def __init__(self, javaJob):
        self.javaJob = javaJob

    def get_id(self):
        """Get the job ID.

        :return: the ID of this job.
        """
        return self.javaJob.getId()

    def get_name(self):
        """Get the job name.

        :return: the name of this job.
        """
        return self.javaJob.getName()

    def get_description(self):

        """Get the job description.

        :return: the description of this job.
        """
        return self.javaJob.getDescription()

    def get_type(self):
        """Get the job type.

        :return: the type of this job.
        """
        return self.javaJob.getType()

    def get_status(self):
        """Get the job status.

        :return: the status of this job.
        """
        return self.javaJob.getStatus()

    def get_created_by(self):
        """Get the database username who created this job.

        :return: the username of the creator of this job.
        """
        return self.javaJob.getCreatedBy()

    def get_error(self):
        """Get an optional error message returned by the server.

        :return: an error message in case this job has completed unsuccessfully or NULL if job is still running or
            completed successfully
        """
        return self.javaJob.getError()

    def get_logs(self):
        """Get the log entries emitted by this job.

        :return: the log entries.
        """
        logs = []
        for entry in java_handler(self.javaJob.getLogEntries, []):
            item = {
                'timestamp': entry.getTimestamp(),
                'message': entry.getMessage()
            }
            logs.append(item)
        return logs

    def poll(self):
        """Starts polling the server using a background thread and updates this job's status and log as results come in.
        Once job completes, fails or gets cancelled, this job is marked as such as well. If this job has completed,
        this method will do nothing.

        :return: this job
        """
        java_handler(self.javaJob.poll, [])
        return self

    def get(self):
        """Waits if necessary for this job to complete, and then returns its result.

        :return: the result value

        Throws:
            CancellationException - if this job was cancelled
            ExecutionException - if this job completed exceptionally
            InterruptedException - if the current thread was interrupted while waiting
        """
        java_handler(self.javaJob.get, [])

    def is_done(self):
        """Returns True if completed in any fashion: normally, exceptionally, or via cancellation.

        :return: True if completed, False otherwise
        """
        return java_handler(self.javaJob.isDone, [])

    def is_cancelled(self):
        """Returns true if this job was cancelled before it completed normally.

        :return: True if this job was cancelled before it completed normally, False otherwise
        """
        return java_handler(self.javaJob.isCancelled, [])

    def is_completed_exceptionally(self):
        """Returns true if this job completed exceptionally, in any way. Possible causes include cancellation,
        explicit invocation of completeExceptionally, and abrupt termination of a CompletionStage action.

        :return: True if this CompletableFuture completed exceptionally, False otherwise
        """
        return java_handler(self.javaJob.isCancelled, [])
