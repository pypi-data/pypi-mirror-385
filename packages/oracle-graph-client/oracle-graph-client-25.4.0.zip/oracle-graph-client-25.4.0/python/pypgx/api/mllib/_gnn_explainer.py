#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_handling import java_handler


class GnnExplainer:
    """GnnExplainer object used to request explanations from model predictions."""

    _java_class = 'oracle.pgx.api.mllib.GnnExplainer'

    def __init__(self, java_explainer):
        self._explainer = java_explainer

    @property
    def num_optimization_steps(self) -> int:
        """Get number of optimization steps.

        :return: number of optimization steps
        :rtype: int
        """
        return java_handler(self._explainer.numOptimizationSteps, [])

    @num_optimization_steps.setter
    def num_optimization_steps(self, num_steps: int):
        java_handler(self._explainer.numOptimizationSteps, [num_steps])

    @property
    def learning_rate(self) -> float:
        """Get learning rate.

        :return: learning rate
        :rtype: float
        """
        return java_handler(self._explainer.learningRate, [])

    @learning_rate.setter
    def learning_rate(self, lr: float):
        java_handler(self._explainer.learningRate, [lr])

    @property
    def marginalize(self) -> bool:
        """Get value of marginalize.

        :return: value of marginalize
        :rtype: bool
        """
        return java_handler(self._explainer.marginalize, [])

    @marginalize.setter
    def marginalize(self, do_marginalize: bool):
        java_handler(self._explainer.marginalize, [do_marginalize])
