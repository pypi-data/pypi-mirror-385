import datetime as dt

endpoints = {
    "/prognose/Solar": {
        "first_data": dt.datetime(2011, 3, 31, 22),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/prognose/Wind": {
        "first_data": dt.datetime(2011, 3, 31, 22),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/Spotmarktpreise": {
        "first_data": dt.datetime(2020, 12, 31, 23),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;Spotmarktpreis in ct/kWh",
        "transformed_header": "von;bis;Spotmarktpreis in ct/kWh",
    },
    "/hochrechnung/Solar": {
        "first_data": dt.datetime(2011, 3, 31, 22),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/hochrechnung/Wind": {
        "first_data": dt.datetime(2011, 3, 31, 22),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/onlineHochrechnung/Solar": {
        "first_data": dt.datetime(2011, 12, 31, 23),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/onlineHochrechnung/Windonshore": {
        "first_data": dt.datetime(2011, 12, 31, 23),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/onlineHochrechnung/Windoffshore": {
        "first_data": dt.datetime(2011, 12, 31, 23),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/NegativePreise": {
        "first_data": dt.datetime(2020, 12, 31, 23),
        "header": "Datum;Stunde1;Stunde3;Stunde4;Stunde6",
        "transformed_header": "Datum;Stunde1;Stunde3;Stunde4;Stunde6",
    },
    "/NegativePreise/1": {
        "first_data": dt.datetime(2020, 12, 31, 23),
        "header": "Datum;Negativ",
        "transformed_header": "Datum;Negativ",
    },
    "/NegativePreise/3": {
        "first_data": dt.datetime(2020, 12, 31, 23),
        "header": "Datum;Negativ",
        "transformed_header": "Datum;Negativ",
    },
    "/NegativePreise/4": {
        "first_data": dt.datetime(2020, 12, 31, 23),
        "header": "Datum;Negativ",
        "transformed_header": "Datum;Negativ",
    },
    "/NegativePreise/6": {
        "first_data": dt.datetime(2020, 12, 31, 23),
        "header": "Datum;Negativ",
        "transformed_header": "Datum;Negativ",
    },
    "/NegativePreise/15": {
        "first_data": dt.datetime(2020, 12, 31, 23),
        "header": "Datum;Negativ",
        "transformed_header": "Datum;Negativ",
    },
    "/vermarktung/InanspruchnahmeAusgleichsenergie": {
        "first_data": dt.datetime(2011, 3, 31, 22),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (kWh);Amprion (kWh);TenneT TSO (kWh);TransnetBW (kWh)",
        "transformed_header": "von;bis;50Hertz (kWh);Amprion (kWh);TenneT TSO (kWh);TransnetBW (kWh)",
    },
    "/vermarktung/UntertaegigeStrommengen": {
        "first_data": dt.datetime(2011, 3, 31, 22),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/vermarktung/DifferenzEinspeiseprognose": {
        "first_data": dt.datetime(2011, 3, 31, 22),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/vermarktung/VermarktungExaa": {
        "first_data": dt.datetime(2011, 12, 31, 23),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/vermarktung/VermarktungEpex": {
        "first_data": dt.datetime(2011, 12, 31, 23),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/vermarktung/VermarktungsSonstige": {
        "first_data": dt.datetime(2011, 12, 31, 22),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/vermarktung/VermarktungsSolar": {
        "first_data": dt.datetime(2013, 12, 31, 23),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/vermarktung/VermarktungsWind": {
        "first_data": dt.datetime(2013, 12, 31, 23),
        "header": "Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
        "transformed_header": "von;bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)",
    },
    "/IdAep": {
        "first_data": dt.datetime(2020, 6, 30, 22),
        "header": "Datum von;(Uhrzeit) von;Zeitzone von;(Uhrzeit) bis;Zeitzone bis;ID AEP in €/MWh",
        "transformed_header": "von;bis;ID AEP in €/MWh",
    },
    "/marktpraemie": {
        "first_data": dt.datetime(2012, 1, 1),
        "header": "Monat;MW-EPEX in ct/kWh;MW Wind Onshore in ct/kWh;PM Wind Onshore fernsteuerbar in ct/kWh;MW Wind Offshore in ct/kWh;PM Wind Offshore fernsteuerbar in ct/kWh;MW Solar in ct/kWh;PM Solar fernsteuerbar in ct/kWh;MW steuerbar in ct/kWh;PM steuerbar in ct/kWh;Negative Stunden (6H);Negative Stunden (4H);Negative Stunden (3H);Negative Stunden (1H);Negative Stunden (15MIN)",
        "transformed_header": "Monat;MW-EPEX in ct/kWh;MW Wind Onshore in ct/kWh;PM Wind Onshore fernsteuerbar in ct/kWh;MW Wind Offshore in ct/kWh;PM Wind Offshore fernsteuerbar in ct/kWh;MW Solar in ct/kWh;PM Solar fernsteuerbar in ct/kWh;MW steuerbar in ct/kWh;PM steuerbar in ct/kWh;Negative Stunden (6H);Negative Stunden (4H);Negative Stunden (3H);Negative Stunden (1H);Negative Stunden (15MIN)",
    },
    "/Jahresmarktpraemie": {
        "first_data": dt.datetime(2020, 1, 1),
        "header": "Alle Werte in ct/kWh;",
        "transformed_header": "Alle Werte in ct/kWh;JW;JW Wind an Land;JW Wind auf See;JW Solar",
    },
    "/redispatch": {
        "first_data": dt.datetime(2021, 1, 1),
        "header": "BEGINN_DATUM;BEGINN_UHRZEIT;ZEITZONE_VON;ENDE_DATUM;ENDE_UHRZEIT;ZEITZONE_BIS;GRUND_DER_MASSNAHME;RICHTUNG;MITTLERE_LEISTUNG_MW;MAXIMALE_LEISTUNG_MW;GESAMTE_ARBEIT_MWH;ANWEISENDER_UENB;ANFORDERNDER_UENB;BETROFFENE_ANLAGE;PRIMAERENERGIEART",
        "transformed_header": "BEGINN;ENDE;GRUND_DER_MASSNAHME;RICHTUNG;MITTLERE_LEISTUNG_MW;MAXIMALE_LEISTUNG_MW;GESAMTE_ARBEIT_MWH;ANWEISENDER_UENB;ANFORDERNDER_UENB;BETROFFENE_ANLAGE;PRIMAERENERGIEART",
    },
    "/Kapazitaetsreserve": {
        "first_data": dt.datetime(2021, 1, 1),
        "header": "BEGINN_DATUM;BEGINN_UHRZEIT;ZEITZONE_VON;ENDE_DATUM;ENDE_UHRZEIT;ZEITZONE_BIS;GRUND_DER_MASSNAHME;RICHTUNG;MITTLERE_LEISTUNG_MW;MAXIMALE_LEISTUNG_MW;GESAMTE_ARBEIT_MWH;ANWEISENDER_UENB;ANFORDERNDER_UENB;BETROFFENE_ANLAGE;PRIMAERENERGIEART",
        "transformed_header": "BEGINN;ENDE;GRUND_DER_MASSNAHME;RICHTUNG;MITTLERE_LEISTUNG_MW;MAXIMALE_LEISTUNG_MW;GESAMTE_ARBEIT_MWH;ANWEISENDER_UENB;ANFORDERNDER_UENB;BETROFFENE_ANLAGE;PRIMAERENERGIEART",
    },
    "/VorhaltungkRD": {
        "first_data": dt.datetime(2025, 1, 1),
        "header": "BEGINN_DATUM;BEGINN_UHRZEIT;ZEITZONE_VON;ENDE_DATUM;ENDE_UHRZEIT;ZEITZONE_BIS;GRUND_DER_MASSNAHME;RICHTUNG;MITTLERE_LEISTUNG_MW;MAXIMALE_LEISTUNG_MW;GESAMTE_ARBEIT_MWH;ANWEISENDER_UENB;ANFORDERNDER_UENB;BETROFFENE_ANLAGE;PRIMAERENERGIEART",
        "transformed_header": "BEGINN;ENDE;GRUND_DER_MASSNAHME;RICHTUNG;MITTLERE_LEISTUNG_MW;MAXIMALE_LEISTUNG_MW;GESAMTE_ARBEIT_MWH;ANWEISENDER_UENB;ANFORDERNDER_UENB;BETROFFENE_ANLAGE;PRIMAERENERGIEART",
    },
    "/TrafficLight": {
        "first_data": dt.datetime(2021, 9, 21, 22),
        "header": "From;To;Value",
        "transformed_header": "From;To;Value",
    },
    "/NrvSaldo/NRVSaldo/Betrieblich": {
        "first_data": dt.datetime(2014, 3, 25, 23),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;Deutschland;AEP Knappheitskomponente;Mrl-Mol-Abweichung;Srl-Mol-Abweichung",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;Deutschland;AEP Knappheitskomponente;Mrl-Mol-Abweichung;Srl-Mol-Abweichung",
    },
    "/NrvSaldo/NRVSaldo/Qualitaetsgesichert": {
        "first_data": dt.datetime(2013, 12, 31, 23),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;Deutschland",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;Deutschland",
    },
    "/NrvSaldo/RZSaldo/Betrieblich": {
        "first_data": dt.datetime(2011, 6, 26, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz;Amprion;TenneT TSO;TransnetBW",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz;Amprion;TenneT TSO;TransnetBW",
    },
    "/NrvSaldo/RZSaldo/Qualitaetsgesichert": {
        "first_data": dt.datetime(2014, 4, 30, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz;Amprion;TenneT TSO;TransnetBW",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz;Amprion;TenneT TSO;TransnetBW",
    },
    "/NrvSaldo/AktivierteSRL/Betrieblich": {
        "first_data": dt.datetime(2011, 6, 26, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ);MOL-Abweichung",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ);MOL-Abweichung",
    },
    "/NrvSaldo/AktivierteSRL/Qualitaetsgesichert": {
        "first_data": dt.datetime(2014, 4, 30, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/AktivierteMRL/Betrieblich": {
        "first_data": dt.datetime(2011, 6, 26, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ);MOL-Abweichung",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ);MOL-Abweichung",
    },
    "/NrvSaldo/AktivierteMRL/Qualitaetsgesichert": {
        "first_data": dt.datetime(2014, 4, 30, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/SRLOptimierung/Betrieblich": {
        "first_data": dt.datetime(2022, 6, 23, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/SRLOptimierung/Qualitaetsgesichert": {
        "first_data": dt.datetime(2022, 6, 21, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/MRLOptimierung/Betrieblich": {
        "first_data": dt.datetime(2011, 6, 26, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/MRLOptimierung/Qualitaetsgesichert": {
        "first_data": dt.datetime(2014, 5, 31, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/PRL/Betrieblich": {
        "first_data": dt.datetime(2022, 6, 21, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/PRL/Qualitaetsgesichert": {
        "first_data": dt.datetime(2022, 6, 21, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/Difference/Betrieblich": {
        "first_data": dt.datetime(2022, 6, 21, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/Difference/Qualitaetsgesichert": {
        "first_data": dt.datetime(2022, 6, 21, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/Zusatzmassnahmen/Betrieblich": {
        "first_data": dt.datetime(2019, 12, 31, 23),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/Zusatzmassnahmen/Qualitaetsgesichert": {
        "first_data": dt.datetime(2013, 12, 31, 23),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/Nothilfe/Betrieblich": {
        "first_data": dt.datetime(2025, 5, 31, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/Nothilfe/Qualitaetsgesichert": {
        "first_data": dt.datetime(2013, 12, 31, 23),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)",
    },
    "/NrvSaldo/reBAP/Qualitaetsgesichert": {
        "first_data": dt.datetime(2013, 12, 31, 23),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;reBAP unterdeckt;reBAP ueberdeckt",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;reBAP unterdeckt;reBAP ueberdeckt",
    },
    "/NrvSaldo/AEPModule/Qualitaetsgesichert": {
        "first_data": dt.datetime(2022, 6, 21, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;AEP Modul 1;AEP Modul 2;AEP Modul 3",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;AEP Modul 1;AEP Modul 2;AEP Modul 3",
    },
    "/NrvSaldo/FinanzielleWirkungAEPModule/Qualitaetsgesichert": {
        "first_data": dt.datetime(2022, 6, 21, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;AEP Modul 1;AEP Modul 2;AEP Modul 3",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;AEP Modul 1;AEP Modul 2;AEP Modul 3",
    },
    "/NrvSaldo/AepSchaetzer/Betrieblich": {
        "first_data": dt.datetime(2023, 3, 13, 23),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;AEP-Schätzer;Status",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;AEP-Schätzer;Status",
    },
    "/NrvSaldo/AbschaltbareLasten/Betrieblich": {
        "first_data": dt.datetime(2023, 11, 30, 23),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;Deutschland (Positiv);50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;Deutschland (Positiv);50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv)",
    },
    "/NrvSaldo/AbschaltbareLasten/Qualitaetsgesichert": {
        "first_data": dt.datetime(2023, 11, 30, 23),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;Deutschland (Positiv);50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;Deutschland (Positiv);50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv)",
    },
    "/NrvSaldo/VoAA/Qualitaetsgesichert": {
        "first_data": dt.datetime(2023, 11, 1),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;VoAA (Positiv);VoAA (Negativ)",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Einheit;VoAA (Positiv);VoAA (Negativ)",
    },
    "/NrvSaldo/SrlMolAbweichungen/Betrieblich": {
        "first_data": dt.datetime(2023, 12, 31, 23),
        "header": "Datum von;Zeitzone von;Uhrzeit von;Datum bis;Zeitzone bis;Uhrzeit bis;Datenkategorie;Datentyp;Abruf-ÜNB;Störung in der MOL-Verarbeitung;Trennung von SRL-Kooperation;Sonstiges",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Abruf-ÜNB;Störung in der MOL-Verarbeitung;Trennung von SRL-Kooperation;Sonstiges",
    },
    "/NrvSaldo/MrlMolAbweichungen/Betrieblich": {
        "first_data": dt.datetime(2023, 12, 31, 23),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Netzengpass;Technische Störung Abrufsystem;Technische Störung Anbieter;Test Aktivierung",
        "transformed_header": "von;bis;Datenkategorie;Datentyp;Netzengpass;Technische Störung Abrufsystem;Technische Störung Anbieter;Test Aktivierung",
    },
    "/AusgewieseneABSM": {
        "first_data": dt.datetime(2024, 9, 30, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Einheit;H1;H2;T1;T2;T3;T4;T5;T6",
        "transformed_header": "von;bis;Datenkategorie;Einheit;H1;H2;T1;T2;T3;T4;T5;T6",
    },
    "/ZugeteilteABSM": {
        "first_data": dt.datetime(2024, 9, 30, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;Einheit;H1;H2;T1;T2;T3;T4;T5;T6",
        "transformed_header": "von;bis;Datenkategorie;Einheit;H1;H2;T1;T2;T3;T4;T5;T6",
    },
    "/Erzeugungsverbot": {
        "first_data": dt.datetime(2024, 9, 30, 22),
        "header": "Datum;Zeitzone;von;bis;Datenkategorie;H1;H2;T1;T2;T3;T4;T5;T6",
        "transformed_header": "von;bis;Datenkategorie;H1;H2;T1;T2;T3;T4;T5;T6",
    },
}
