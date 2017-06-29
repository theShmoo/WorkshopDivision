import csv
import logging
import logging.config
import json
import os
from random import shuffle

from workshop import Workshop
from participant import Participant

logger = logging.getLogger("workshopdivision")


def setup_logging(
    default_path='logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration"""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def getDialect(filename):
    """Get the dialect of the given csv file."""
    if os.path.isfile(filename):
        with open(filename, 'rb') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
        logging.info("using %s for %s", dialect, filename)
    else:
        logging.error("Filename %s does not exist", filename)
    return dialect


def parseInt(s):
    try:
        return int(s)
    except ValueError:
        logging.error("String %s is not an integer", s)
        return s


def unicode_csv_reader(filename, dialect=None, **kwargs):
    """Yield the rows of a file """
    if os.path.isfile(filename):

        if dialect is None:
            dialect = getDialect(filename)

        with open(filename, 'rb') as f:
            csv_reader = csv.reader(f, dialect=dialect, **kwargs)
            for row in csv_reader:
                yield [unicode(cell, 'utf-8') for cell in row]
    else:
        logging.error("Filename %s does not exist", filename)


class WorkshopDivision(object):
    """A class to divise children to workshops"""

    def __init__(self):
        """Initialize the workshop division"""
        super(WorkshopDivision, self).__init__()
        # init the sets
        self.workshops = []
        self.participants = []
        self.available_dates = ["Sa", "Mi"]
        self.available_ages = ["GuSp", "CaEx"]
        # load the logging configuration
        setup_logging()
        logger.debug("Workshop Division created")

    def addWorkshop(self, name, chef, str_ages,
                    max_participants_per_date, str_dates):
        """Parse the input parameters and adds a new workshop to the diviser"""
        logger.debug("add Workshop %s", name)
        ages = []
        for a in self.available_ages:
            if a in str_ages:
                ages.append(a)
        if len(ages) is 0:
            logger.error("No Ages!")

        dates = []
        for d in self.available_dates:
            if d in str_dates:
                dates.append(d)
        if len(dates) is 0:
            logger.error("No Dates!")

        w = Workshop(name, chef, ages, dates,
                     parseInt(max_participants_per_date))
        self.workshops.append(w)

    def addParticipant(self, name, stufe, trupp, points):
        """Adds a new participants to the diviser"""
        logger.debug("add Participant %s", name)
        p = Participant(name, stufe, trupp, points, self.available_dates)
        self.participants.append(p)

    def getNumWorkshops(self):
        """Get the number of workshops in the diviser"""
        return len(self.workshops)

    def getWorkshop(self, name):
        """Get the workshop with the specified name"""
        for w in self.workshops:
            if w.name == name:
                logger.debug("Found Workshop %s", name)
                return w

        logger.warning("Did not found Workshop %s", name)

    def getAllWorkshopPlaces(self):
        """"""
        return sum([w.maxParticipants() for w in self.workshops])

    def getWorkshopStatistics(self):
        """"""
        data = {}
        data['anzahl'] = self.getNumWorkshops()
        data['platz'] = self.getAllWorkshopPlaces()
        logging.info("Workshop Statistics: %s", str(data))
        return data

    def getNumParticipants(self):
        """Get the number of participants in the diviser"""
        return len(self.workshops)

    def getPointsPerWorkshop(self, remaining=None):
        """Get all points per workshop"""
        if remaining is None:
            remaining = self.participants
        all_points = {w: 0.0 for w in self.workshops}
        for p in remaining:
            for w in self.workshops:
                if p.isAvailable(w):
                    all_points[w] += p.getPoints(w)

        return all_points

    def getParticipantsStatistics(self):
        """"""
        data = {}
        data['anzahl'] = self.getNumParticipants()
        data['platz'] = self.getMeanPointsPerWorkshop()
        logging.info("Workshop Statistics: %s", str(data))
        return data

    def loadWorkshops(self, csv_file, dialect=None):
        """Loads the workshops from a csv file"""
        logger.info('loading workshops from %s', csv_file)
        reader = unicode_csv_reader(csv_file, dialect)

        # skip headers
        next(reader)

        for row in reader:
            name = row[1]
            chef = row[2]
            ages = row[3]
            max_participants = row[4]
            dates = row[5]
            self.addWorkshop(name, chef, ages, max_participants, dates)

    def loadParticipants(self, csv_file, dialect=None):
        """Loads the participants from a csv file"""
        logger.info('loading participants from %s', csv_file)
        reader = unicode_csv_reader(csv_file, dialect)

        # get headers
        header = next(reader)
        name_ids = range(5, len(header))
        w_names = [header[i] for i in name_ids]

        for row in reader:
            name = row[1]
            if "GuSp" in row[2]:
                stufe = "GuSp"
            else:
                stufe = "CaEx"
            trupp = row[3] if stufe is "GuSp" else row[4]
            points = {}
            for count, i in enumerate(name_ids):
                w = self.getWorkshop(w_names[count])
                points[w] = parseInt(row[i])
            self.addParticipant(name, stufe, trupp, points)

        # shuffle participants for randomness
        shuffle(self.participants)

    def getParticipantWithMaxPoints(self, w, remaining=None):
        """Get the participants with the maximum number of given points"""
        if remaining is None:
            remaining = self.participants
        # points are not allowed to be zero!
        max_points = 0.01
        max_points_p = None
        for p in remaining:
            if p.isAvailable(w):
                points = p.getPoints(w)
                if points > max_points:
                    max_points_p = p
                    max_points = points

        if max_points_p:
            logger.info('%s has a maximum of %.1f points for %s',
                        max_points_p, max_points, w)

        return max_points_p

    def sortWorkshopsByMaxPoints(self, remaining):
        points = self.getPointsPerWorkshop(remaining)
        self.workshops = sorted(points, key=points.get, reverse=True)
        logger.debug('Sorted workshops by their maximum points.')

    def calculateRemainingParticipants(self, remaining):
        """Throws all participants that are assigned out of the array"""
        for p in remaining[:]:
            if p.isFullyAssigned():
                remaining.remove(p)
                logger.debug('Participant %s is fully assigned.', p)

        return remaining

    def startDivision(self):
        """Start the division of the participants to the workshops"""
        remaining = self.participants[:]
        change = True
        while len(remaining) > 0 and change:
            # reduce the number of remaining
            self.calculateRemainingParticipants(remaining)
            self.sortWorkshopsByMaxPoints(remaining)
            change = False
            for w in self.workshops:
                participant = self.getParticipantWithMaxPoints(w, remaining)
                participant.assignWorkshop(w)
                change = True
                # if there was a change priotize again (break)
                break

        if len(remaining) > 0:
            logger.warning("Not all participants got a workshop!" +
                           "Removing assignments of these participants")
            for p in remaining:
                p.clearAssignment()
            # self.startDivision()

    def exportDays(self, filename):
        with open(filename, 'wb') as f:
            csv_writer = csv.writer(f)
            header = ["day", "workshop", "name", "stufe", "trupp", "punkte"]
            csv_writer.writerow(header)
            for d in self.available_dates:
                for w in self.workshops:
                    if w.usesDay(d):
                        participants = w.getParticipantsOfDay(d)
                        for p in participants:
                            row = [d, w.name, p.name, p.stufe, p.trupp,
                                   str(p.getPoints(w))]
                            row = [r.encode('utf-8') for r in row]
                            csv_writer.writerow(row)
