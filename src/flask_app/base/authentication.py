from abc import (
    ABC,
    abstractmethod
)
from dataclasses import dataclass
from typing import Optional

from flask.wrappers import Response as FlaskResponse
from iam import models as iam_models


@dataclass
class BaseAuthentication(ABC):
    authenticated: bool = True
    response: Optional[FlaskResponse] = None

    user: Optional[iam_models.User] = None

    @classmethod
    @abstractmethod
    def validate_request(cls):
        raise NotImplementedError('Calling from the base class')
