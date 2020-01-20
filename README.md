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
## Benutzung
### Server starten
Dazu wird das Skript "genetic.py" ausgeführt. Es stellt einen Server auf dem Port 50122 bereit, welcher über eine kleine REST-API wahlweise den Trainingsmodus, oder den Spielemodus startet.

    python genetic.py

### REST-API

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
Spielemodus starten, auf Anfragen vom ic20 Client auf Port 50122 unter /play warten:

    {
    	"play" : "1"
    }
### Testen
Bisher steht mangels ausreichender Rechenzeit noch kein ausreichend gutes Genom zur Verfügung. Es ist empfehlenswert, vorher einige weitere Generationen im Trainingsmodus zu erzeugen um die Leistung zu verbessern.
Der IC20 client ist, falls der Server lokal läuft, zum Beispiel folgendermaßen zu starten:

    ic20_windows -u http://localhost:50122/play

## Deployment mit Docker
Sollte Docker installiert sein, lässt sich mit folgenden Befehlen ein Docker container erzeugen und aufrufen:

    docker build -t informaticup2020:latest .
    docker run -d -p informaticup2020
