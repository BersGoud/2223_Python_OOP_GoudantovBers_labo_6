# Opdracht Labo 6 Python OOP
# Made by Bers Goudantov, 1ITAI :)
""" BELANGERIJK!!!
    Volgende elementen moeten geïnstalleerd worden via pip install om de programma te laten werken:
    * pyautogui = cmd (py -m pip install pyautogui)
    * jinja2 = cmd (py -m pip install jinja2)
    * ping3 = cmd (py -m pip install ping3)
"""
import json
import sys
import webbrowser
import time
from datetime import datetime
from ping3 import ping
from jinja2 import Environment, FileSystemLoader
import pyautogui

""" De benodigende files:
    * server_list.json bevat een lijst van alle opgeslagen servers
    *server_status_report.html word gebruikt als een template om de rapport.html aan te maken.
    *log.json wordt alle logs opgeslagen van de ping commando's en getoond in de rapport.html, note bij het uitvoeren van de programma word deze file automatisch leeg gemaakt.
"""
SERVERS_FILE = "server_list.json"
TEMPLATE_FILE = "templates/server_status_report.html"
LOG_FILES = "log.json"

""" Deze methode laad alle files op van de server_list.json op"""
def load_servers():
    try:
        with open(SERVERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

""" Deze methode verwijdert alles in de log.json file"""
def clear_log_file():
    with open(LOG_FILES, "w") as f:
        f.write("")

""" Nieuwe servers of aanpassingen worden opgeslagen in de server_list.json file"""
def save_servers(servers):
    with open(SERVERS_FILE, 'w') as f:
        json.dump(servers, f, indent=4)

""" Deze methode maakt een nieuwe server aan een voegt dit toe aan het server_list.json file via de methode save_servers"""
def add_server(server_list, name, ip):
    if name in server_list:
        print("Server met die naam bestaat al.")
        return
    server_list[name] = {"ip": ip, "status": "OK", "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    save_servers(server_list)
    print(f"Server {name} toegevoegd.")

""" Deze methode verwijdert een server van de list"""
def remove_server(server_list, name):
    if name in server_list:
        del server_list[name]
        save_servers(server_list)
        print(f"Server {name} verwijderd.")
    else:
        print(f"Server met naam {name} bestaat niet.")

""" Toont een lijst van alle servers die opgeslagen zijn in de list"""
def list_servers(server_list):
    if server_list:
        print("Beschikbare servers:")
        for name, server in server_list.items():
            print(f"{name}: {server['ip']} ({server['status']})")
    else:
        print("Er zijn geen servers beschikbaar.")

""" Deze methode voert voor elke server in de list een ping check uit, de output hiervan word bekeken en opgeslagen in de log.json file.
    Nadien word de wijzigingen opgeslagen in de server_list.json file  via de methode save_severs().
    Ten laatste word een rapport.html file aangemaakt via de methode generate_report().
"""
def check_servers(server_list):
    for name, server in server_list.items():
        if ping(server["ip"]):
            server["status"] = "OK"
        elif not ping(server["ip"]):
            server["status"] = "FAIL"
        server["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_data = {"server": name, "ip": server["ip"], "status": server["status"], "timestamp": server["last_check"]}
        with open(LOG_FILES, "a") as f:
            f.write(json.dumps(log_data) + "\n")
    
    save_servers(server_list)
    generate_report(server_list)

""" Hier word vanuit de server_list argument een rapport.html file aangemaakt. Verder nog worden de waardes van de log.json file opgenomen die genereert zijn via de methode check_servers().
    Ook word hier de template file gebruikt voor de opmaak en aanmaken van de rapport.html file, en ook word een javascript code geïnjecteerd bij het script tag van de template file in de rapport.html.
    Deze javascript code voegt een funcite toe die het toelaat bij het indrukken van de knop "sluiten" de pagina volledig afsluiten.
"""
def generate_report(server_list):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(TEMPLATE_FILE)
    with open(LOG_FILES, 'r') as f:
        log_lines = [json.loads(line.strip()) for line in f]
    with open('rapport.html', 'w') as f:
        javascriptCode = '''
        function Close() { setTimeout(function() { window.close(); }, 1000); } '''
        rendered = template.render(servers=[{"name": name, **server} if "name" not in server else server for name, server in server_list.items()], log_lines=log_lines, script = javascriptCode)
        f.write(rendered)

""" De main methode dient als een gebruiker interface."""
def main():
    """ Bij het starten word de log file leeggemaakt."""
    clear_log_file()
    command = sys.argv[1] if len(sys.argv) > 1 else None # sys argumenten word aangemaakt om als commands te gebruiken wanneer je de main.py toespreekt.
    servers = load_servers() # server file word ingeladen binnen het programma.

    if command == "add": # Bij het command add word de gebruiker overgebracht naar het gedeelte 'server' toevegen.
        name = input("Servernaam: ")
        ip = input("IP-adres: ")
        
        add_server(servers, name, ip)
        
    elif command == "remove": # Bij het command remove word de gebruiker overgebracht naar het gedeelte 'server' verwijderen.
        name = input("Servernaam: ")
        remove_server(servers, name)
        
    elif command == "list": # Bij het command list krijgt de gebruiker een overzicht van alle servers.
        list_servers(servers)
    
    elif command == "check": # Bij het command check word de gebruiker overgebracht naar het gedeelte 'servers' ping checken en controleren.
        iteratie = input("Voer het aantal pogingen in: ") # De gebruker word gevraagd om de aantal pogingen in te instellen.
        i = 1
        if iteratie and int(iteratie) >= 0:
            check_servers(servers)
            webbrowser.open_new_tab('rapport.html') # De aangemaakte rapport.html word geopened in de browser.
            while i < int(iteratie):
                time.sleep(1) # Voer een 1 seconde delay toe voor het uitvoeren van de ping check.
                check_servers(servers)
                generate_report(servers) # Er word een nieuwe rapport.html file aangemaakt en de oude word verwjdert.
                pyautogui.hotkey('f5') # De pagina word opnieuw geladen om de nieuwe waardes te tonen
                i += 1
        elif not iteratie: # Wanneer de gebruiker bij het input niks opgeeft.
            print("U heeft geen waarde opgegeven!")
        else: # Wanneer de gebruiker bij het input een negatieve getal opgeeft.
            print("U kunt geen negatieve waarde ingeven!")

    elif command == "help": # Bij het command help krijgt de gebruiker een korte uitleg over hoe hij/zij de programma kan gebruiken.
        print(" add: Voegt een nieuwe server toe aan de lijst.\n remove: Verwijdert een server van de lijst.\n list: Toont een overzicht van alle servers en hun status.\n check: Controleert de status van alle servers in de lijst.\n help: Toont deze helpinformatie.\n")
    else:
        print("Gebruik:  python main.py <add/remove/list/check/help>") # Wanneer de gebruiker geen commando's opgeeft voor het uitvoeren van de programma.

if __name__ =='__main__': # Hier word de main methode bij het uitvoeren van main.py als eerste aangesproken.
    main()