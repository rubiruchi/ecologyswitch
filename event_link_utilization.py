from ryu.controller import ofp_event, event

class EventLinkUtilization(event.EventBase):
    def __init__(self, message):
        super(EventLinkUtilization, self).__init__()
        self.message = message