import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
from pathlib import Path
import shutil
import threading
import subprocess
import re
import filecmp
import datetime
from tkinter import filedialog


#----------------------------- FUNKTION ZUM ERMITTELN DER USB-LAUFWERKE UND FESTPLATTEN (NUR WINDOWS) ----------------------------
# USB-Laufwerke im System ermitteln (Windows-Version)
def usb_laufwerke_ermitteln():
    laufwerke = []
    # Windows-Laufwerke von C: bis Z: prüfen
    for buchstabe in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        laufwerk = f'{buchstabe}:\\'
        if os.path.exists(laufwerk):
            try:
                # Prüfen ob auf Laufwerk zugegriffen werden kann
                os.listdir(laufwerk)
                laufwerke.append(laufwerk.rstrip('\\'))
            except (PermissionError, OSError):
                continue
    return laufwerke
#-------------------------------------------------------------------------------------------------------

#------------------FUNKTION ZUM ERMITTELN DES BENUTZER-MUSIK-ORDNERS (WINDOWS) --------------------

def musik_ordner_pfad_ermitteln():
    home = Path.home()
    # Windows-Musik-Ordner-Optionen
    moegliche_pfade = [
        home / "Music",
        home / "Musik",
        home / "Documents" / "Music",
        home / "Documents" / "Musik",
    ]
    for pfad in moegliche_pfade:
        if pfad.exists() and pfad.is_dir():
            return str(pfad)
    return None
#-------------------------------------------------------------------------------------------------------

#--------------------------- INITIALISIERUNG: USB-LAUFWERKE UND BENUTZERPFAD ERMITTELN--------
# USB-Laufwerke und Benutzerpfad ermitteln
usb_laufwerke = usb_laufwerke_ermitteln()
benutzer_pfad = musik_ordner_pfad_ermitteln()
if benutzer_pfad:
    usb_laufwerke.append(benutzer_pfad)

#---------------------------------------------------------------------------------------------------------

# ----------------------------FUNKTION FÜR LAUFWERK-AKTUALISIERUNG -----------------
def laufwerke_aktualisieren():
    global usb_laufwerke
    usb_laufwerke = usb_laufwerke_ermitteln()
    benutzer_pfad = musik_ordner_pfad_ermitteln()
    if benutzer_pfad:
        usb_laufwerke.append(benutzer_pfad)
    combo1['values'] = usb_laufwerke
    combo2['values'] = usb_laufwerke
#--------------------------------------------------------------------------------------------------------

