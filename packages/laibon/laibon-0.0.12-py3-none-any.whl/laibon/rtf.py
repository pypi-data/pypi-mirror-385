# Copyright Wenceslaus Mumala 2023. See LICENSE file.

import logging
import time

from laibon import common
from laibon import exception


class FlowDefinition:
    """Defines a workflow of activities with conditional jumps.
    
    Activities are executed in sequence with the ability to jump to other
    activities based on result codes. Supports error handling and backward
    jump prevention.
    
    Example:
        flow = FlowDefinition("User Registration")
        flow.add(ValidateInputActivity) \\
            .jump_if(ValidationResult.INVALID, ErrorActivity) \\
            .jump_default(CreateUserActivity)
        flow.add(CreateUserActivity) \\
            .jump_if(CreateResult.SUCCESS, SendEmailActivity) \\
            .jump_if(CreateResult.DUPLICATE, DuplicateErrorActivity)
        flow.add(SendEmailActivity)
        
        # Execute the flow
        runner = FlowRunner(data_container)
        runner.run_flow(flow)
    """

    def __init__(self, flow_name="Undefined"):
        """Dictionary to store activity together with jumps i.e {activity, {activity_result, next_activity_to_run}}"""
        self.activities = {}

        """Dictionary to store jumps e.g {result_ok:activity_a, result_error: activity_2}. Initialized in add() """
        self._jumps = None

        """Dictionary to store arguments to an activity class constructor, the arguments are in a list"""
        self.activity_args = {}

        """If available, will be run if no jump is available and the flow will terminate"""
        self.error_handler = None

        """Name of flow, used for logging purposes"""
        self._flow_name = flow_name

    def __str__(self):
        return self._flow_name

    def add(self, activity_class, activity_args=None):
        """
        Add activity to the flow, activity_args contains any sequence of arguments supported by the activity constructor
        :param activity_class:
        :param activity_args:
        :return:
        """
        self._jumps = {}
        self.activities[activity_class] = self._jumps
        if activity_args is not None:
            self.activity_args[activity_class] = activity_args
        return self

    def error_handler(self, activity_class):
        """
        If an activity returns a result for which there isnt a jump, this activity will be called and the flow will terminate
        If the activity has jumps, they will not be executed.
        """
        self.error_handler = activity_class
        return self

    def jump_if(self, result: common.ActivityResult, activity_class):
        """
        Conditional jump based on result code from the running activity
        :param result:
        :param activity_class:
        :return:
        """
        self.validate_jump(activity_class)
        self._jumps[result] = activity_class
        return self

    def jump_default(self, activity_class):
        """
        Default jump when running activity completes normally
        :param activity_class:
        :return:
        """
        self.validate_jump(activity_class)
        self._jumps[common.DefaultActivityResult.NEXT] = activity_class
        return self

    def validate_jump(self, activity_class):
        """
        Should protect against backward jumps
        :param activity_class:
        :return:
        """
        if self.activities.get(activity_class) is not None:
            raise exception.InvalidFlowDefinition()


class FlowRunner:
    """Executes a flow
    Every Activity must return a RESULT_OK and provide a jump case in default ie if the Activity might return some other
    result code, there must be a jump case defined on the flow
    """
    # TODO Add possibility to run the next activity in the sequence if result code from executed flow is RESULT_OK...
    # Will help against having to define a jump_default if the flow continues to the next activity in the sequence

    LOGGER = logging.getLogger(__name__)

    def __init__(self, data_container: common.Container):
        self.data_container = data_container
        self._flow_start_time = None
        self._flow_end_time = None

    def _run_activity_steps(self, activity: common.Activity):
        """Runs the methods of the activity. Currently only 'process' is triggered for simplicity"""
        # Would be a great improvement if we could scan annotated methods in the activity and run them separately
        # Each activity should have a process(DataContainer) method
        return activity.process(self.data_container)

    def _run_activity(self, active_activity, jumps_dict, activities_dict, flow_activity_args):
        self.LOGGER.debug("Running activity {}".format(active_activity.__name__))
        activity_args = flow_activity_args.get(active_activity)
        result = common.DefaultActivityResult.NEXT
        try:
            activity_instance = active_activity() if activity_args is None else active_activity(
                *activity_args)  # Call constructor
        except Exception as e:
            self.LOGGER.debug("Unable to start activity because of ", exc_info=True)
            raise e
        try:
            result = self._run_activity_steps(activity_instance)
        except Exception as e:
            self.LOGGER.debug("Unhanded exception in activity {} {}".format(active_activity.__name__, e), exc_info=True)
            raise e
        finally:
            self.LOGGER.debug("{} completed with result code {}.".format(active_activity.__name__, result.to_value()))

        if len(jumps_dict) > 0:
            next_activity = jumps_dict[result]
            self.LOGGER.debug("Found next activity to execute " + next_activity.__name__)
            next_jumps = activities_dict.get(next_activity)
            if next_jumps is None:  # Should never happen at runtime
                self.LOGGER.debug("Unable to find jump location for result ", result)
                raise exception.InvalidFlowDefinition(
                    "Flow is not configured correctly. {} is missing".format(next_activity.__name__))
            self._run_activity(next_activity, next_jumps, activities_dict, flow_activity_args)

    def run_flow(self, flow: FlowDefinition):
        """Entry point for execution of provided flow
           Callback if provided will be triggered at the end
           """
        self._flow_start_time = time.process_time()
        if not isinstance(flow, FlowDefinition):
            raise exception.InvalidFlowDefinition()

        # Get start activity
        start_activity, jumps = next(iter(flow.activities.items()))

        FlowRunner.LOGGER.debug("Starting flow {}".format(str(flow)))
        self._run_activity(start_activity, jumps, flow.activities, flow.activity_args)
        FlowRunner.LOGGER.debug("Done running flow {}".format(str(flow)))
        self._flow_end_time = time.process_time()

    def get_elapsed_time(self):  # Returns None if flow didnt complete gracefully
        return self._flow_end_time - self._flow_start_time if self._flow_end_time else None
