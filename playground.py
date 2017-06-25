from workshopdivision import WorkshopDivision

# start the workshop division
w = WorkshopDivision()
w.loadWorkshops("Workshops.csv")
# w.getWorkshopStatistics()
w.loadParticipants("Anmeldung.csv")
# w.getParticipantsStatistics()
w.startDivision()
