import json, datetime, requests,sys, pandas as pd, schedule, time
from pathlib import Path
import mimetypes
fachbereiche=["bcp","erzpsy","vetmed","wiwiss","physik","jfk","geowiss","polsoz","philgeist","sz","rewiss","geschkult","matheinf","mi"]
semester_alle={
    "wise1920":"Wintersemester 19/20","sose 2020":"Sommersemester 2020","sose2020":"Sommersemester 2020","sose20":"Sommersemester 2020","sose-2020":"Sommersemester 2020","sosoe2020":"Sommersemester 2020",

    "wise20-21":"Wintersemester 2020/2021","wise20-21":"Wintersemester 2020/2021","wise2021":"Wintersemester 2020/2021","wise 2020/2021":"Wintersemester 2020/2021","wise2021":"Wintersemester 2020/2021","ws-20-21":"Wintersemester 2020/2021","wise-2020-2021":"Wintersemester 2020/2021","ws2020-2021":"Wintersemester 2020/2021","wise 2020-2021":"Wintersemester 2020/2021","wise2020-2021":"Wintersemester 2020/2021","wise-20-21":"Wintersemester 2020/2021","ws2021":"Wintersemester 2020/2021","ws20-21":"Wintersemester 2020/2021","wise2020-2021":"Wintersemester 2020/2021","wise-2021":"Wintersemester 2020/2021","ws-2021":"Wintersemester 2020/2021","wise2020":"Wintersemester 2020/2021","wisee20/21":"Wintersemester 2020/2021",

    "21-sose":"Sommersemester 2021",

    "21-wise":"Wintersemester 2021/2022","wise21/22":"Wintersemester 2021/2022",

    "22-sose":"Sommersemester 2022","sose-22":"Sommersemester 2022","sose2022":"Sommersemester 2022",

    "22-wise":"Wintersemester 2022/2023","wise2022-2023":"Wintersemester 2022/2023",

    "23-sose":"Sommersemester 2023",

    "23-wise":"Wintersemester 2023/2024"
    }

semesterzuordnung={
            "Sommersemester 2020":{"Start":"2020-06-01","Ende":"2020-11-30"},
            "Wintersemester 2020/2021":{"Start":"2020-12-01","Ende":"2021-05-31"},
            "Sommersemester 2021":{"Start":"2021-06-01","Ende":"2021-11-30"},
            "Wintersemester 2021/2022":{"Start":"2021-12-01","Ende":"2022-05-31"},
            "Sommersemester 2022":{"Start":"2022-06-01","Ende":"2022-11-30"},
            "Wintersemester 2022/2023":{"Start":"2022-12-01","Ende":"2023-05-31"},
            "Sommersemester 2023":{"Start":"2023-06-01","Ende":"2023-11-30"},
            "Wintersemester 2023/2024":{"Start":"2023-12-01","Ende":"2024-05-31"},
            }

