from workshopdivision import WorkshopDivision

# start the workshop division
w = WorkshopDivision()
w.loadWorkshops("Workshops.csv")
# w.getWorkshopStatistics()
w.loadParticipants("Anmeldung.csv")
# w.getParticipantsStatistics()
w.startDivision()
w.exportDays("export_tage.csv")
w.exportWorkshops("export_workshop.csv")
w.exportTrupps("export_trupps.csv")