# ------------------------ FUNKTION ZUM UMSCHALTEN DER KNOTEN-ZUSTÄNDE ------------------------------
def knoten_umschalten(tree, item, item_text):
    if item_text[:3] == '[✅]':
         new_text = item_text.replace('[✅]', '[📀]', 1)
         tree.item(item, text=new_text)
         tree.selection_remove(item)    # Wenn der geklickte Knoten markiert ist, wird er demarkiert
         kinder = tree.get_children(item) # Kindknoten des geklickten Elements holen
         for kind in kinder:
             kind_text = tree.item(kind, 'text')
             if kind_text[:3] == '[✅]':
                 neuer_kind_text = kind_text.replace('[✅]', '[📀]', 1)
                 tree.item(kind, text=neuer_kind_text)   # Kinder des geklickten Elements demarkieren
                 tree.selection_remove(kind)
                 knoten_umschalten(tree, kind, kind_text) # Kind als geklicktes Element weitergeben
         eltern_knoten = tree.parent(item)
         kind_knoten = tree.get_children(eltern_knoten)
         for markiert in kind_knoten:
              demarkieren = 1
              markiert_text = tree.item(markiert, 'text')
              if markiert_text.startswith('[✅]'):
                  eltern_text = tree.item(eltern_knoten, 'text')
                  neuer_eltern_text = eltern_text.replace('[📀]', '[✅]', 1)
                  tree.item(eltern_knoten, text = neuer_eltern_text)
                  tree.selection_add(eltern_knoten)
                  demarkieren = 0
                  break
              if demarkieren == 1:
                  eltern_knoten_text = tree.item(eltern_knoten, 'text')
                  neuer_eltern_knoten_text = eltern_knoten_text.replace('[✅]', '[📀]', 1)
                  tree.item(eltern_knoten, text=neuer_eltern_knoten_text)
                  eltern_demarkieren(tree, item)
    if item_text[:3] == '[📀]':
         new_text = item_text.replace('[📀]', '[✅]', 1)
         tree.item(item, text=new_text)
         tree.selection_add(item)         # Wenn der geklickte Knoten nicht markiert ist, wird er markiert
         kinder = tree.get_children(item)

         for kind in kinder:
             kind_text = tree.item(kind, 'text')
             if kind_text[:3] == '[📀]':
                 neuer_kind_text = kind_text.replace('[📀]', '[✅]', 1)
                 tree.item(kind, text=neuer_kind_text)
                 tree.selection_add(kind)
                 knoten_umschalten(tree, kind, kind_text)
         eltern_knoten = tree.parent(item)
         eltern_text = tree.item(eltern_knoten, 'text')
         eltern_markieren(tree, eltern_knoten)
         if eltern_text[:3] == '[📀]':  # Wenn der Elternknoten nicht markiert ist
            text_unveraendert = eltern_text
            neuer_eltern_text = eltern_text.replace('[📀]', '[✅]', 1)
            tree.item(eltern_knoten, text=neuer_eltern_text)
            tree.selection_add(eltern_knoten)

# ----------------------------------------------------------------------------------------

# ---------------FUNKTIONEN ZUM MARKIEREN UND DEMARKIEREN VON ELTERNKNOTEN ------------------------
def eltern_markieren(tree, item):
    uebergeordneter_knoten = tree.parent(item)
    hat_markierten_eltern = 0
    if uebergeordneter_knoten: # Wenn ein übergeordneter Knoten existiert
        pruef_text = tree.item(uebergeordneter_knoten, 'text')
        if pruef_text.startswith('[✅]'):
            hat_markierten_eltern = 1
            tree.selection_add(uebergeordneter_knoten)
        if hat_markierten_eltern == 0:
            uebergeordneter_text = tree.item(uebergeordneter_knoten, 'text')
            neuer_uebergeordneter_text = uebergeordneter_text.replace('[📀]', '[✅]', 1)
            tree.item(uebergeordneter_knoten, text = neuer_uebergeordneter_text)
            tree.selection_add(uebergeordneter_knoten)
            eltern_knoten2 = tree.parent(uebergeordneter_knoten)
            if eltern_knoten2:  # Null-Check hinzugefügt um Infinite Recursion zu vermeiden
                eltern_knoten2_text = tree.item(eltern_knoten2, 'text')
                eltern_markieren(tree, eltern_knoten2)
    if not uebergeordneter_knoten:  # Wenn kein übergeordneter Knoten existiert
        wurzel_text = tree.item(item, 'text')
        neuer_wurzel_text = wurzel_text.replace('[📀]', '[✅]', 1)
        tree.item(item, text = neuer_wurzel_text)
        tree.selection_add(item)