#depricated function
def daten_exportieren():
    def oauth():
        lplus_client_id= ''
        lplus_client_secret= ''
        benutzername=''
        passwort=''


        payload = {
            'grant_type': 'password',
            'client_id': lplus_client_id,
            'client_secret': lplus_client_secret,
            'username': benutzername,
            'password': passwort}
        r = requests.post('https://fub.lplus-teststudio.de/token', data=payload)
        token=json.loads(r.text)['access_token']
        return token

    def get_licences(token):
        demolizenzen=["e-examinations@home","zusatz","showcase","html","take-home","workshop","mp3","rth-","videotest","funktionstests","e-examinations@home om","lts5","zusatz-lts5testlizenz","drag-drop","neue lizenz","test api","test-impact","gjpa","demokatalog","testlizenz","julia","test_freigabe","heptner","test_bug","kopie","tali","testkatalog","_testlizenz_22","inaktiv","charité","cedis","demoprüfung","doz","probe"]

        headers={
            "Authorization": f"Bearer {token}"
            }

        r = requests.get('https://fub.lplus-teststudio.de/publicapi/v1/licences',headers=headers)
        lizensen=json.loads(r.text)

        datengrundlage_lizenzen_tagesaktuell=[]
        for lizenz in lizensen:
            zu_prüfende_lizenz=lizenz["name"].lower()
            if any(lizenz in zu_prüfende_lizenz for lizenz in demolizenzen):
                pass
            else:
                lizenzpaar={"Name":lizenz["name"],"ID":lizenz["id"]}
                datengrundlage_lizenzen_tagesaktuell.append(lizenzpaar)

        
        print(datengrundlage_lizenzen_tagesaktuell)
        print(len(datengrundlage_lizenzen_tagesaktuell))
        return datengrundlage_lizenzen_tagesaktuell

    def get_subject(token,datengrundlage_lizenzen_tagesaktuell):
        demofächer=["demoprüfung","doz","probe","cedis"]

        headers={
            "Authorization": f"Bearer {token}"
            }
        
        zähler=0
        checker=0
        for lizenz in datengrundlage_lizenzen_tagesaktuell:
            zähler+=1
            if checker<zähler:
                token=oauth()
                headers={"Authorization": f"Bearer {token}"}
                checker+=100
                print(f"Neuer Token, Checker bei {checker}")
                
            lizenz_id=lizenz["ID"]
            r = requests.get(f'https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/subjects',headers=headers)
            fächer=json.loads(r.text)

            #print(f"Fächer: {fächer}","\n")
            
            fächer_core=[]
            for listeneintrag in fächer:
                if any(demofach in listeneintrag["name"].lower() for demofach in demofächer):
                    pass
                else:
                    if " HK" in listeneintrag["name"] or "hauptklausur" in listeneintrag["name"].lower():
                        durchgang="HK"
                    elif " NK" in listeneintrag["name"] or "nachklausur" in listeneintrag["name"].lower() or "wiederholungsklausur" in listeneintrag["name"].lower():
                        durchgang = "NK"
                    else:
                        durchgang = None
                        
                    eintrag={"Fach-ID":listeneintrag["id"],"Fachname":listeneintrag["name"],"Prüfungsdurchgang":durchgang}
                    fächer_core.append(eintrag)
            lizenz["Fächer"]=fächer_core
            print(f"Fächer {zähler}")         

        return datengrundlage_lizenzen_tagesaktuell
        
    def get_exam_enrollment_and_tries(datengrundlage_lizenzen_tagesaktuell):
        token=oauth()
        headers={
        "Authorization": f"Bearer {token}"
        }

        zähler=0
        checker=0
        for lizenz in datengrundlage_lizenzen_tagesaktuell:
            zähler+=1
            if checker<zähler:
                token=oauth()
                headers={"Authorization": f"Bearer {token}"}
                checker+=100
                print(f"Neuer Token, Checker bei {checker}")
            
            lizenz_id=lizenz["ID"]
            
            datum_heute=datetime.datetime.today().date()
            for fach in lizenz["Fächer"]:
                fach_id=fach["Fach-ID"]
                fach["Semester"]=[]

                for semester, datum in semesterzuordnung.items():
                    semester_aktuell=semester

                    datum_start=datum["Start"]
                    datum_ende=datum["Ende"]

                    if datetime.datetime.strptime(datum_start, "%Y-%m-%d").date() <= datum_heute:
                    
                        url=f'https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/subjects/{fach_id}/statistics?dateFilterData.dateFrom={datum_start}&dateFilterData.dateTo={datum_ende}'

                        r = requests.get(url,headers=headers)
                        
                        statistik=json.loads(r.text)

                        prüfungsdurchführungen=statistik["candidatesWithExaminationTries"]

                        fach["Semester"].append({semester_aktuell:{"Absolvierte Prüfungen": prüfungsdurchführungen}})


                print(fach)                   
            
            #print(f"Absolvierte Prüfungen {zähler}")
        
        return datengrundlage_lizenzen_tagesaktuell
  

    def hinzufügen_von_metadaten(datengrundlage_lizenzen_tagesaktuell):
        for lizenz in datengrundlage_lizenzen_tagesaktuell:

            name_lizenz=lizenz["Name"].lower()
            for fb in fachbereiche:
                if fb in name_lizenz:
                    lizenz["Fachbereich"]=fb
                    break
            else:
                lizenz["Fachbereich"]=None

            """   
            for semester_idio,semester_generisch in semester_alle.items():
                if semester_idio in name_lizenz:
                    lizenz["Semester"]=semester_generisch
                    break
            else:
                lizenz["Semester"]=None
            """

            if "EEC" in lizenz["Name"]:
                lizenz["Format"] = "Präsenz"
            elif "HOME" in lizenz["Name"]:
                lizenz["Format"] = "Distanz"
            else:
                lizenz["Format"] = None
        
        return datengrundlage_lizenzen_tagesaktuell

    #Eigentliche Methode
    token=oauth() #Token generieren
    
    datengrundlage_lizenzen_tagesaktuell=get_licences(token) #Alle Lizenzen auf Plattform ziehen
    datengrundlage_lizenzen_tagesaktuell=get_subject(token,datengrundlage_lizenzen_tagesaktuell) #Zugehörige Fächer der Lizenzen ziehen

    datengrundlage_lizenzen_tagesaktuell=get_exam_enrollment_and_tries(datengrundlage_lizenzen_tagesaktuell) #Gemeldete und geprüfte Studierende ziehen

    datengrundlage_lizenzen_tagesaktuell=hinzufügen_von_metadaten(datengrundlage_lizenzen_tagesaktuell) #Fachbereich und Semester zu Lizenz hinzufügen
    print(datengrundlage_lizenzen_tagesaktuell)
    
    return datengrundlage_lizenzen_tagesaktuell

