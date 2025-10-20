from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.helpers.pubsub.schemas.Schema__Event import Schema__Event
from osbot_utils.utils.Misc import random_guid


class Schema__Event__Leave_Room(Schema__Event):
    event_type : str = 'leave-room'
    room_name  : str