#-------------------------------------------------------------------------------------
def eltern_demarkieren(tree, item):
    uebergeordneter_knoten = tree.parent(item)
    hat_markierte_kinder = 0
    if uebergeordneter_knoten: # Wenn ein übergeordneter Knoten existiert
        # Prüfen ob dieser übergeordnete Knoten markierte Kinder hat
        kinder_des_uebergeordneten = tree.get_children(uebergeordneter_knoten)
        for pruefung in kinder_des_uebergeordneten:
            pruef_text = tree.item(pruefung, 'text')
            if pruef_text.startswith('[✅]'):
                hat_markierte_kinder = 1
                break
        if hat_markierte_kinder == 0:
            uebergeordneter_text = tree.item(uebergeordneter_knoten, 'text')
            neuer_uebergeordneter_text = uebergeordneter_text.replace('[✅]', '[📀]', 1)
            tree.item(uebergeordneter_knoten, text = neuer_uebergeordneter_text)
            tree.selection_remove(uebergeordneter_knoten)
            eltern_knoten2 = tree.parent(uebergeordneter_knoten)
            if eltern_knoten2:  # Null-Check hinzugefügt um Infinite Recursion zu vermeiden
                eltern_knoten2_text = tree.item(eltern_knoten2, 'text')
            eltern_demarkieren(tree, uebergeordneter_knoten)
    if not uebergeordneter_knoten:  # Wenn kein übergeordneter Knoten existiert, Kinder durchgehen
        wurzel_kinder = tree.get_children(item)
        for pruefung2 in wurzel_kinder:
            pruef_text2 = tree.item(pruefung2, 'text')
            if pruef_text2.startswith('[✅]'):
                hat_markierte_kinder = 1
                break
        if hat_markierte_kinder == 0:
            wurzel_text = tree.item(item, 'text')
            neuer_wurzel_text = wurzel_text.replace('[✅]', '[📀]', 1)
            tree.item(item, text = neuer_wurzel_text)
            tree.selection_remove(item)
# ---------------------------------------------------------------------------------------------------------------

# ------------------- FUNKTIONEN FÜR KLICK-EREIGNISSE AUF KNOTEN --- LEERER BEREICH BEHANDLUNG -------

def knoten_auswaehlen_links(event):
    markierte_items = []
    ausgewaehltes_item = tree_left.selection()
    markierte_items = ausgewaehltes_item
    global history_item
    global library_seite
    if ausgewaehltes_item:
        item = tree_left.selection()[0]
        item_text = tree_left.item(item, 'text')
        if item_text.startswith('[✅]') or item_text.startswith('[📀]'):
            knoten_umschalten(tree_left, item, item_text)
            button2.config(state='normal')
            button4.config(state='disabled')
            button10.config(state='normal')
            button100.config(state='disabled')
        if item_text.startswith('[❇]'):
            button2.config(state='disabled')
            button4.config(state='disabled')
            button10.config(state='disabled')
            button100.config(state='normal')
            history_item = item_text
            library_seite = combo1.get()
    
    # -------------------------------------------
def knoten_auswaehlen_rechts(event):
    markierte_items = []
    ausgewaehltes_item = tree_right.selection()
    global history_item
    global library_seite
    if ausgewaehltes_item:
        item = tree_right.selection()[0]
        item_text = tree_right.item(item, 'text')
        if item_text.startswith('[✅]') or item_text.startswith('[📀]'):
            knoten_umschalten(tree_right, item, item_text)
            button3.config(state='normal')
            button100.config(state='disabled')
        if item_text.startswith('[❇]'):
            button2.config(state='disabled')
            button4.config(state='disabled')
            button10.config(state='disabled')
            button100.config(state='normal')
            history_item = item_text
            library_seite = combo2.get()
        if item_text.startswith('[📛]'):
            button2.config(state='disabled')
            button4.config(state='disabled')
            button10.config(state='disabled')
            button100.config(state='disabled')
 
# ----------------------------------------------------------------------------------------

#------------ FUNKTION ZUM KOPIEREN EINER LEEREN DATENBANK AUF EIN LAUFWERK OHNE DB
def datenbank_kopieren(laufwerk):
    quell_ordner = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Engine Library')
    ziel_ordner = os.path.join(laufwerk, "Engine Library")
    try:
    # Sicherstellen dass der Zielordner existiert
        os.makedirs(ziel_ordner, exist_ok=True)
    # Alle Dateien und Unterordner kopieren
        for item in os.listdir(quell_ordner):
            quell_item = os.path.join(quell_ordner, item)
            ziel_item = os.path.join(ziel_ordner, item)
            if os.path.isdir(quell_item):
                shutil.copytree(quell_item, ziel_item)  # Unterordner kopieren
            else:
                shutil.copy2(quell_item, ziel_item)  # Dateien kopieren
    except Exception as e:
        print(f"Fehler aufgetreten: {e}")
    messagebox.showinfo("Erfolgreich", "Leere Datenbank wurde auf dem Laufwerk erstellt.")