# 1. Schritt: Tagesaktuelle Daten der Plattform ziehen
def daten_exportieren_current_semester():
    
    def oauth():
        lplus_client_id= ''
        lplus_client_secret= ''
        benutzername=''
        passwort=''


        payload = {
            'grant_type': 'password',
            'client_id': lplus_client_id,
            'client_secret': lplus_client_secret,
            'username': benutzername,
            'password': passwort}
        r = requests.post('https://fub.lplus-teststudio.de/token', data=payload)
        token=json.loads(r.text)['access_token']
        return token

    def get_licences(token):
        demolizenzen=["e-examinations@home","zusatz","showcase","html","take-home","workshop","mp3","rth-","videotest","funktionstests","e-examinations@home om","lts5","zusatz-lts5testlizenz","drag-drop","neue lizenz","test api","test-impact","gjpa","demokatalog","testlizenz","julia","test_freigabe","heptner","test_bug","kopie","tali","testkatalog","_testlizenz_22","inaktiv","charité","cedis","demoprüfung","doz","probe"]

        headers={
            "Authorization": f"Bearer {token}"
            }

        connection_counter=0
        while connection_counter < 5:
            try:
                r = requests.get('https://fub.lplus-teststudio.de/publicapi/v1/licences',headers=headers)
                lizensen=json.loads(r.text)
                break
            except:
                connection_counter+=1
                time.sleep(connection_counter)
        else:
            sys.exit()

        datengrundlage_lizenzen_tagesaktuell=[]
        for lizenz in lizensen:
            zu_prüfende_lizenz=lizenz["name"].lower()
            if any(lizenz in zu_prüfende_lizenz for lizenz in demolizenzen):
                pass
            else:
                lizenzpaar={"Name":lizenz["name"],"ID":lizenz["id"]}
                datengrundlage_lizenzen_tagesaktuell.append(lizenzpaar)

        print(len(datengrundlage_lizenzen_tagesaktuell))
        return datengrundlage_lizenzen_tagesaktuell

    def check_licence_change(liste_aktuelle_lizenzen, datengrundlage_lizenzen):
        print("Beginne Prüfung Änderung von Lizenznamen")
        
        for eintrag in datengrundlage_lizenzen:
            for inhalt in liste_aktuelle_lizenzen:
                if eintrag["ID"] == inhalt["ID"]:
                    if eintrag["Name"] != inhalt["Name"]:
                        eintrag["Name"] = inhalt["Name"]
        
        return datengrundlage_lizenzen

    def check_subject_change(datengrundlage_lizenzen):
        print("Beginne Prüfung auf Änderung von Fachnamen und neu angelegte Fächer")
        demofächer=["demoprüfung","doz","probe","cedis"]
        zähler=0
        checker=0
        counter=0
        for eintrag in datengrundlage_lizenzen:
            counter+=1
            print(f"Abfrage Nr. {counter}")

            zähler+=1
            if checker<zähler:
                token=oauth()
                headers={"Authorization": f"Bearer {token}"}
                checker+=100
                print(f"Neuer Token, Checker bei {checker}")

            lizenz_id=eintrag["ID"]

            connection_counter=0
            while connection_counter < 5:
                try:
                    r = requests.get(f'https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/subjects/',headers=headers)
                    fächer=json.loads(r.text)
                    break
                
                except:
                    connection_counter+=1
                    time.sleep(connection_counter)
                    print(fach)
            else:
                sys.exit()
            
            drop_liste_fächer=[]
            for fach in eintrag["Fächer"]:
                fach_id=fach["Fach-ID"]
                fach_name=fach["Fachname"]
                
                
                for response in fächer: 
                    if response["id"] == fach_id:
                        drop_liste_fächer.append(response)

                        if response["name"] != fach_name:
                            fach["Fachname"] = response["name"]
                
            #print(drop_liste_fächer,"\n")

            for eintrag2 in drop_liste_fächer:
                if eintrag2 in fächer:
                    fächer.remove(eintrag2)
            
            for response in fächer:
                if any(demofach in response["name"].lower() for demofach in demofächer):
                    pass
                else:
                    eintrag["Fächer"].append({"Fach-ID":response["id"],"Fachname":response["name"],"Prüfungsdurchgang":None})
                    print(eintrag)

                
                            



        return datengrundlage_lizenzen

    def compare_saved_and_new_lincences(alte_liste,aktuelle_liste):
        print("Vergleiche Datenbank und neue Daten")
        liste_hinzuzufügender_lizenzen=[]

        for lizenz in aktuelle_liste:
            for alte_lizenz in alte_liste:
                if lizenz["ID"] in alte_lizenz.values():
                    break
            else:
                liste_hinzuzufügender_lizenzen.append(lizenz)
        
        print(liste_hinzuzufügender_lizenzen)
        return liste_hinzuzufügender_lizenzen

    def get_new_subjects(liste_neuer_lizenzen):
        print("Ziehe neue Fächerdaten")

        demofächer=["demoprüfung","doz","probe","cedis"]
        
        zähler=0
        checker=0
        for lizenz in liste_neuer_lizenzen:
            zähler+=1
            if checker<zähler:
                token=oauth()
                headers={"Authorization": f"Bearer {token}"}
                checker+=100
                print(f"Neuer Token, Checker bei {checker}")
                
            lizenz_id=lizenz["ID"]

            connection_counter=0
            while connection_counter < 5:
                try:
                    r = requests.get(f'https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/subjects',headers=headers)
                    fächer=json.loads(r.text)
                    break
                except:
                    connection_counter+=1
                    time.sleep(connection_counter)
            else:
                sys.exit()


            
            fächer_core=[]
            for listeneintrag in fächer:
                if any(demofach in listeneintrag["name"].lower() for demofach in demofächer):
                    pass
                
                else:    
                    eintrag={"Fach-ID":listeneintrag["id"],"Fachname":listeneintrag["name"],"Prüfungsdurchgang":None}
                    fächer_core.append(eintrag)
            lizenz["Fächer"]=fächer_core
     

        return liste_neuer_lizenzen
  
    def merge_lists(liste_neuer_lizenzen, datengrundlage_lizenzen):
        print("Kombiniere Datenbank mit neuen Daten")
        print(liste_neuer_lizenzen)
        if len(liste_neuer_lizenzen)>0:
            datengrundlage_lizenzen=datengrundlage_lizenzen+liste_neuer_lizenzen
        else:
            pass

        return datengrundlage_lizenzen

    def hinzufügen_von_metadaten(datengrundlage_lizenzen):
        print("Füge Metadaten hinzu")
        for lizenz in datengrundlage_lizenzen:

            name_lizenz=lizenz["Name"].lower()
            for fb in fachbereiche:
                if fb in name_lizenz:
                    lizenz["Fachbereich"] = fb
                    break
            else:
                lizenz["Fachbereich"]="MISC"

            if "EEC" in lizenz["Name"]:
                lizenz["Format"] = "Präsenz"
            elif "HOME" in lizenz["Name"]:
                lizenz["Format"] = "Distanz"
            else:
                lizenz["Format"] = None

            for fach in lizenz["Fächer"]:
                if " HK" in fach["Fachname"] or "hauptklausur" in fach["Fachname"].lower():
                        fach["Prüfungsdurchgang"] = "HK"

                elif " NK" in fach["Fachname"] or "nachklausur" in fach["Fachname"].lower() or "wiederholungsklausur" in fach["Fachname"].lower():
                        fach["Prüfungsdurchgang"] =  "NK"
                else:
                    fach["Prüfungsdurchgang"] = None


        return datengrundlage_lizenzen
   
    def get_exam_enrollment_and_tries_of_current_semester(datengrundlage_lizenzen_tagesaktuell):
        print("Ziehe aktuelle Prüfungszahlen")

        token=oauth()
        headers={
        "Authorization": f"Bearer {token}"
        }

        zähler=0
        checker=0
        counter=0
        for lizenz in datengrundlage_lizenzen_tagesaktuell:
            zähler+=1
            if checker<zähler:
                token=oauth()
                headers={"Authorization": f"Bearer {token}"}
                checker+=100
                print(f"Neuer Token, Checker bei {checker}")
            
            #print(lizenz)
            lizenz_id=lizenz["ID"]
            
            datum_heute=datetime.datetime.today().date()
            
            
            for fach in lizenz["Fächer"]:
                counter+=1
                print(f"Abfrage Nr. {counter}")
                
                fach_id=fach["Fach-ID"]

                if not fach.get("Semester"):
                    fach["Semester"]=[]
               
                for semester, datum in semesterzuordnung.items():

                    semester_aktuell=semester

                    datum_start=datum["Start"]
                    datum_ende=datum["Ende"]

                    if datum_heute > datetime.datetime.strptime(datum_start, "%Y-%m-%d").date() and datum_heute > datetime.datetime.strptime(datum_ende, "%Y-%m-%d").date():
                        
                        for eintrag in fach["Semester"]:
                            if eintrag.get(semester):
                                break
                        else:
                            print("Noch keine Daten für das vergangene Semester vorliegend - ersetze mit 0.")
                            fach["Semester"].append({semester_aktuell:{"Absolvierte Prüfungen": 0}})


                    elif datum_heute >= datetime.datetime.strptime(datum_start, "%Y-%m-%d").date() and datum_heute <= datetime.datetime.strptime(datum_ende, "%Y-%m-%d").date():
    
                        url=f'https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/subjects/{fach_id}/statistics?dateFilterData.dateFrom={datum_start}&dateFilterData.dateTo={datum_ende}'
                        
                        connection_counter=0
                        while connection_counter < 5:
                            try:
                                r = requests.get(url,headers=headers)
                                statistik=json.loads(r.text)
                                prüfungsdurchführungen=statistik["candidatesWithExaminationTries"]
                        
                                for eintrag in fach["Semester"]:
                                    semester_json=list(eintrag.keys())[0]
                                    if semester_json == semester:
                                        break
                                else:
                                    fach["Semester"].append({semester:""})
                                
                                for sem in fach["Semester"]:
                                    for key, item in sem.items():
                                        if key == semester:
                                            sem[key]={"Absolvierte Prüfungen": prüfungsdurchführungen}
                                        break
                                break
                            
                            except ValueError:
                                print("Konnte JSON nicht dekodieren")
                                break

                            except:
                                connection_counter+=1
                                time.sleep(connection_counter)
                                print(fach)
                        else:
                            sys.exit()
                        



                    elif datum_heute < datetime.datetime.strptime(datum_start, "%Y-%m-%d").date():
                        pass

        
        return datengrundlage_lizenzen_tagesaktuell

    def filter_leere_lizenzen(datengrundlage_lizenzen_tagesaktuell):
        for lizenz in datengrundlage_lizenzen_tagesaktuell:
            liste_einträge_drop=[]
            for eintrag in lizenz["Fächer"]:
                print(eintrag)
                prüfungsteilnahmen=0
                for inhalt in eintrag["Semester"]:
                    for k,v in inhalt.items():
                        for keys, absolvierte_prüfungen in v.items(): 
                            prüfungsteilnahmen=prüfungsteilnahmen+int(absolvierte_prüfungen)
                if prüfungsteilnahmen == 0:
                    liste_einträge_drop.append(eintrag)
            for i in liste_einträge_drop:
                lizenz["Fächer"].remove(i)

        return datengrundlage_lizenzen_tagesaktuell

    #Reinladen der Datenbank
    f = open('prüfungsdaten_roh_vollständig.json',encoding='utf-8')
    datengrundlage_lizenzen = json.load(f)

    #Erstmaliges Generieren LPLUS Token
    token=oauth()

    #Ziehen der aktuellen Lizenzen
    liste_aktuelle_lizenzen = get_licences(token)

    #Prüfung auf Namensänderung der gespeicherten Lizenzen
    datengrundlage_lizenzen = check_licence_change(liste_aktuelle_lizenzen, datengrundlage_lizenzen)
    
    #Prüfung auf Namensänderung in gespeicherten Fächern
    datengrundlage_lizenzen = check_subject_change(datengrundlage_lizenzen)

    #Filtern der neu dazugekommenen Lizenzen
    liste_neuer_lizenzen = compare_saved_and_new_lincences(datengrundlage_lizenzen, liste_aktuelle_lizenzen)

    #Ziehen der Fächer für neue Lizenzen
    liste_neuer_lizenzen = get_new_subjects(liste_neuer_lizenzen)
    
    #Zusammenführung bestehender Daten und neu generierter Daten
    datengrundlage_lizenzen = merge_lists(liste_neuer_lizenzen, datengrundlage_lizenzen)

    #Hinzufügen von Metadaten (Format, Prüfungsdurchgang, Fachbereich)
    datengrundlage_lizenzen = hinzufügen_von_metadaten(datengrundlage_lizenzen)
    
    #Abfrage aktueller Prüfungsteilnahmen
    datengrundlage_lizenzen_tagesaktuell = get_exam_enrollment_and_tries_of_current_semester(datengrundlage_lizenzen)
    
    #Droppen aller leeren Lizenzen
    #datengrundlage_lizenzen_tagesaktuell = filter_leere_lizenzen(datengrundlage_lizenzen_tagesaktuell)
    #Rückgabe des vollständigen, aktualisierten Datenstamms
    return datengrundlage_lizenzen_tagesaktuell
    
