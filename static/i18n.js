// English / German interface switch.
// How it works: the page is written in English. When German is chosen, this script replaces each English text
// (and placeholder, label and title) by its German version, now and whenever the page adds new text.
// To fix or add a German text: edit the lists D (whole texts), P (texts with numbers or names inside) or SUBST below.
// Answers from the assistant and the safety steps come from the server and stay as they are.
(function () {
  "use strict";
  var KEY = "fa-lang";

  /* ---------- whole texts: English -> German ---------- */
  var D = {
    // page header and emergency band
    "Fire Emergency Assistant": "Brandschutz-Assistent",
    "Answers from your site's approved documents and building plan. Type or speak.": "Antworten aus den freigegebenen Dokumenten und dem Gebäudeplan Ihres Standorts. Tippen oder sprechen Sie.",
    "Extinguisher training": "Löschertraining",
    "Edit plan": "Plan bearbeiten",
    "Finish editing": "Bearbeitung beenden",
    "Inspections due": "Prüfungen fällig",
    "Emergency call": "Notruf",
    "If anyone's life is at risk, call 112 first.": "Wenn jemandes Leben in Gefahr ist, rufen Sie zuerst die 112 an.",
    "Free, 24 hours, across Europe. This assistant supplements the official Brandschutzordnung and does not replace the emergency call.": "Kostenlos, rund um die Uhr, in ganz Europa. Dieser Assistent ergänzt die offizielle Brandschutzordnung und ersetzt den Notruf nicht.",
    "Call 112": "112 anrufen",

    // SOS
    "SOS for people who are trapped": "SOS für eingeschlossene Personen",
    "Cancel my SOS": "Meinen SOS abbrechen",
    "Optional: what is happening? (door blocked, smoke, injured)": "Optional: Was ist passiert? (Tür blockiert, Rauch, verletzt)",
    "What is happening": "Was ist passiert",
    "I am trapped: send SOS": "Ich bin eingeschlossen: SOS senden",
    "Tap again to send the SOS": "Zum Senden erneut tippen",
    "First tap the plan where you are. Your SOS is shown to everyone using this app. It does not call anyone: call 112 as well.": "Tippen Sie zuerst auf den Plan, wo Sie sind. Ihr SOS wird allen angezeigt, die diese App nutzen. Es ruft niemanden an: Rufen Sie auch die 112 an.",
    "Only help if it is safe. Never enter smoke or fire. Call 112 and tell them where the person is.": "Helfen Sie nur, wenn es sicher ist. Betreten Sie niemals Rauch oder Feuer. Rufen Sie die 112 an und sagen Sie, wo sich die Person befindet.",
    "Show on plan": "Im Plan zeigen",
    "I am on my way": "Ich bin unterwegs",
    "Thank you, noted": "Danke, vermerkt",
    "Remove (admin)": "Entfernen (Admin)",
    "Tap the plan where you are first, then send the SOS. If you cannot, call 112.": "Tippen Sie zuerst auf den Plan, wo Sie sind, und senden Sie dann den SOS. Wenn das nicht geht, rufen Sie die 112 an.",
    "The SOS could not be sent. Call 112.": "Der SOS konnte nicht gesendet werden. Rufen Sie die 112 an.",

    // plan
    "Building plan": "Gebäudeplan",
    "Floors": "Stockwerke",
    "Floor": "Stockwerk",
    "Ground floor": "Erdgeschoss",
    "Clear position": "Position löschen",
    "Practise with this extinguisher": "Mit diesem Feuerlöscher üben",
    "The dashed line is a straight line. Walls are not on the plan: follow corridors and escape-route signs.": "Die gestrichelte Linie ist eine Luftlinie. Wände sind nicht im Plan eingezeichnet: Folgen Sie den Fluren und der Rettungswegkennzeichnung.",
    "No building plan has been set up yet.": "Es wurde noch kein Gebäudeplan eingerichtet.",
    "Upload a plan image for this floor.": "Laden Sie ein Planbild für dieses Stockwerk hoch.",
    "No image for this floor.": "Kein Bild für dieses Stockwerk.",
    "You": "Sie",
    "SOS (you)": "SOS (Sie)",
    "The building plan could not be loaded.": "Der Gebäudeplan konnte nicht geladen werden.",
    "Pick a marker type and tap the plan. Drag markers to move them. Tap a marker to name or delete it.": "Wählen Sie einen Markierungstyp und tippen Sie auf den Plan. Ziehen Sie Markierungen, um sie zu verschieben. Tippen Sie auf eine Markierung, um sie zu benennen oder zu löschen.",
    "Create the first floor to start.": "Legen Sie zuerst ein Stockwerk an.",
    "Position set. Ask me about exits, extinguishers or the assembly point.": "Position gesetzt. Fragen Sie mich nach Ausgängen, Feuerlöschern oder dem Sammelplatz.",
    "Tap the plan where you are now, or tap a room name.": "Tippen Sie auf den Plan, wo Sie gerade sind, oder auf einen Raumnamen.",
    "Editing is locked. Enter the admin token below to change the plan.": "Die Bearbeitung ist gesperrt. Geben Sie unten den Admin-Token ein, um den Plan zu ändern.",
    "(choose your room)": "(Raum wählen)",
    "(not set)": "(nicht festgelegt)",

    // marker types and extinguisher kinds
    "Fire extinguisher": "Feuerlöscher",
    "Emergency exit": "Notausgang",
    "Stairs": "Treppe",
    "Assembly point": "Sammelplatz",
    "Alarm call point": "Handfeuermelder",
    "First aid": "Erste Hilfe",
    "Room": "Raum",
    "ABC powder": "ABC-Pulver",
    "Foam": "Schaum",
    "Grease fire (F)": "Fettbrand (F)",
    "Water": "Wasser",

    // admin editor
    "Set up the building plan": "Gebäudeplan einrichten",
    "Admin token": "Admin-Token",
    "Unlock editing": "Bearbeitung freischalten",
    "Create the first floor": "Erstes Stockwerk anlegen",
    "Draw walls": "Wände zeichnen",
    "Select wall": "Wand auswählen",
    "Add door": "Tür hinzufügen",
    "Door width (m)": "Türbreite (m)",
    "Undo last wall": "Letzte Wand rückgängig",
    "Delete selected wall": "Ausgewählte Wand löschen",
    "Draw walls: click where a wall starts, then where it ends. Walls are always drawn horizontal or vertical. Select wall: click a wall, then delete it. Add door: click on a wall to open a door there (green); click a green door again to remove it. Set the plan width in metres first. Walls are only used to work out walking routes and are not shown to employees.": "Wände zeichnen: Klicken Sie auf den Anfang einer Wand und dann auf ihr Ende. Wände werden immer waagerecht oder senkrecht gezeichnet. Wand auswählen: Klicken Sie eine Wand an und löschen Sie sie. Tür hinzufügen: Klicken Sie auf eine Wand, um dort eine Tür (grün) zu setzen; klicken Sie eine grüne Tür erneut an, um sie zu entfernen. Legen Sie zuerst die Planbreite in Metern fest. Wände dienen nur zur Berechnung von Gehwegen und werden Mitarbeitern nicht angezeigt.",
    "Print QR codes for all rooms": "QR-Codes für alle Räume drucken",
    "Label": "Bezeichnung",
    "Type": "Typ",
    "Extinguisher type": "Löscherart",
    "Next inspection due": "Nächste Prüfung fällig",
    "QR code for this room": "QR-Code für diesen Raum",
    "Delete marker": "Markierung löschen",
    "Floor name": "Stockwerkname",
    "Plan width in metres": "Planbreite in Metern",
    "Upload plan image": "Planbild hochladen",
    "Add floor": "Stockwerk hinzufügen",
    "Delete floor": "Stockwerk löschen",
    "Really delete?": "Wirklich löschen?",
    "PNG, JPG, WebP or SVG up to 10 MB. Export a PDF to an image first. The width in metres is used to estimate distances.": "PNG, JPG, WebP oder SVG bis 10 MB. Exportieren Sie ein PDF zuerst als Bild. Die Breite in Metern dient zur Schätzung von Entfernungen.",
    "Delete the whole building plan": "Gesamten Gebäudeplan löschen",
    "Click again to delete ALL floors, markers, walls and doors": "Zum Löschen ALLER Stockwerke, Markierungen, Wände und Türen erneut klicken",
    "Site name": "Standortname",
    "Company notes (assembly point, fire wardens, internal emergency number)": "Firmenhinweise (Sammelplatz, Brandschutzhelfer, interne Notrufnummer)",
    "Set the plan width in metres first, then add doors.": "Legen Sie zuerst die Planbreite in Metern fest und fügen Sie dann Türen hinzu.",
    "Click on a wall to put a door there.": "Klicken Sie auf eine Wand, um dort eine Tür zu setzen.",
    "Saved": "Gespeichert",
    "Saving …": "Speichern …",
    "Uploading …": "Hochladen …",
    "The admin token was rejected, so your changes were discarded. Unlock again.": "Der Admin-Token wurde abgelehnt, daher wurden Ihre Änderungen verworfen. Bitte erneut freischalten.",
    "Plan editing is switched off on this server. Set ADMIN_TOKEN in .env and restart.": "Die Planbearbeitung ist auf diesem Server abgeschaltet. Setzen Sie ADMIN_TOKEN in .env und starten Sie neu.",
    "Wrong admin token.": "Falscher Admin-Token.",
    "The server is not reachable.": "Der Server ist nicht erreichbar.",
    "The QR library is missing. Upload static/qrcode.js to your project and redeploy.": "Die QR-Bibliothek fehlt. Laden Sie static/qrcode.js in Ihr Projekt hoch und stellen Sie es erneut bereit.",
    "No room has a label yet. Select a room marker, give it a label, then try again.": "Noch kein Raum hat eine Bezeichnung. Wählen Sie eine Raummarkierung, vergeben Sie eine Bezeichnung und versuchen Sie es erneut.",
    "This QR code does not match a room on the plan. Tap the plan to mark where you are.": "Dieser QR-Code passt zu keinem Raum im Plan. Tippen Sie auf den Plan, um Ihren Standort zu markieren.",
    "Scan to mark where you are.": "Scannen, um Ihren Standort zu markieren.",
    "Fire: leave the building and call": "Feuer: Gebäude verlassen, Notruf",

    // chat
    "Chat": "Chat",
    "Where is …? (from your position)": "Wo ist …? (von Ihrer Position)",
    "What is happening?": "Was ist passiert?",
    "Or pick your room:": "Oder wählen Sie Ihren Raum:",
    "Ask by voice": "Per Sprache fragen",
    "Stop recording": "Aufnahme stoppen",
    
    "Ask about fire safety …": "Fragen zum Brandschutz …",
    "Read answers aloud": "Antworten vorlesen",
    "Send": "Senden",
    "Assistant": "Assistent",
    "Fire? Do this first:": "Feuer? Zuerst Folgendes tun:",
    "I found nothing about this in the approved documents.": "Dazu habe ich in den freigegebenen Dokumenten nichts gefunden.",
    "Please check your site's fire safety rules.": "Bitte prüfen Sie die Brandschutzregeln Ihres Standorts.",
    "In an emergency call 112 and follow the Brandschutzordnung.": "Rufen Sie im Notfall die 112 an und befolgen Sie die Brandschutzordnung.",
    "Searching the documents …": "Dokumente werden durchsucht …",
    "The assistant is not reachable. In an emergency call 112 and follow the Brandschutzordnung.": "Der Assistent ist nicht erreichbar. Rufen Sie im Notfall die 112 an und befolgen Sie die Brandschutzordnung.",
    "I do not know where you are yet. Tap the plan where you are, or tap a room name.": "Ich weiß noch nicht, wo Sie sind. Tippen Sie auf den Plan, wo Sie sind, oder auf einen Raumnamen.",
    "I am your fire safety assistant. If anyone is in danger: leave the area and call 112. Tap the plan where you are and I will show you exits and extinguishers from your site's plan. You can also ask me how to help others.": "Ich bin Ihr Brandschutz-Assistent. Wenn jemand in Gefahr ist: Verlassen Sie den Bereich und rufen Sie die 112 an. Tippen Sie auf den Plan, wo Sie sind, dann zeige ich Ihnen Ausgänge und Feuerlöscher aus dem Plan Ihres Standorts. Sie können mich auch fragen, wie Sie anderen helfen können.",
    "Nearest exit": "Nächster Ausgang",
    "Nearest extinguisher": "Nächster Feuerlöscher",
    "Nearest alarm button": "Nächster Alarmknopf",
    "Where is the nearest exit?": "Wo ist der nächste Ausgang?",
    "Where is the nearest fire extinguisher?": "Wo ist der nächste Feuerlöscher?",
    "Where is the assembly point?": "Wo ist der Sammelplatz?",
    "Where is the nearest alarm button?": "Wo ist der nächste Alarmknopf?",
    "Fire or smoke in the building": "Feuer oder Rauch im Gebäude",
    "Clothes on fire": "Kleidung brennt",
    "Grease fire in the kitchen": "Fettbrand in der Küche",
    "How do I use an extinguisher?": "Wie benutze ich einen Feuerlöscher?",
    "I want to help others": "Ich möchte anderen helfen",
    "There is a fire in the building. What should I do?": "Im Gebäude brennt es. Was soll ich tun?",
    "My clothes are on fire. What should I do?": "Meine Kleidung brennt. Was soll ich tun?",
    "There is a grease fire in the kitchen. What should I do?": "In der Küche gibt es einen Fettbrand. Was soll ich tun?",
    "How do I use a fire extinguisher?": "Wie benutze ich einen Feuerlöscher?",
    "How can I help others during a fire evacuation?": "Wie kann ich anderen bei einer Brandevakuierung helfen?",
    "Voice input is not supported in this browser or needs a secure (https) connection. Please type your question.": "Spracheingabe wird in diesem Browser nicht unterstützt oder braucht eine sichere (https) Verbindung. Bitte tippen Sie Ihre Frage.",
    "Microphone access was denied. Allow it in the browser, or type your question.": "Der Mikrofonzugriff wurde verweigert. Erlauben Sie ihn im Browser oder tippen Sie Ihre Frage.",
    "Transcribing …": "Wird transkribiert …",
    "I could not hear anything. Please try again or type.": "Ich konnte nichts hören. Bitte versuchen Sie es erneut oder tippen Sie.",
    "Could not transcribe the recording. Please type your question.": "Die Aufnahme konnte nicht transkribiert werden. Bitte tippen Sie Ihre Frage.",
    "Listening … tap the microphone again to send.": "Ich höre zu … tippen Sie erneut auf das Mikrofon zum Senden.",

    // reference cards and footer
    "Emergency call: the 5 Ws": "Notruf: die 5 W-Fragen",
    "Where": "Wo",
    "is the fire? Place, street, number, floor": "brennt es? Ort, Straße, Hausnummer, Stockwerk",
    "What": "Was",
    "happened? Type of fire": "ist passiert? Art des Brandes",
    "How many": "Wie viele",
    "people are affected?": "Personen sind betroffen?",
    "Which": "Welche",
    "injuries are there?": "Verletzungen gibt es?",
    "Wait": "Warten",
    "for questions. Hang up only when the dispatcher says so.": "Sie auf Rückfragen. Legen Sie erst auf, wenn die Leitstelle es sagt.",
    "Trapped?": "Eingeschlossen?",
    "Close the door and seal gaps with wet cloths": "Tür schließen und Ritzen mit nassen Tüchern abdichten",
    "Go to a window, shout and wave": "Zum Fenster gehen, rufen und winken",
    "Call 112, give exact location and floor": "112 anrufen, genauen Ort und Stockwerk nennen",
    "Never jump from a great height": "Niemals aus großer Höhe springen",
    "Stay low if smoke is in the room": "Bei Rauch im Raum tief am Boden bleiben",
    "This page gives general guidance from approved documents and does not replace the fire service or medical care. Distances on the plan are estimates. When in doubt: leave the danger area and call 112.": "Diese Seite gibt allgemeine Hinweise aus freigegebenen Dokumenten und ersetzt weder die Feuerwehr noch ärztliche Hilfe. Entfernungen im Plan sind Schätzungen. Im Zweifel: Gefahrenbereich verlassen und die 112 anrufen.",

    // access-code screen
    "Enter the access code from your company to open the assistant.": "Geben Sie den Zugangscode Ihres Unternehmens ein, um den Assistenten zu öffnen.",
    "Access code": "Zugangscode",
    "Open": "Öffnen",
    "In an emergency call 112 first.": "Rufen Sie im Notfall zuerst die 112 an.",
    "Wrong code. Please try again.": "Falscher Code. Bitte versuchen Sie es erneut.",
    "Could not reach the server. Try again.": "Der Server ist nicht erreichbar. Bitte erneut versuchen.",
    "Please enter the access code.": "Bitte geben Sie den Zugangscode ein.",

    // extinguisher game
    "Choose the right extinguisher, then use it with the PASS steps in the right order.": "Wählen Sie den richtigen Feuerlöscher und setzen Sie ihn dann mit den PASS-Schritten in der richtigen Reihenfolge ein.",
    "← Back to the assistant": "← Zurück zum Assistenten",
    "Back to the assistant": "Zurück zum Assistenten",
    "Ask the assistant": "Fragen Sie den Assistenten",
    "Questions like \"Can I use water on a laptop fire?\" are answered from your site's approved documents, with the source. If the documents say nothing, the assistant says so.": "Fragen wie „Darf ich Wasser bei einem Laptop-Brand verwenden?“ werden aus den freigegebenen Dokumenten Ihres Standorts beantwortet, mit Quellenangabe. Wenn die Dokumente nichts dazu sagen, sagt der Assistent das.",
    "Ask about extinguishers ...": "Fragen zu Feuerlöschern ...",
    "Ask": "Fragen",
    "Searching the documents ...": "Dokumente werden durchsucht ...",
    "The assistant is not reachable. In an emergency call 112.": "Der Assistent ist nicht erreichbar. Rufen Sie im Notfall die 112 an.",
    "Training only. In a real fire: raise the alarm first, fight only small fires with your exit behind you, never put yourself at risk and call 112. The label on the real extinguisher and your site's fire safety rules always come first.": "Nur zum Training. Bei einem echten Brand: zuerst Alarm auslösen, nur kleine Brände mit dem Ausgang im Rücken bekämpfen, sich niemals in Gefahr bringen und die 112 anrufen. Das Etikett des echten Feuerlöschers und die Brandschutzregeln Ihres Standorts gehen immer vor.",
    "Finished": "Beendet",
    "What do you do?": "Was tun Sie?",
    "Which extinguisher do you take?": "Welchen Feuerlöscher nehmen Sie?",
    "Leave, close the door, raise the alarm, call 112": "Gehen, Tür schließen, Alarm auslösen, 112 anrufen",
    "Correct: you got out safely.": "Richtig: Sie sind sicher hinausgekommen.",
    "The fire is out.": "Das Feuer ist aus.",
    "Not the right choice. The fire gets worse.": "Nicht die richtige Wahl. Das Feuer wird schlimmer.",
    "You lose a life.": "Sie verlieren ein Leben.",
    "See results": "Ergebnisse ansehen",
    "Next scenario": "Nächstes Szenario",
    "Game over": "Spiel vorbei",
    "Training complete": "Training abgeschlossen",
    "Which extinguisher for what": "Welcher Feuerlöscher wofür",
    "Paper, wood": "Papier, Holz",
    "Liquids": "Flüssigkeiten",
    "Live electrical": "Elektrisch unter Spannung",
    "Cooking oil": "Speiseöl",
    "Yes": "Ja",
    "No": "Nein",
    "Works": "Möglich",
    "Wet chemical (F)": "Fettbrandlöscher (F)",
    "General guidance. Always read the label of the real extinguisher. Wet chemical on solids is limited. CO₂ and powder on liquids work only on small fires.": "Allgemeine Hinweise. Lesen Sie immer das Etikett des echten Feuerlöschers. Fettbrandlöscher sind bei festen Stoffen nur eingeschränkt wirksam. CO₂ und Pulver wirken bei Flüssigkeiten nur bei kleinen Bränden.",
    "Play again": "Nochmal spielen",
    "Scene": "Szene",
    "Left the building: correct (+100)": "Gebäude verlassen: richtig (+100)",

    // extinguisher kinds shown with a short note
    "solids": "feste Stoffe",
    "solids and liquids": "feste Stoffe und Flüssigkeiten",
    "solids, liquids, gases": "feste Stoffe, Flüssigkeiten, Gase",
    "electrical, small liquid fires": "Elektrobrände, kleine Flüssigkeitsbrände",
    "cooking oil and fat": "Speiseöl und Fett",

    // PASS steps
    "Pull": "Pull · Ziehen",
    "Aim": "Aim · Zielen",
    "Squeeze": "Squeeze · Drücken",
    "Sweep": "Sweep · Schwenken",
    "Pull the safety pin and break the seal.": "Sicherungsstift ziehen und Plombe aufbrechen.",
    "Aim the nozzle at the base of the flames, not the top.": "Düse auf den Brandherd richten, nicht auf die Flammenspitzen.",
    "Squeeze the handle to release the agent.": "Hebel drücken, um das Löschmittel freizugeben.",
    "Sweep from side to side across the base until the fire is out.": "Seitlich über den Brandherd schwenken, bis das Feuer aus ist.",
    "Start at the near edge and work forward.": "Am vorderen Rand beginnen und nach hinten vorarbeiten.",
    "Let the foam fall on the surface.": "Den Schaum auf die Oberfläche fallen lassen.",
    "Do not blast it straight into a burning liquid.": "Nicht direkt in die brennende Flüssigkeit spritzen.",
    "Powder makes a cloud: keep your back to the exit and hold your breath if you can.": "Pulver bildet eine Wolke: Den Ausgang im Rücken behalten und wenn möglich die Luft anhalten.",
    "Hold only the insulated handle.": "Nur den isolierten Griff halten.",
    "The horn becomes freezing cold.": "Das Schneerohr wird eiskalt.",
    "CO₂ has a short range: stay close, about 1 m.": "CO₂ hat eine kurze Reichweite: nah herangehen, etwa 1 m.",
    "Use a gentle, sweeping stream.": "Sanft und schwenkend sprühen.",
    "Never splash the hot oil.": "Das heiße Öl niemals verspritzen.",

    // scenario 1
    "Boxes in the storage room": "Kartons im Lagerraum",
    "Storage room": "Lagerraum",
    "A stack of cardboard boxes is burning, knee-high.": "Ein kniehoher Stapel Kartons brennt.",
    "The exit is behind you and there is little smoke.": "Der Ausgang liegt hinter Ihnen und es gibt wenig Rauch.",
    "Water cools burning paper and cardboard (a solid fire, class A).": "Wasser kühlt brennendes Papier und Pappe (ein Feststoffbrand, Brandklasse A).",
    "Foam also works on solids, but plain water is the simple choice here.": "Schaum wirkt auch bei festen Stoffen, aber einfaches Wasser ist hier die naheliegende Wahl.",
    "Powder works on solids, but it makes a mess and does not cool.": "Pulver wirkt bei festen Stoffen, macht aber Schmutz und kühlt nicht.",
    "Acceptable, not the best.": "Vertretbar, aber nicht die beste Wahl.",
    "CO₂ only blows the flames away and does not cool.": "CO₂ bläst die Flammen nur weg und kühlt nicht.",
    "Cardboard glows on and reignites.": "Pappe glimmt weiter und entzündet sich neu.",
    "Wet chemical is made for cooking oil and fat.": "Fettbrandlöscher sind für Speiseöl und Fett gemacht.",
    "It is the wrong tool for cardboard.": "Für Pappe ist er das falsche Mittel.",

    // scenario 2
    "Server rack on fire": "Brennender Serverschrank",
    "Server room": "Serverraum",
    "A computer rack is burning.": "Ein Rechnerschrank brennt.",
    "The equipment is still powered.": "Die Geräte stehen noch unter Strom.",
    "The fire is small and the exit is behind you.": "Das Feuer ist klein und der Ausgang liegt hinter Ihnen.",
    "If you can do it safely, switch off the power.": "Wenn es gefahrlos möglich ist, den Strom abschalten.",
    "CO₂ leaves no residue and does not conduct electricity.": "CO₂ hinterlässt keine Rückstände und leitet keinen Strom.",
    "The best choice for live electrical equipment.": "Die beste Wahl für Elektrogeräte unter Spannung.",
    "Powder can be used on electrical fires, but it ruins the electronics.": "Pulver kann bei Elektrobränden eingesetzt werden, zerstört aber die Elektronik.",
    "Water conducts electricity: you could get an electric shock.": "Wasser leitet Strom: Sie könnten einen Stromschlag erleiden.",
    "Never use it on live equipment.": "Niemals bei Geräten unter Spannung verwenden.",
    "Foam contains water and can conduct electricity.": "Schaum enthält Wasser und kann Strom leiten.",
    "Not for live equipment.": "Nicht für Geräte unter Spannung.",
    "Wet chemical is for cooking oil and fat, and it is not safe on live equipment.": "Fettbrandlöscher sind für Speiseöl und Fett und bei Geräten unter Spannung nicht sicher.",

    // scenario 3
    "Pan of burning oil": "Pfanne mit brennendem Öl",
    "Kitchen": "Küche",
    "Oil in a frying pan has caught fire.": "Öl in einer Bratpfanne hat Feuer gefangen.",
    "Do not move the pan.": "Bewegen Sie die Pfanne nicht.",
    "The exit is behind you.": "Der Ausgang liegt hinter Ihnen.",
    "Never carry the pan and never use water.": "Tragen Sie die Pfanne niemals weg und verwenden Sie niemals Wasser.",
    "Wet chemical forms a soapy layer on the hot oil that seals and cools it.": "Fettbrandlöscher bilden auf dem heißen Öl eine seifige Schicht, die es abdeckt und kühlt.",
    "Made for exactly this.": "Genau dafür gemacht.",
    "NEVER water on burning oil: it turns to steam and throws burning oil up as a fireball.": "NIEMALS Wasser auf brennendes Öl: Es verdampft schlagartig und schleudert das brennende Öl als Feuerball hoch.",
    "Foam can splash the burning oil around.": "Schaum kann das brennende Öl verspritzen.",
    "Use wet chemical (F).": "Verwenden Sie einen Fettbrandlöscher (F).",
    "Powder may knock down the flames, but the oil stays hot and flares up again.": "Pulver kann die Flammen niederschlagen, aber das Öl bleibt heiß und flammt wieder auf.",
    "CO₂ can blow burning oil out of the pan, and it does not cool the oil.": "CO₂ kann brennendes Öl aus der Pfanne blasen und kühlt das Öl nicht.",

    // scenario 4
    "Spilled solvent in the workshop": "Verschüttetes Lösungsmittel in der Werkstatt",
    "Workshop": "Werkstatt",
    "A puddle of solvent on the floor is burning.": "Eine Lache Lösungsmittel auf dem Boden brennt.",
    "Foam floats on the liquid and smothers it, so it cannot reignite (a liquid fire, class B).": "Schaum schwimmt auf der Flüssigkeit und erstickt das Feuer, sodass es nicht wieder aufflammt (Flüssigkeitsbrand, Brandklasse B).",
    "Powder works on liquid fires.": "Pulver wirkt bei Flüssigkeitsbränden.",
    "Acceptable, but the fire can flare up again.": "Vertretbar, aber das Feuer kann wieder aufflammen.",
    "CO₂ works on small liquid fires, but it has a short range and no lasting effect.": "CO₂ wirkt bei kleinen Flüssigkeitsbränden, hat aber geringe Reichweite und keine Dauerwirkung.",
    "Water sinks under the solvent and spreads the burning liquid.": "Wasser sinkt unter das Lösungsmittel und verteilt die brennende Flüssigkeit.",
    "Do not use it.": "Nicht verwenden.",
    "Wet chemical is for cooking oil and fat, not for solvents.": "Fettbrandlöscher sind für Speiseöl und Fett, nicht für Lösungsmittel.",

    // scenario 5
    "Shelves with paint cans": "Regale mit Farbdosen",
    "Garage store": "Garagenlager",
    "Wooden shelves with paint cans are burning.": "Holzregale mit Farbdosen brennen.",
    "Wood and liquids are both on fire.": "Holz und Flüssigkeiten brennen gleichzeitig.",
    "ABC powder covers solids, liquids and gases at once: the right choice when different materials burn.": "ABC-Pulver deckt feste Stoffe, Flüssigkeiten und Gase gleichzeitig ab: die richtige Wahl, wenn verschiedene Materialien brennen.",
    "Foam works on both wood and liquids.": "Schaum wirkt bei Holz und Flüssigkeiten.",
    "Acceptable, though powder is more flexible.": "Vertretbar, aber Pulver ist vielseitiger.",
    "Water helps with wood but spreads the burning paint.": "Wasser hilft bei Holz, verteilt aber die brennende Farbe.",
    "Not suitable.": "Nicht geeignet.",
    "CO₂ does not cool the wood, so the shelves reignite.": "CO₂ kühlt das Holz nicht, daher entzünden sich die Regale neu.",
    "Wet chemical is for cooking oil and fat only.": "Fettbrandlöscher sind nur für Speiseöl und Fett.",

    // scenario 6
    "The fire is too big": "Das Feuer ist zu groß",
    "Open office": "Großraumbüro",
    "The fire has reached the ceiling and thick black smoke is filling the room.": "Das Feuer hat die Decke erreicht und dichter schwarzer Rauch füllt den Raum.",
    "You have one extinguisher in your hand.": "Sie haben einen Feuerlöscher in der Hand.",
    "Right.": "Richtig.",
    "A fire this size cannot be fought with an extinguisher.": "Ein Feuer dieser Größe lässt sich nicht mit einem Feuerlöscher bekämpfen.",
    "Raise the alarm, close the door behind you, leave and call 112.": "Alarm auslösen, die Tür hinter sich schließen, das Gebäude verlassen und die 112 anrufen.",
    "The fire is too big, and the smoke is already dangerous.": "Das Feuer ist zu groß und der Rauch ist bereits gefährlich.",
    "Leave instead.": "Verlassen Sie stattdessen das Gebäude."
  };

  var NAME = { "Water": "Wasser", "Foam": "Schaum", "ABC powder": "ABC-Pulver", "CO₂": "CO₂", "Wet chemical (F)": "Fettbrandlöscher (F)" };
  function nm(x) { return NAME[x] || D[x] || x; }

  /* ---------- texts with numbers or names inside: [pattern, function(match) -> German] ---------- */
  var P = [
    [/^Position set\.(\n\([\s\S]*\))? Ask me about exits, extinguishers or the assembly point\.$/, function (m) { return "Position gesetzt." + (m[1] || "") + " Fragen Sie mich nach Ausgängen, Feuerlöschern oder dem Sammelplatz."; }],
    [/^Floor (\d+)$/, function (m) { return "Stockwerk " + m[1]; }],
    [/^Room(: ([\s\S]*))?$/, function (m) { return "Raum" + (m[1] || ""); }],
    [/^Sources: ([\s\S]*)$/, function (m) { return "Quellen: " + m[1]; }],
    [/^Saving failed: ([\s\S]*)$/, function (m) { return "Speichern fehlgeschlagen: " + m[1]; }],
    [/^Upload failed: ([\s\S]*)$/, function (m) { return "Hochladen fehlgeschlagen: " + m[1]; }],
    [/^The QR codes could not be made: ([\s\S]*)$/, function (m) { return "Die QR-Codes konnten nicht erstellt werden: " + m[1]; }],
    [/^You opened the app on this computer \(([\s\S]*?)\)\. The QR codes would only work here\. Open the live web address and print from there\. Print anyway\?$/, function (m) { return "Sie haben die App auf diesem Computer geöffnet (" + m[1] + "). Die QR-Codes würden nur hier funktionieren. Öffnen Sie die Internetadresse der Live-Version und drucken Sie von dort. Trotzdem drucken?"; }],
    [/^(\d+) overdue, (\d+) due soon: inspection needed$/, function (m) { return m[1] + " überfällig, " + m[2] + " bald fällig: Prüfung nötig"; }],
    [/^(\d+) inspection\(s\) due within 30 days$/, function (m) { return m[1] + " Prüfung(en) innerhalb von 30 Tagen fällig"; }],
    [/^Your SOS is on the plan\. (?:(\d+) colleague\(s\) are on the way\.|Nobody has answered yet\.) Call 112 and stay where you are if you can\.$/, function (m) { return "Ihr SOS ist im Plan eingetragen. " + (m[1] ? m[1] + " Kollege(n) sind unterwegs." : "Noch niemand hat geantwortet.") + " Rufen Sie die 112 an und bleiben Sie, wenn möglich, wo Sie sind."; }],
    [/^SOS near [\s\S]*$|^SOS(?: \([^)]*\))?, (?:just now|\d+ min ago)[\s\S]*$/, function (m) {
      return m[0].replace(/^SOS near /, "SOS bei ").replace(/, just now/, ", gerade eben").replace(/, (\d+) min ago/, ", vor $1 Min.").replace(/ · (\d+) on the way$/, " · $1 unterwegs"); }],
    // game
    [/^Scenario (\d+) of (\d+)$/, function (m) { return "Szenario " + m[1] + " von " + m[2]; }],
    [/^Score (\d+)$/, function (m) { return "Punkte " + m[1]; }],
    [/^(\d) lives left$/, function (m) { return m[1] + " Leben übrig"; }],
    [/^(\d) of 3 stars$/, function (m) { return m[1] + " von 3 Sternen"; }],
    [/^Score (\d+)\. (\d+) of (\d+) scenarios solved\.$/, function (m) { return "Punkte " + m[1] + ". " + m[2] + " von " + m[3] + " Szenarien gelöst."; }],
    [/^Tip: ([\s\S]*)$/, function (m) { return "Tipp: " + tr(m[1], true); }],
    [/^(\d)\. (Pull|Aim|Squeeze|Sweep)$/, function (m) { return m[1] + ". " + D[m[2]]; }],
    [/^Wrong choice: (.*) \(0\)$/, function (m) { return "Falsche Wahl: " + (m[1] === "left too early" ? "zu früh gegangen" : nm(m[1])) + " (0)"; }],
    [/^(Best choice|Acceptable choice)(, fire out(?:, (\d+) order mistake\(s\))?) \(\+(\d+)\)$/, function (m) {
      return (m[1] === "Best choice" ? "Beste Wahl" : "Vertretbare Wahl") + ", Feuer aus" + (m[3] !== undefined ? ", " + m[3] + " Reihenfolgefehler" : "") + " (+" + m[4] + ")"; }],
    [/^(.*?): you already know the PASS steps \(Pull, Aim, Squeeze, Sweep\), so no quiz this time\.$/, function (m) { return nm(m[1]) + ": Sie kennen die PASS-Schritte bereits (Pull, Aim, Squeeze, Sweep), daher diesmal kein Quiz."; }],
    [/^(.*?) will work, though it is not the best choice\. Now use it: tap the steps in the right order \(P, A, S, S\)\.$/, function (m) { return nm(m[1]) + " funktioniert, ist aber nicht die beste Wahl. Setzen Sie ihn jetzt ein: Tippen Sie die Schritte in der richtigen Reihenfolge an (P, A, S, S)."; }],
    [/^Good choice: (.*?)\. Now tap the steps in the right order \(P, A, S, S\)\.$/, function (m) { return "Gute Wahl: " + nm(m[1]) + ". Tippen Sie jetzt die Schritte in der richtigen Reihenfolge an (P, A, S, S)."; }],
    [/^Not yet\. Next is step (\d) of P-A-S-S: Pull, Aim, Squeeze, Sweep\.$/, function (m) { return "Noch nicht. Als Nächstes kommt Schritt " + m[1] + " von P-A-S-S: Pull, Aim, Squeeze, Sweep."; }],
    [/^(\n?)Best choice here: (.*?)\. ([\s\S]*)$/, function (m) { return m[1] + "Beste Wahl hier: " + nm(m[2]) + ". " + tr(m[3], true); }],
    [/^(\n?)The right move: (.*?)\. ([\s\S]*)$/, function (m) { return m[1] + "Richtig wäre: " + (m[2] === "leave and call 112" ? "gehen und die 112 anrufen" : nm(m[2])) + ". " + tr(m[3], true); }],
    [/^\nYou lose a life\.$/, function () { return "\nSie verlieren ein Leben."; }]
  ];

  /* ---------- phrases inside longer text (used outside chat bubbles only) ---------- */
  var SUBST = [
    [/about (\d+) m in a straight line \(ask me for the walking route\), /g, "etwa $1 m Luftlinie (fragen Sie mich nach dem Gehweg), "],
    [/about (\d+) m, /g, "etwa $1 m, "],
    [/to the right on the plan/g, "im Plan nach rechts"],
    [/down and right on the plan/g, "im Plan nach rechts unten"],
    [/down and left on the plan/g, "im Plan nach links unten"],
    [/down on the plan/g, "im Plan nach unten"],
    [/to the left on the plan/g, "im Plan nach links"],
    [/up and left on the plan/g, "im Plan nach links oben"],
    [/up and right on the plan/g, "im Plan nach rechts oben"],
    [/up on the plan/g, "im Plan nach oben"],
    [/\(ABC powder\)/g, "(ABC-Pulver)"], [/\(Foam\)/g, "(Schaum)"], [/\(Water\)/g, "(Wasser)"], [/\(Grease fire \(F\)\)/g, "(Fettbrand (F))"],
    [/Fire extinguisher/g, "Feuerlöscher"], [/Emergency exit/g, "Notausgang"], [/Alarm call point/g, "Handfeuermelder"],
    [/Assembly point/g, "Sammelplatz"], [/First aid/g, "Erste Hilfe"], [/\bStairs\b/g, "Treppe"],
    [/overdue by (\d+) day\(s\)/g, "seit $1 Tag(en) überfällig"],
    [/due today/g, "heute fällig"],
    [/due in (\d+) day\(s\)/g, "fällig in $1 Tag(en)"]
  ];

  /* ---------- translation ---------- */
  function has(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }
  function bySentence(core) {                          // a text made of known sentences
    var parts = core.split(/((?<=[.!?])\s+)/);
    if (parts.length < 3) return null;
    var out = [];
    for (var i = 0; i < parts.length; i++) {
      if (i % 2) { out.push(parts[i]); continue; }
      if (!has(D, parts[i])) return null;
      out.push(D[parts[i]]);
    }
    return out.join("");
  }
  function inner(core, restricted) {
    if (has(D, core)) return D[core];
    for (var i = 0; i < P.length; i++) { var m = P[i][0].exec(core); if (m) return P[i][1](m); }
    var s = bySentence(core);
    if (s !== null) return s;
    if (!restricted) { var t = core; for (var j = 0; j < SUBST.length; j++) t = t.replace(SUBST[j][0], SUBST[j][1]); return t; }
    return core;
  }
  function tr(s, restricted) {
    var m = /^(\s*)([\s\S]*?)(\s*)$/.exec(s);
    if (!m || !m[2]) return s;
    var out = inner(m[2], restricted);
    return out === m[2] ? s : m[1] + out + m[3];
  }

  /* ---------- walking the page ---------- */
  var lang = "en";
  var RESTRICT = ".msg, #ans, option, .mk.t-room, #sos-list";   // text that may come from people or the server: whole-text matches only
  var SKIP = "script, style, textarea, #siteinfo, [data-notr]";
  var SKIPA = "script, style, #siteinfo, [data-notr]";
  var ATTRS = ["placeholder", "aria-label", "title", "alt"];
  var textRec = new WeakMap(), attrRec = new WeakMap();
  var busy = false, obs = null;

  function skipEl(el) { return !el || (el.closest && el.closest(SKIP)); }
  function restricted(el) { return !!(el && el.closest && el.closest(RESTRICT)); }

  function doText(node) {
    var el = node.parentNode;
    if (!el || skipEl(el)) return;
    var rec = textRec.get(node), v = node.nodeValue;
    if (rec && rec.de !== null && v === rec.de) return;      // already German
    if (lang !== "de") { textRec.set(node, { en: v, de: null }); return; }
    var de = tr(v, restricted(el));
    textRec.set(node, { en: v, de: de === v ? null : de });
    if (de !== v) node.nodeValue = de;
  }
  function doAttrs(el) {
    if (!el || (el.closest && el.closest(SKIPA))) return;
    var rec = attrRec.get(el) || {};
    ATTRS.forEach(function (a) {
      if (!el.hasAttribute(a)) return;
      var v = el.getAttribute(a), r = rec[a];
      if (r && r.de !== null && v === r.de) return;
      if (lang !== "de") { rec[a] = { en: v, de: null }; return; }
      var de = tr(v, restricted(el));
      rec[a] = { en: v, de: de === v ? null : de };
      if (de !== v) el.setAttribute(a, de);
    });
    attrRec.set(el, rec);
  }
  function walk(root) {
    if (!root) return;
    if (root.nodeType === 3) { doText(root); return; }
    if (root.nodeType !== 1) return;
    doAttrs(root);
    var w = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, null), n;
    while ((n = w.nextNode())) { if (n.nodeType === 3) doText(n); else doAttrs(n); }
  }
  function restoreAll() {                                  // back to English
    var w = document.createTreeWalker(document.documentElement, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, null), n;
    while ((n = w.nextNode())) {
      if (n.nodeType === 3) {
        var r = textRec.get(n);
        if (r && r.de !== null && n.nodeValue === r.de) n.nodeValue = r.en;
        textRec.delete(n);
      } else {
        var ar = attrRec.get(n);
        if (ar) Object.keys(ar).forEach(function (a) { if (ar[a].de !== null && n.getAttribute(a) === ar[a].de) n.setAttribute(a, ar[a].en); });
        attrRec.delete(n);
      }
    }
  }
  function run(fn) { busy = true; try { fn(); } finally { if (obs) obs.takeRecords(); busy = false; } }

  function onMutations(list) {
    if (busy) return;
    run(function () {
      list.forEach(function (m) {
        if (m.type === "childList") m.addedNodes.forEach(walk);
        else if (m.type === "characterData") doText(m.target);
        else if (m.type === "attributes") doAttrs(m.target);
      });
    });
  }

  function paintButton() {
    var b = document.getElementById("fa-lang-btn"); if (!b) return;
    b.textContent = lang === "de" ? "English" : "Deutsch";
    b.setAttribute("aria-label", lang === "de" ? "Switch the language to English" : "Sprache auf Deutsch umstellen");
    b.setAttribute("lang", lang === "de" ? "en" : "de");
  }
  function setLang(l, save) {
    lang = l === "de" ? "de" : "en";
    if (save) { try { localStorage.setItem(KEY, lang); } catch (e) {} }
    document.documentElement.setAttribute("lang", lang);
    run(function () {
      restoreAll();
      if (lang === "de") walk(document.documentElement);
      paintButton();
    });
  }
  function addButton() {
    if (document.getElementById("fa-lang-btn")) return;
    var b = document.createElement("button");
    b.type = "button"; b.id = "fa-lang-btn"; b.className = "btn"; b.setAttribute("data-notr", "");
    b.addEventListener("click", function () { setLang(lang === "de" ? "en" : "de", true); });
    var head = document.querySelector("header.top"), box = head && head.querySelector("div:last-of-type");
    if (head && box && head.children.length > 1 && box.querySelector("a,button")) box.insertBefore(b, box.firstChild);
    else if (head) head.appendChild(b);
    else { b.style.cssText = "position:fixed;top:8px;right:8px;z-index:9999"; document.body.appendChild(b); }
  }

  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  var start = saved === "de" || saved === "en" ? saved : ((navigator.language || "").toLowerCase().indexOf("de") === 0 ? "de" : "en");

  window.I18N = { get lang() { return lang; }, set: function (l) { setLang(l, true); }, tr: function (s) { return lang === "de" ? tr(s, true) : s; } };

  function init() {
    addButton();
    obs = new MutationObserver(onMutations);
    obs.observe(document.documentElement, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS });
    setLang(start, false);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();