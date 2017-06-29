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
        logger.info("%s: %s", self, self.days)

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

    def getMinDay(self, free_days=None):
        """returns the day with the minimum participants."""
        if free_days is None:
            free_days = self.days

        min_part = 1000
        for d in free_days:
            if self.usesDay(d):
                part = len(self.participants[d])
                if part < min_part:
                    min_day = d
                    min_part = part
        return min_day

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

    def assignParticipant(self, day, participant):
        if not self.usesDay(day):
            logger.warning("%s does not use day %s", self, day)
            return
        if participant in self.participants[day]:
            logger.warning("Was not able to assign %s for %s on %s!",
                           participant, self, day)
        else:
            self.participants[day].append(participant)
            logger.debug("Assigned %s for %s on %s", participant, self, day)

    def usesDay(self, day):
        return day in self.days

    def removeParticipant(self, day, participant):
        """Remove the participant from the given date"""
        if self.usesDay(day):
            if participant in self.participants[day]:
                self.participants[day].remove(participant)
            else:
                logger.warning("Can't remove %s from %s for %s (not there)",
                               participant, day, self)
        else:
            logger.warning("%s does not use day %s", self, day)

    def hasFreeSlots(self, day):
        if self.usesDay(day):
            free_slots = len(self.participants[day])

            isfree = free_slots < self.max_participants_per_day

            if isfree:
                logger.debug("%s has %d/%d on %s",
                             self, free_slots, self.max_participants_per_day,
                             day)
            else:
                logger.debug("%s has no free slots left (%d/%d) on %s",
                             self, free_slots, self.max_participants_per_day,
                             day)
            return isfree
        else:
            logger.debug("%s does not use use day %s",
                         self, day)
            return False

    def __str__(self):
        # return "Workshop %s am %s von %s" % (
        #     self.name,
        #     self.getDaysString(),
        #     self.supervisor)
        return self.name.encode('ascii', 'ignore').decode('ascii')

    def __repr__(self):
        return self.name.encode('ascii', 'ignore').decode('ascii')