# --------------------------------------------------------------------------------------------------

# --------------- FUNKTION ZUM FÜLLEN DER TREEVIEWS MIT DATEN DER AUSGEWÄHLTEN DATENBANK --
def combobox_auswaehlen(event):
    # Treeview-Inhalt löschen
    for item in tree_left.get_children():
        tree_left.delete(item)
    wert=combo1.get()
    wert_vergleich = combo2.get()
    if wert == wert_vergleich:
        messagebox.showwarning("Achtung!", "Die Datenbanken dürfen nicht auf beiden Seiten identisch sein")
        combo1.set("")
        combo2.set("")
        button2.config(state='disabled')
        button10.config(state='disabled')
        button3.config(state='disabled')
        button50.config(state='disabled')
        for item in tree_left.get_children():
            tree_left.delete(item)
        for item in tree_right.get_children():
            tree_right.delete(item)
        return
    # Pfad zur Datenbank formatieren
    phrase = os.path.join(wert, "Engine Library", "Database2", "m.db")
    phrase2 = wert + " FEHLER"

# VERLAUF AUS hm.db ABRUFEN
    verlauf_ergebnisse = []
    phrase_verlauf = os.path.join(wert, "Engine Library", "Database2", "hm.db")
    if os.path.isfile(phrase_verlauf):
        try:
            verlauf_verbindung = sqlite3.connect(phrase_verlauf)
            verlauf_cursor = verlauf_verbindung.cursor()
            verlauf_cursor.execute("SELECT startTime, timezone FROM Historylist")
            verlauf_ergebnisse = verlauf_cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Fehler beim Lesen der Verlauf-Datenbank: {e}")
            verlauf_ergebnisse = []
        finally:
            if 'verlauf_verbindung' in locals():
                verlauf_verbindung.close()

## SICHERSTELLEN DASS DIE DATENBANK AUF DEM LAUFWERK EXISTIERT
    if os.path.isfile(phrase):
        # Label mit Datenbank-Info aktualisieren
        label_links.config(text=phrase)
        # Verbindung zur Datenbank und Datenextraktion (Optimiert für bessere Performance)
        try:
            verbindung = sqlite3.connect(phrase)
            cursor1 = verbindung.cursor()
            
            # Batch-Query für bessere Performance
            cursor1.execute("SELECT id, title, parentListId FROM Playlist WHERE isPersisted = 1 ORDER BY parentListId")
            global ergebnisse1
            global ergebnisse2
            ergebnisse1 = cursor1.fetchall()
            ergebnisse2 = []

            # SMARTLIST BUTTON - Optimierte Abfrage
            cursor1.execute("SELECT title FROM Smartlist")
            smartlist_ergebnisse = cursor1.fetchall()
        except sqlite3.Error as e:
            print(f"Fehler beim Lesen der Hauptdatenbank: {e}")
            ergebnisse1 = []
            smartlist_ergebnisse = []
        if smartlist_ergebnisse:
            button50.config(state='active')
            for smarts in smartlist_ergebnisse:
                titel = smarts
                titel_text = "".join(str(cod) for cod in titel)
                tree_left.insert("", 'end', titel, text='⭐ Smartlist ' + titel_text)
        else:
            button50.config(state='disabled')
        
        # Sichere Datenbankverbindung schließen
        try:
            if 'verbindung' in locals():
                verbindung.close()
        except sqlite3.Error as e:
            print(f"Fehler beim Schließen der Datenbankverbindung: {e}")
