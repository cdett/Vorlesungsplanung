import sys

from datetime import datetime
from pytz import timezone
from colorama import init
from termcolor import colored,cprint
from icalendar import Calendar
from icalendar import vDatetime, vText

#Funktion zur Erstellung eines Dictionarys der ics Dateien (Key: UID, Value: alles)
def create_ics_dict(ics_path):
    ics_data = ""
    with open(ics_path, "rb") as f:
        ics_data = f.read()
    
    cal = Calendar.from_ical(ics_data)

    ics_dict = {}
    for comp in cal.subcomponents:
        if comp.has_key("UID") and comp.has_key("LAST-MODIFIED"):
            uid = comp["UID"].to_ical().decode("utf-8")
            ics_dict[uid] = comp
    
    return ics_dict

# Funktion zur Rückgabe des Titels eines Events
def get_title(comp):
    if "SUMMARY" in comp:
        return comp["SUMMARY"].to_ical().decode("utf-8")
    return "Kein Titel"

# Funktion zur Rückgabe der Anfangszeit eines Events
def get_start_date(comp):
    if "DTSTART" in comp:
        return vDatetime.from_ical(comp["DTSTART"].to_ical().decode("utf-8")).astimezone(timezone('Europe/Berlin'))
    return "00:00"

# Funktion zur Rückgabe der Endzeit eines Events
def get_end_date(comp):
    if "DTEND" in comp:
        return vDatetime.from_ical(comp["DTEND"].to_ical().decode("utf-8")).astimezone(timezone('Europe/Berlin'))
    return "00:00"

# Funktion zur Rückgabe des Zeitpunkts der letzten Bearbeitung eines Events
def get_last_modified(comp):
    if "LAST-MODIFIED" in comp:
        return vDatetime.from_ical(comp["LAST-MODIFIED"].to_ical().decode("utf-8"))
    # bei nicht vorhandenem last-modified Datum wird ein Datum erstellt
    return datetime.fromtimestamp(0)

# Funktion zur formatierten Rückgabe des Events
def display(cal):
    return cal.to_ical().decode("utf-8").replace('\r\n', '\n').strip()

# Überprüfung, ob zwei Dateien zum Vergleich angegeben wurden
if len(sys.argv) != 3:
    print("Falsche Parameteranzahl: " + sys.argv[0] + " [alte ics datei] [neue ics datei]")
    exit()

old_file = sys.argv[1]
new_file = sys.argv[2]

old_dict = create_ics_dict(old_file)
new_dict = create_ics_dict(new_file)

# Schleife überprüft für jedes Event, ob es noch vorhanden ist und ob es bearbeitet wurde
for uid, comp in old_dict.items():
    #UID nicht im Dictionary vorhanden bedeutet, dass das Event gelöscht wurde
    init(convert = True)
    if not uid in new_dict:
        title = get_title(comp)
        start_date = get_start_date(comp)
        end_date = get_end_date(comp)
        cprint("Termin '{}' von '{}' bis '{}' wurde gelöscht!".format(title,start_date,end_date),"red")
        print(display(comp))
    else:
        new_comp = new_dict[uid]
        old_modified = get_last_modified(comp)
        new_modified = get_last_modified(new_comp)
        old_title = get_title(comp)
        #Veränderter Wert des Last-modified Parameters bedeutet, dass der Termin bearbeitet wurde
        if old_modified != new_modified:
            cprint('\n'+"Termin '{}' wurde geändert. Differenz:".format(old_title),"yellow")
            print("Alter Termin:")
            print(display(comp))
            print('\n'+"Neuer Termin:")
            print(display(new_comp))