# importation des module de manipulaion de l'os et des fichiers
import os
import shutil

class Cleaner:
    def __init__(self):
        self.rep_donnees_utilisateur_flatpak = os.path.expanduser("~/.var/app")
        self.rep_installation_systeme_flatpak = "/var/lib/flatpak/app"
        self.rep_installation_utilisateur_flatpak = os.path.expanduser("~/.local/share/flatpak/app")
        self.donnees_residuelles = []

    def scanner(self):
        self.donnees_residuelles = []
        apps_installees = self.obtenir_apps_installees()
        
        if os.path.exists(self.rep_donnees_utilisateur_flatpak):
            for element in os.listdir(self.rep_donnees_utilisateur_flatpak):
                chemin_complet = os.path.join(self.rep_donnees_utilisateur_flatpak, element)
                if os.path.isdir(chemin_complet) and element not in apps_installees:
                    taille = self.obtenir_taille_repertoire(chemin_complet)
                    self.donnees_residuelles.append((chemin_complet, taille))
        
        return self.donnees_residuelles

    def obtenir_apps_installees(self):
        apps_installees = []
        if os.path.exists(self.rep_installation_systeme_flatpak):
            apps_installees += os.listdir(self.rep_installation_systeme_flatpak)
        if os.path.exists(self.rep_installation_utilisateur_flatpak):
            apps_installees += os.listdir(self.rep_installation_utilisateur_flatpak)
        return list(set(apps_installees))  # supprimer les doublons

    def clean(self, repertoires_a_nettoyer):
        erreurs = []
        for chemin_repertoire in repertoires_a_nettoyer:
            try:
                shutil.rmtree(chemin_repertoire)
            except Exception as e:
                erreurs.append((chemin_repertoire, str(e)))
        return erreurs

    def obtenir_taille_repertoire(self, chemin):
        taille_totale = 0
        for chemin_repertoire, noms_repertoires, noms_fichiers in os.walk(chemin):
            for f in noms_fichiers:
                fp = os.path.join(chemin_repertoire, f)
                taille_totale += os.path.getsize(fp)
        return taille_totale

    @staticmethod
    def formater_taille(taille):
        for unite in ['o', 'Ko', 'Mo', 'Go', 'To']:
            if taille < 1024.0:
                return f"{taille:.1f} {unite}"
            taille /= 1024.0