# 2. Schritt aktuelle Daten mit Datenbank abgleichen
def generierung_datenbank(datengrundlage_lizenzen_tagesaktuell):
    
    #Generieren der Detailansicht aller Fächer
    print("Generiere Datenübersicht")

    columns=['Fach',"Fach-ID","Lizenz","Lizenz-ID","Fachbereich","Prüfungsdurchgang","Format"]
    for key,value in semesterzuordnung.items():
        columns.append(key)

    detailtable_fächer = pd.DataFrame(columns=columns)
    
    sammlung_rows=[]
    for lizenz in datengrundlage_lizenzen_tagesaktuell:
        for fach in lizenz["Fächer"]:
            new_row = {'Fach':fach["Fachname"],"Fach-ID":fach["Fach-ID"],"Lizenz":lizenz["Name"],"Lizenz-ID":lizenz["ID"],"Fachbereich":lizenz["Fachbereich"],"Prüfungsdurchgang":fach["Prüfungsdurchgang"],"Format":lizenz["Format"]}
            for key,value in semesterzuordnung.items():
                for eintrag in fach["Semester"]:
                    if eintrag.get(key):
                        new_row[key]=eintrag[key]["Absolvierte Prüfungen"]
            sammlung_rows.append(new_row)
    
    detailtable_fächer = pd.DataFrame(sammlung_rows)

    #detailtable_fächer = pd.concat([detailtable_fächer,new_rows], ignore_index=True)
    print(detailtable_fächer)

    detailtable_fächer.to_csv("Fächerliste.csv", encoding="utf-8-sig", sep=";")

    #Generieren der Übersicht der Prüfungszahlen nach Semester und Fachbereich

    columns=["Fachbereiche"]
    for key,value in semesterzuordnung.items():
        columns.append(key)
    
    #Fachbereiche eintragen
    fachbereiche.sort()
    fachbereiche.append("MISC")


    gesamtübersicht_prüfungszahlen = pd.DataFrame(columns=columns)
    gesamtübersicht_prüfungszahlen["Fachbereiche"]=fachbereiche
    gesamtübersicht_prüfungszahlen=gesamtübersicht_prüfungszahlen.set_index('Fachbereiche')

    #Analyse der Detailstatistik für Semester-Prüfungszahlen 
    #Analyse der jeweiligen Semester

    for semester in semesterzuordnung.keys():
        analyse_dict={}
        for fb in fachbereiche:
            dict_paar={fb:0}
            analyse_dict.update(dict_paar)
        analyse_dict.update({"MISC":0})
        analyse_dict_aktuell=analyse_dict

        for key, value in analyse_dict_aktuell.items():
            try:
                dftest=detailtable_fächer.loc[detailtable_fächer['Fachbereich'] == key, semester]

                analyse_dict_aktuell[key]=dftest.sum()
                value=dftest.sum()
            except:
                pass
        for key,value in analyse_dict_aktuell.items():
            gesamtübersicht_prüfungszahlen.loc[[key],[semester]] = value


    gesamtübersicht_prüfungszahlen = gesamtübersicht_prüfungszahlen.fillna(0)
    gesamtübersicht_prüfungszahlen.loc["Total"] = gesamtübersicht_prüfungszahlen.sum()
    gesamtübersicht_prüfungszahlen['Total'] = gesamtübersicht_prüfungszahlen.sum(axis=1)
    print(gesamtübersicht_prüfungszahlen)

    gesamtübersicht_prüfungszahlen.to_excel("Gesamtübersicht Prüfungszahlen.xlsx", encoding="utf-8-sig")
                

