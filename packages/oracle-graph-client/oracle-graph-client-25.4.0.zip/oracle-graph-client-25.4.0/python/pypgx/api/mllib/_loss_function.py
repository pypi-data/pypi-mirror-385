#
# Copyright (C) 2013 - 2025 Oracle and/or its affiliates. All rights reserved.
#

from pypgx._utils.error_messages import INVALID_OPTION
from pypgx._utils import pgx_types
from pypgx._utils.pgx_types import SUPERVISED_LOSS_FUNCTIONS
from pypgx._utils.error_handling import java_handler
from typing import Any, List
from jnius import autoclass

JavaLossFunctions = autoclass("oracle.pgx.config.mllib.loss.LossFunctions")


class LossFunction(object):
    """Abstract LossFunction class that represent loss functions"""

    _java_class = 'oracle.pgx.config.mllib.loss.LossFunction'

    def __init__(self, java_arg_list: List[Any] = None) -> None:
        self._java_arg_list = java_arg_list if java_arg_list else []


class SoftmaxCrossEntropyLoss(LossFunction):
    """Softmax Cross Entropy loss for multi-class classification"""

    _java_class = 'oracle.pgx.config.mllib.loss.SoftmaxCrossEntropyLoss'

    def __init__(self) -> None:
        super().__init__([])

    def __repr__(self) -> str:
        return "%s" % (self.__class__.__name__)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)


class SigmoidCrossEntropyLoss(LossFunction):
    """Sigmoid Cross Entropy loss for binary classification"""

    _java_class = 'oracle.pgx.config.mllib.loss.SigmoidCrossEntropyLoss'

    def __init__(self):
        super().__init__([])

    def __repr__(self) -> str:
        return "%s" % (self.__class__.__name__)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)


class DevNetLoss(LossFunction):
    """Deviation loss for anomaly detection"""

    _java_class = 'oracle.pgx.config.mllib.loss.DevNetLoss'

    def __init__(self,
                 confidence_margin: float,
                 anomaly_property_value: bool) -> None:
        """
        :param confidence_margin: confidence margin
        :param anomaly_property_value: property value that represents the anomaly
        """
        anomaly_property_value = pgx_types.Boolean(anomaly_property_value)
        super().__init__([confidence_margin, anomaly_property_value])
        self._dev_net_loss = java_handler(JavaLossFunctions.devNetLoss,
                                          [confidence_margin, anomaly_property_value])

    def __repr__(self) -> str:
        return "%s" % (self.__class__.__name__)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._java_arg_list[0] == other._java_arg_list[0] and self._java_arg_list[1].equals(
            other._java_arg_list[1]
        )

    def get_anomaly_property_value(self) -> Any:
        """Get Anomaly Property Value.

        :return: the anomaly property value
        """
        return java_handler(self._dev_net_loss.getAnomalyPropertyValue, [])

    def get_confidence_margin(self) -> float:
        """Get confidence margin of the loss function.

        :return: the confidence margin
        """
        return java_handler(self._dev_net_loss.getConfidenceMargin, [])


class MSELoss(LossFunction):
    """MSE loss for regression"""

    _java_class = 'oracle.pgx.config.mllib.loss.MSELoss'

    def __init__(self) -> None:
        super().__init__([])

    def __repr__(self) -> str:
        return "%s" % (self.__class__.__name__)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)


def _get_loss_function(loss_fn_name: str) -> LossFunction:
    """Retrieve LossFunction object that can be instantiated no constructor argument"""

    loss_fn_value_error = ValueError(
        INVALID_OPTION.format(
            var='loss function',
            opts=', '.join(SUPERVISED_LOSS_FUNCTIONS.keys())
        )
    )

    if loss_fn_name not in SUPERVISED_LOSS_FUNCTIONS.keys():
        raise loss_fn_value_error

    loss_fn = None
    for subclass in LossFunction.__subclasses__():
        if subclass.__name__ is SUPERVISED_LOSS_FUNCTIONS[loss_fn_name]:
            loss_fn = subclass()

    if loss_fn is not None:
        return loss_fn
    raise loss_fn_value_error