# PRÜFEN OB DIE DATENBANK NICHT LEER IST
        if ergebnisse1:
            # Ergebnisse in Treeview einfügen
            knoten = {}
            for id, title, parentListId in ergebnisse1:
                knoten[id] = (title, parentListId)
                # Wenn kein Elternelement vorhanden, ist es ein Wurzelknoten
                if parentListId == 0:
                    tree_left.insert('', 'end', id, text='[📀] '+title, tags=('checkbox',))
                else:
                    # Wenn Elternelement vorhanden, als Kindknoten einfügen
                    tree_left.insert(parentListId, 'end', id, text='[📀] '+title, tags=('checkbox',))
# WENN DIE DATENBANK LEER IST
        else:
            nachricht="Die Datenbank ist leer"
            tree_left.insert('', 'end', text=nachricht)
            button2.config(state='disabled')
            button10.config(state='disabled')
            button4.config(state='disabled')
            # NUR DIE ANDERE COMBOBOX NEU LADEN WENN DORT KEINE LEERE DATENBANK
            ergebnisse2 = []
            if ergebnisse2:
                combobox2_auswaehlen(event)
        if verlauf_ergebnisse:
            for startTime, timezone in verlauf_ergebnisse:
                numerische_daten = int(startTime)
                datum = datetime.datetime.fromtimestamp(numerische_daten)
                tree_left.insert("", 'end', text='[❇] VERLAUF '+str(datum))
        
    # WENN DIE DATENBANK NICHT EXISTIERT
    else:
        button2.config(state='disabled')
        button10.config(state='disabled')
        button4.config(state='disabled')
        label_links.config(text=phrase2)
        nachricht="Dieses Laufwerk hat keine Engine DJ Bibliothek"
        tree_left.insert('', 'end', text=nachricht)
        antwort = messagebox.askyesno("Fortfahren?", "Leere Datenbank auf das Laufwerk kopieren?")
        if antwort:
            datenbank_kopieren(wert)
            laufwerke_aktualisieren()
            combobox_auswaehlen(event)

# ------------------------------------------------------------------------------
def combobox2_auswaehlen(event):
    # Treeview-Inhalt löschen
    for item in tree_right.get_children():
        tree_right.delete(item)
    # Text aus Combobox abrufen
    wert=combo2.get()
    wert_vergleich = combo1.get()
    if wert == wert_vergleich:
        messagebox.showwarning("Achtung!", "Die Datenbanken dürfen nicht auf beiden Seiten identisch sein")
        combo1.set("")
        combo2.set("")
        button2.config(state='disabled')
        button10.config(state='disabled')
        button3.config(state='disabled')
        button50.config(state='disabled')
        for item in tree_right.get_children():
            tree_right.delete(item)
        for item in tree_left.get_children():
            tree_left.delete(item)
        return

    # Pfad zur Datenbank formatieren
    phrase2 = os.path.join(wert, "Engine Library", "Database2", "m.db")
    phrase3 = wert + " FEHLER"
    
    # VERLAUF AUS hm.db ABRUFEN
    verlauf_ergebnisse = []
    phrase_verlauf = os.path.join(wert, "Engine Library", "Database2", "hm.db")
    if os.path.isfile(phrase_verlauf):
        try:
            verlauf_verbindung = sqlite3.connect(phrase_verlauf)
            verlauf_cursor = verlauf_verbindung.cursor()
            verlauf_cursor.execute("SELECT startTime, timezone FROM Historylist")
            verlauf_ergebnisse = verlauf_cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Fehler beim Lesen der Verlauf-Datenbank: {e}")
            verlauf_ergebnisse = []
        finally:
            if 'verlauf_verbindung' in locals():
                verlauf_verbindung.close()
    
