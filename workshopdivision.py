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

        with open(filename) as f:
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

        ages = [a in str_ages for a in self.available_ages]
        if len(ages) is 0:
            logger.error("No Ages!")

        dates = [d in str_dates for d in self.available_dates]
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

    def getMeanPointsPerWorkshop(self):
        """Get the mean points per workshop"""
        sum_points = 0.0
        mean_points = {w: 0.0 for w in self.workshops}
        for p in self.participants:
            for k in mean_points:
                points = p.getPoints(k)
                mean_points[k] += points
                sum_points += points
        for k in mean_points:
            mean_points[k] /= sum_points
        return mean_points

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
        print(str(w_names))

        for row in reader:
            name = row[1]
            stufe = "GuSp" if row[2] else "CaEx"
            trupp = row[3] if stufe is "GuSp" else row[4]
            points = {}
            for count, i in enumerate(name_ids):
                w = self.getWorkshop(w_names[count])
                points[w] = parseInt(row[i])
            self.addParticipant(name, stufe, trupp, points)

        # shuffle participants for randomness
        shuffle(self.participants)

    def getParticipantWithMaxPoints(self, w, remaining=None):
        """Get the participant with the maximum number of given points"""
        if remaining is None:
            remaining = self.participants
        max_points = 0
        max_points_p = None
        for p in remaining:
            if p.isAvailable(w):
                points = p.getPoints(w)
                if points > max_points:
                    max_points = points
                    max_points_p = p

        if max_points_p is not None:
            logger.debug('Participant %s has a maximum of %d points for %s',
                         max_points_p, max_points, w)

        return max_points_p

    def calculateRemainingParticipants(self, remaining):
        """Throws all participants that are assigned out of the array"""
        for p in remaining:
            if not p.isAvailable():
                remaining.remove(p)
                logger.debug('Participant %s is fully assigned.', p)

    def startDivision(self):
        """Start the division of the participants to the workshops"""
        remaining = self.participants[:]
        while len(remaining) > 0:
            for w in self.workshops:
                p = self.getParticipantWithMaxPoints(w, remaining)
                if p is not None:
                    p.assignWorkshop(w)

            self.calculateRemainingParticipants(remaining)



