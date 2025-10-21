"""
[Bridgic Event Handling Mechanism]

This module defines the foundational classes and types for the Bridgic event handling
system, which facilitates near real-time communication between workers within an Automa 
and the application layer outside of it.

Workers can send events to the application layer, and, if necessary, the application layer 
can send feedback back to the workers. A worker can send an event by calling the `post_event()` 
method. To process these events, the application layer can register event handlers using 
the Automa's `register_event_handler()` method. Since Automa can be nested, only event handlers 
registered on the top-level Automa will be triggered to handle events.

There are two categories of events: those that require feedback from the application layer 
and those that do not. For example, a `ProgressEvent` is used to report progress from a 
worker to the application layer and does not require feedback. Conversely, some events may 
request additional required feedback from the user. When an event requires feedback, the 
application layer can respond by calling the `send` method of the `FeedbackSender` object. 
The worker will then `await` the future object returned by the `post_event` method to receive 
this feedback.

Attention: For the Bridgic event handling system to work properly, the Automa process must 
remain in memory throughout the entire event and feedback exchange. If an interaction is 
expected to take a long time and the Automa process needs to be paused before the exchange 
is complete, it is recommended to use the [Bridgic human interaction mechanism] instead.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, Callable, Union
from typing_extensions import TypeAlias
from abc import ABC, abstractmethod
from bridgic.core.types._common import ZeroToOne

class Event(BaseModel):
    """
    An event is a message that is sent from one worker inside the Automa to the application layer outside the Automa.

    Fields
    ------
    event_type: Optional[str]
        The type of the event. The type of the event is used to identify the event handler registered to handle the event.
    timestamp: datetime
        The timestamp of the event.
    data: Optional[Any]
        The data attached to the event.
    """
    event_type: Optional[str] = None
    timestamp: datetime = datetime.now()
    data: Optional[Any] = None

class ProgressEvent(Event):
    """
    A progress event is an event that indicates the progress of a worker task.

    Fields
    ------
    progress: ZeroToOne
        The progress of the task, represented as a value between 0 and 1.
    """
    progress: ZeroToOne

class Feedback(BaseModel):
    """
    A feedback is a message that is sent from the application layer outside the Automa to a worker inside the Automa.

    Fields
    ------
    data: Any
        The data attached to the feedback.
    """
    data: Any

class FeedbackSender(ABC):
    """
    The appliction layer must use `FeedbackSender` to send back feedback to the worker inside the Automa.
    """
    @abstractmethod
    def send(self, feedback: Feedback) -> None:
        """
        Send feedback to the Automa.
        This method can be called only once for each event.

        This `send` method can be safely called in several different scenarios:
        - In the same asyncio Task of the same event loop as the event handler.
        - In a different asyncio Task of the same event loop as the event handler.
        - In a different thread from the event handler.

        Parameters
        ----------
        feedback: Feedback
            The feedback to be sent.
        """
        ...

EventHandlerType: TypeAlias = Union[Callable[[Event, FeedbackSender], None], Callable[[Event], None]]