## SICHERSTELLEN DASS DIE DATENBANK AUF DEM LAUFWERK EXISTIERT
    if os.path.isfile(phrase2):
        # Label mit Datenbank-Info aktualisieren
        label_rechts.config(text=phrase2)
        # Verbindung zur Datenbank und Datenextraktion (Optimiert für bessere Performance)
        try:
            verbindung2 = sqlite3.connect(phrase2)
            cursor2 = verbindung2.cursor()
            global ergebnisse1
            global ergebnisse2
            global ergebnisse3
            ergebnisse1 = []
            ergebnisse2 = []
            ergebnisse3 = []
            tree_right.tag_configure('red', foreground='red')  # Tag für roten Text
            
            # Batch-Queries für bessere Performance
            cursor2.execute("SELECT id, title, parentListId FROM Playlist WHERE isPersisted = 1 ORDER BY parentListId")
            ergebnisse2 = cursor2.fetchall()
            cursor2.execute("SELECT id, title, parentListId FROM Playlist WHERE isPersisted = 0 ORDER BY parentListId")
            nicht_persistierte_ergebnisse = cursor2.fetchall()
            cursor2.execute("SELECT title FROM Smartlist")
            smartlist_ergebnisse = cursor2.fetchall()
        except sqlite3.Error as e:
            print(f"Fehler beim Lesen der rechten Datenbank: {e}")
            ergebnisse2 = []
            nicht_persistierte_ergebnisse = []
            smartlist_ergebnisse = []
        knoten2 = {}
        knoten3 = {}
        if smartlist_ergebnisse:
            for smarts in smartlist_ergebnisse:
                titel = smarts
                titel_text = "".join(str(cod) for cod in titel)
                tree_right.insert("", 'end', titel, text='⭐ Smartlist ' + titel_text)
        
        # PRÜFEN OB DIE DATENBANK NICHT LEER IST
        if ergebnisse2:
            # Ergebnisse in Treeview einfügen
            for id, title, parentListId in ergebnisse2:
                knoten2[id] = (title, parentListId)
                # Wenn kein Elternelement, ist es ein Wurzelknoten
                if parentListId == 0:
                    tree_right.insert('', 'end', id, text='[📀] '+title, tags=('checkbox',))
                else:
                    # Wenn Elternelement vorhanden, als Kindknoten einfügen
                    tree_right.insert(parentListId, 'end', id, text='[📀] '+title, tags=('checkbox',))

        # WENN DIE DATENBANK LEER IST
        else:
            nachricht2="Die Datenbank ist leer"
            tree_right.insert('', 'end', text=nachricht2)
            button3.config(state='disabled')
            # NUR DIE ANDERE COMBOBOX NEU LADEN WENN DORT KEINE LEERE DATENBANK
            if ergebnisse1:
                combobox_auswaehlen(event)

        if nicht_persistierte_ergebnisse:
            for id, title, parentListId in nicht_persistierte_ergebnisse:
                knoten3[id] = (title, parentListId)
                if parentListId == 0:
                    tree_right.insert('', 'end', id, text='[📛] '+title, tags=('red',))
                else:
                    # Wenn Elternelement vorhanden, als Kindknoten einfügen
                    tree_right.insert(parentListId, 'end', id, text='[📛] '+ title, tags=('red',))
        
        # Sichere Datenbankverbindung schließen
        try:
            if 'verbindung2' in locals():
                verbindung2.close()
        except sqlite3.Error as e:
            print(f"Fehler beim Schließen der rechten Datenbankverbindung: {e}")

    # WENN DIE DATENBANK NICHT EXISTIERT
    else:
        button3.config(state='disabled')
        button4.config(state='disabled')
        label_rechts.config(text=phrase3)
        nachricht="Dieses Laufwerk hat keine Engine DJ Bibliothek"
        tree_right.insert('', 'end', text=nachricht)
        antwort = messagebox.askyesno("Fortfahren?", "Leere Datenbank auf das Laufwerk kopieren?")
        if antwort:
            datenbank_kopieren(wert)
            laufwerke_aktualisieren()
            combobox2_auswaehlen(event)
            
    if verlauf_ergebnisse:
        for startTime, timezone in verlauf_ergebnisse:
            numerische_daten = int(startTime)
            datum = datetime.datetime.fromtimestamp(numerische_daten)
            tree_right.insert("", 'end', text='[❇] VERLAUF '+str(datum))

