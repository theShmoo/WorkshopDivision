import logging

logger = logging.getLogger("workshopdivision")


class Workshop(object):
    """Workshop is a class to encapsulate the info of a workshop"""
    ID = 0

    def __init__(self, name, supervisor, ages, days, max_participants_per_day):
        super(Workshop, self).__init__()
        self.name = name
        self.days = days
        self.ages = ages
        self.supervisor = supervisor
        self.max_participants_per_day = max_participants_per_day
        self.participants = {day: [] for day in self.days}
        self.id = Workshop.ID
        Workshop.ID += 1

    def maxParticipants(self):
        """Get the number of participants of the workshop"""
        num_days = len(self.days)
        if num_days > 0:
            max_participants = self.max_participants_per_day * num_days
            logger.debug("Workshop %s has %d on %d days!",
                         self.name, max_participants, num_days)
            return max_participants
        else:
            logger.error("Workshop %s has no valid days!", self.name)

    def getParticipantsOfDay(self, day):
        """Get the participants of a day"""
        p = self.participants[day]
        if p is None:
            logger.warning("%s is not available in %s", day, self.name)
        return p

    def getDaysString(self):
        s = ""
        first = True
        for d in self.days:
            if first:
                first = False
                s = s + d
            else:
                s = s + "," + d
        return s

    def __str__(self):
        # return "Workshop %s am %s von %s" % (
        #     self.name,
        #     self.getDaysString(),
        #     self.supervisor)
        return self.name.encode('ascii', 'ignore').decode('ascii')

    def __repr__(self):
        return str(self.id)