# 3. Schritt: Upload ins Wiki
def upload_wiki():
    print("Laden Datenübersicht in Wiki hoch")

    zielseite=""
    token=""
    url = f'https://wikis.fu-berlin.de/rest/api/content/{zielseite}/child/attachment/'
    headers = {"Authorization": f"Bearer {token}"}
    
    
    r = requests.get(url, headers=headers)
    attachment_id=json.loads(r.text)
    attachment_id=attachment_id["results"][0]["id"]
    
    url = f'https://wikis.fu-berlin.de/rest/api/content/{zielseite}/child/attachment/{attachment_id}/data'
    headers = {'X-Atlassian-Token': 'no-check',
               "Authorization": f"Bearer {token}"}
    file = 'Gesamtübersicht Prüfungszahlen.xlsx'

    # determine content-type
    content_type, encoding = mimetypes.guess_type(file)
    if content_type is None:
        content_type = 'multipart/form-data'

    # provide content-type explicitly
    files = {'file': (file, open(file, 'rb'), content_type)}

    r = requests.post(url, headers=headers, files=files)

    if r.status_code==200:
        print("Datei erfolgreich hochgeladen")
    else:
        print("Achtung, Fehler beim Upload")

####Ablauf Skript mit Abfrage aktuelles Semester
def include_all():
    
    datengrundlage_lizenzen_tagesaktuell=daten_exportieren_current_semester()
    
    with open('prüfungsdaten_roh_vollständig.json', 'w') as f: #
        json.dump(datengrundlage_lizenzen_tagesaktuell, f)  #data is dumped into file 
    
    cwd = Path.cwd()
    
    with open(f'{cwd}/repository/{datetime.datetime.today().date().strftime("%Y-%m-%d")}_prüfungsdaten_roh_vollständig.json', 'w') as f: #
        json.dump(datengrundlage_lizenzen_tagesaktuell, f)  #data is dumped into file 
        
    generierung_datenbank(datengrundlage_lizenzen_tagesaktuell)
    
    upload_wiki()


schedule.every().day.at("00:00").do(include_all)

while True:

    schedule.run_pending()
    
    time.sleep(1)