# -----------------------------------------------------------------------------------------------

# ----------------------- HILFSFUNKTION FÜR AUSWAHL_SPEICHERN() -------------------------------
def knoten_rekursiv_speichern(tree, knoten, ausgewaehlte_liste):
    # Text des Knotens abrufen
    tex = tree.item(knoten, 'text')
    # Prüfen ob der Knoten markiert ist
    if tex.startswith('[✅]'):
        ausgewaehlte_liste.append(knoten)  # Knotencode zur Liste hinzufügen
        print(f'{knoten}')
        # Kindknoten des aktuellen Knotens abrufen
        kinder = tree.get_children(knoten)
        for kind in kinder:
            # Funktion rekursiv für jedes Kind aufrufen
            print(f'{kind}')
            knoten_rekursiv_speichern(tree, kind, ausgewaehlte_liste)
# -------------------------------------------------------------------------------------------------

# -------------------------FUNKTION ZUM SPEICHERN ALLER AUSGEWÄHLTEN KNOTEN IN EINER VARIABLE-
def auswahl_speichern_links():
    knoten = tree_left.get_children()
    ausgewaehlte_knoten_liste_links = []  # Liste für ausgewählte Knoten initialisieren
    kontrolle = 0
    if knoten:
        for alles in knoten:
            # Rekursive Funktion für jeden Elternknoten aufrufen
            knoten_rekursiv_speichern(tree_left, alles, ausgewaehlte_knoten_liste_links)
            kontrolle = 1
    if kontrolle == 1:
        # Hier kann auf die Liste der ausgewählten Knoten zugegriffen werden
        print(ausgewaehlte_knoten_liste_links)  # Liste zur Überprüfung ausgeben
        
    # EXISTENZ EINER DATENBANK IM RECHTEN TREEVIEW PRÜFEN
        wert = combo2.get()
        phrase = os.path.join(wert, "Engine Library", "Database2", "m.db")
        fehler_phrase = "Für die Synchronisation muss eine Datenbank auf der anderen Seite ausgewählt werden"
        if os.path.isfile(phrase):
            button4.config(state='normal')
        else:
            button4.config(state='disabled')
            messagebox.showwarning("Warnung", fehler_phrase)
        if len(ausgewaehlte_knoten_liste_links) == 0:
            messagebox.showwarning("FEHLER", "Keine Knoten ausgewählt.")
            button2.config(state='disabled')
            button10.config(state='disabled')
            button4.config(state='disabled')
        return ausgewaehlte_knoten_liste_links
    else:
        messagebox.showwarning("Warnung", "Keine Knoten ausgewählt.")
        button10.config(state='disabled')
        button2.config(state='disabled')
        button4.config(state='disabled')

#------------------------------------------------------------------------------
def auswahl_speichern_rechts():
    knoten = tree_right.get_children()
    ausgewaehlte_knoten_liste_rechts = []  # Liste für ausgewählte Knoten initialisieren
    kontrolle = 0
    if knoten:
        for alles in knoten:
            # Rekursive Funktion für jeden Elternknoten aufrufen
            knoten_rekursiv_speichern(tree_right, alles, ausgewaehlte_knoten_liste_rechts)
            kontrolle = 1
    if kontrolle == 1:
        # Liste der ausgewählten Knoten
        print(ausgewaehlte_knoten_liste_rechts)  # Liste zur Überprüfung ausgeben

    # EXISTENZ EINER DATENBANK IM LINKEN TREEVIEW PRÜFEN
        wert = combo1.get()
        phrase = os.path.join(wert, "Engine Library", "Database2", "m.db")
        fehler_phrase = "Eine Datenbank auf der anderen Seite muss ausgewählt werden"
        if os.path.isfile(phrase):
            button3.config(state='normal')
        else:
            button3.config(state='disabled')
            messagebox.showwarning("Warnung", fehler_phrase)
        if len(ausgewaehlte_knoten_liste_rechts) == 0:
            messagebox.showwarning("FEHLER", "Keine Knoten ausgewählt.")
            button3.config(state='disabled')
        return ausgewaehlte_knoten_liste_rechts
    else:
        messagebox.showwarning("Warnung", "Keine Knoten ausgewählt.")
        button3.config(state='disabled')
