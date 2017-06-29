from workshopdivision import WorkshopDivision

# start the workshop division
w = WorkshopDivision()
w.loadWorkshops("Workshops.csv")
# w.getWorkshopStatistics()
w.loadParticipants("Anmeldung.csv")
# w.getParticipantsStatistics()
w.startDivision()
w.exportDays("tage.csv")
w.exportWorkshops("exportedWorkshop.csv")
w.exportTrupps("trupps.csv")
