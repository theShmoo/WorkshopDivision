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

    def getPoints(self, workshop):
        points = self.points[workshop]
        if points is None:
            logger.warning("%s is not inside Participant %s", workshop,
                           self.name)
        else:
            logger.debug("Get %d Points of Workshop %s from Participant %s",
                         points, workshop, self.name)
            return points

    def isAvailable(self, workshop=None):
        """If the participant has a free slot and is not using the workshop"""
        free = False
        for d, w in self.workshops.iteritems():
            if w is workshop:
                return False
            if w is None:
                free = True

        return free

    def assignWorkshop(self, workshop):
        """Assigns the workshop to a free date"""
        for d, w in self.workshops.iteritems():
            if w is None:
                self.workshops[d] = workshop
                logger.info("%s assigned for %s on %s with %d points",
                            self, workshop, d, self.getPoints(workshop))
                return
        logger.warning("Was not able to assign %s for %s on %s with %d points",
                       self, workshop, d, self.getPoints(workshop))

    def __str__(self):
        return self.name.encode('ascii', 'ignore').decode('ascii')