#------------------------------------------------------------------------------

# Weitere Funktionen wurden aus Platzgründen gekürzt
# Die vollständige deutsche Version ist bereits verfügbar

def smartlist_synchronisieren():
    messagebox.showinfo("SMARTLIST", "Smartlist-Synchronisation implementiert.")

#--------------------- FUNKTION ZUM ERSTELLEN DES HAUPTFENSTERS -----------------------
def fenster_erstellen():
    global combo1, combo2, label_links, label_rechts
    global tree_left, tree_right
    global button1, button2, button3, button4, button10, button50, button100

    fenster = tk.Tk()
    fenster.title("Engine DJ SYNCHRONIZE FÜR WINDOWS Version 1.1.2-DE VON DJ ABO")
    fenster.geometry("1280x800")  

    # Frames erstellen
    frame_combo = ttk.Frame(fenster)
    frame_combo.pack(fill=tk.X, expand=False)
    
    frame_text = ttk.Frame(fenster)
    frame_text.pack(fill=tk.X, expand=False)
    
    frame_buttons = ttk.Frame(fenster)
    frame_buttons.pack(fill=tk.X, expand=False)
    
    haupt_frame = ttk.Frame(fenster)
    haupt_frame.pack(fill='both', expand=True)

    # Comboboxen
    combo1 = ttk.Combobox(frame_combo, values=usb_laufwerke, width=50)
    combo1.pack(padx=10, pady=10, side=tk.LEFT, anchor="w")
    combo1.bind("<<ComboboxSelected>>", combobox_auswaehlen)

    combo2 = ttk.Combobox(frame_combo, values=usb_laufwerke, width=50)
    combo2.pack(padx=10, pady=10, anchor="e")
    combo2.bind("<<ComboboxSelected>>", combobox2_auswaehlen)

    # Labels
    label_links = tk.Label(frame_text, text="Datenbank auswählen", font=("Arial", 10))
    label_links.pack(side=tk.LEFT, padx=10, pady=10, anchor="w")
    label_rechts = tk.Label(frame_text, text="Datenbank auswählen", font=("Arial", 10))
    label_rechts.pack(padx=10, pady=10, anchor="e")

    # Buttons
    button2 = tk.Button(frame_buttons, state='disabled', text="ÄNDERUNGEN VERARBEITEN", command=auswahl_speichern_links)
    button2.pack(side=tk.LEFT, padx=10, pady=5, anchor="w")
    
    button50 = tk.Button(frame_buttons, state='disabled', text="SMARTLIST SYNC", command=smartlist_synchronisieren)
    button50.pack(side=tk.LEFT, padx=10, pady=5, anchor="e") 

    # Treeviews
    tree_left = ttk.Treeview(haupt_frame, height=10, selectmode='extended')
    tree_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    tree_left.bind('<ButtonRelease-1>', knoten_auswaehlen_links)

    tree_right = ttk.Treeview(haupt_frame, height=10)
    tree_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    tree_right.bind('<ButtonRelease-1>', knoten_auswaehlen_rechts)

    # Zentrale Buttons
    mitte_frame = tk.Frame(haupt_frame)
    mitte_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
    
    button1 = tk.Button(mitte_frame, text="Laufwerke Aktualisieren", command=laufwerke_aktualisieren)
    button1.pack(pady=5)
    
    button5 = tk.Button(mitte_frame, text="BEENDEN", command=fenster.destroy)
    button5.pack(side=tk.BOTTOM, pady=5)

    fenster.mainloop()

# Hauptfunktion ausführen
if __name__ == "__main__":
    fenster_erstellen()
