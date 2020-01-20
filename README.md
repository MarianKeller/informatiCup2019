# InformatiCup 2020
Lösungsvorschlag zur Teilnahme [InformatiCup 2020](https://github.com/informatiCup/informatiCup2020).
## Installation
### Systemvoraussetzungen
Zum Ausführen des Programms wird Python ab Version 3.5 benötigt.

### Repository klonen
Um mit den Quelldateien arbeiten zu können, wird zuerst das Repository geklont:

    git clone https://github.com/MarianKeller/informatiCup2020

### Abhängigkeiten installieren
Alle Abhängigkeiten lassen sich mit pip aus der requirements.txt installieren.

    pip install -r requirements.txt
## Server starten
Dazu wird das Skript "genetic.py" ausgeführt. Es stellt einen Server auf dem Port 50122 bereit, welcher über eine kleine REST-API wahlweise den Trainingsmodus, oder den Spielemodus startet.

    python genetic.py
Um den Trainingsmodus zu starten, ist folgender Aufruf zu verwenden:
**URL:** /main
**PORT:** 50122
**METHODE:** POST
**Erforderlich:** evolve=[] ODER play=[]
**Optional:** startFromLast=[boolean]

**Beispielaufrufe**
Trainingsmodus starten, letzte generierte Population weiterführen:

    {
    	"evolve" : "1",
    	"startFromLast" : "True"
    }
Spielemodus starten, auf Anfragen vom ic20 Client auf Port 50122 warten:

    {
    	"play" : "1"
    }
