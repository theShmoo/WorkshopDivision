import logging

logger = logging.getLogger("workshopdivision")


class Participant(object):
    """docstring for Participant"""
    def __init__(self, name, stufe, trupp, points, available_dates):
        super(Participant, self).__init__()
        self.name = name
        self.stufe = stufe
        self.trupp = trupp
        self.points = points
        self.workshops = {date: None for date in available_dates}
        self.available_dates = available_dates
        self.normalizePoints()

    def getPoints(self, workshop):
        points = self.points[workshop]
        if points is None:
            logger.warning("%s is not inside Participant %s", workshop,
                           self.name)
        else:
            logger.debug("Get %d Points of Workshop %s from Participant %s",
                         points, workshop, self.name)
            return points

    def normalizePoints(self):
        """Get a copy of the normalized points."""
        sum_points = sum([p for w, p in self.points.iteritems()])
        sum_points /= float(100)
        self.points = {w: p / sum_points for w, p in self.points.iteritems()}
        print(str(self.points))

    def isFullyAssigned(self):
        for d, w in self.workshops.iteritems():
            if w is None:
                return False

        logger.debug("Participant %s is fully assigned with workshops: %s",
                     self, str(self.workshops))
        return True

    def isAvailable(self, workshop):
        """If the participant has a free slot and is not using the workshop"""
        free = False

        free_days = []
        for d in self.available_dates:
            if workshop.hasFreeSlots(d):
                free_days.append(d)

        for d in free_days:
            w = self.workshops[d]
            # check if the workshop is already assigned
            if w is workshop:
                return False
            # if the day is still free set the participant available
            if w is None:
                free = True

        return free

    def getFreeDays(self):
        free_days = []
        for d, w in self.workshops.iteritems():
            if w is None:
                free_days.append(d)

        return free_days

    def assignWorkshop(self, workshop):
        """Assigns the workshop to a free date"""
        free_days = self.getFreeDays()
        day = workshop.getMinDay(free_days)
        if day is not None:
            self.workshops[day] = workshop
            workshop.assignParticipant(day, self)
            logger.info("%s assigned for %s on %s with %.1f points",
                        self, workshop, day, self.getPoints(workshop))
        else:
            logger.warning("Was not able to assign %s for %s on %s with %.1f" +
                           "points", self, workshop, day,
                           self.getPoints(workshop))

    def clearAssignment(self):
        """Remove the assigned workshops of the participant"""
        for d in self.workshops:
            workshop = self.workshops[d]
            if workshop is not None:
                workshop.removeParticipant(d, self)
                self.workshops[d] = None
                logger.info("%s removed from %s", self, workshop)

    def __str__(self):
        return self.name.encode('ascii', 'ignore').decode('ascii')
