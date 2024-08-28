# infos app
versionApp = "0.1.0"
nomApp = "Flatsweep-light"
descriptionApp = "Une application pour nettoyer les fichiers résiduels de Flatpak."
auteurApp = "Pandaroux007"
lienApp = "https://github.com/pandaroux007/flatsweep-light"
licenceApp = ""

try:
    import os, sys
    repertoire_courant = os.path.dirname(os.path.abspath(os.path.realpath(sys.argv[0])))
    chemin_fichier_licence = os.path.join(os.path.dirname(repertoire_courant), "LICENCE.txt")
    chemin_fichier_icon = os.path.join(os.path.dirname(repertoire_courant), "data", "icon.png")
    del os, sys
except Exception as e:
    print(f"ERREUR >> Impossible de générer les chemins des fichiers d'icone et de licence\nERREUR : \t{e}")
    chemin_fichier_licence = None

# recuperation contenu du fichier de licence
if(chemin_fichier_licence != None):
    try:
        with open(chemin_fichier_licence, "r") as file:
            licenceApp = file.read()
    except FileNotFoundError:
        print(f"ERREUR >> Impossible de trouver le fichier de licence depuis le chemin suivant ({chemin_fichier_licence})!")
else: print("ERREUR >> Impossible de trouver le fichier de licence; chemin de fichier inexistant!")