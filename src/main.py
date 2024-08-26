import wx
import wx.dataview as dv
import os
import shutil
import subprocess
import threading

versionApp = "0.1.0"
nomApp = "Flatsweep-light"

class FlatsweepLight(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title=f"{nomApp} v{versionApp}")
        self.SetSize(400, 600)
        self.SetMinSize((400, 300))
        
        panneau = wx.Panel(self)
        sizer_principal = wx.BoxSizer(wx.VERTICAL)
        
        titre = wx.StaticText(panneau, label=f"{nomApp}")
        titre.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer_principal.Add(titre, 0, wx.ALL | wx.CENTER, 5)
        
        description = wx.StaticText(panneau, label="Nettoyer les fichiers résiduels de Flatpak")
        sizer_principal.Add(description, 0, wx.ALL | wx.CENTER, 5)
        
        self.bouton_scan = wx.Button(panneau, label="Scanner")
        self.bouton_scan.Bind(wx.EVT_BUTTON, self.au_scan)
        sizer_principal.Add(self.bouton_scan, 0, wx.ALL | wx.CENTER, 10)
        
        self.barre_progression = wx.Gauge(panneau, range=100, style=wx.GA_HORIZONTAL)
        sizer_principal.Add(self.barre_progression, 0, wx.ALL | wx.EXPAND, 10)
        self.barre_progression.Hide()
        
        self.liste_ctrl = dv.DataViewListCtrl(panneau, style=dv.DV_ROW_LINES | dv.DV_VERT_RULES)
        self.liste_ctrl.AppendTextColumn("Chemin", width=300)
        self.liste_ctrl.AppendTextColumn("Taille", width=100)
        self.liste_ctrl.AppendToggleColumn("Sélectionner", width=100)
        sizer_principal.Add(self.liste_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        
        self.bouton_nettoyage = wx.Button(panneau, label="Nettoyer")
        self.bouton_nettoyage.Bind(wx.EVT_BUTTON, self.au_nettoyage)
        sizer_principal.Add(self.bouton_nettoyage, 0, wx.ALL | wx.CENTER, 10)
        self.bouton_nettoyage.Disable()
        
        panneau.SetSizer(sizer_principal)
        
        self.dossier_flatpak = os.path.expanduser("~/.var/app")
        self.dossiers_residuels = []

    def au_scan(self, evenement):
        self.bouton_scan.Disable()
        self.barre_progression.Show()
        self.liste_ctrl.DeleteAllItems()
        self.bouton_nettoyage.Disable()
        
        fil = threading.Thread(target=self.fil_scan)
        fil.start()

    def fil_scan(self):
        self.dossiers_residuels = []
        apps_installees = self.obtenir_apps_installees()
        
        for element in os.listdir(self.dossier_flatpak):
            chemin_complet = os.path.join(self.dossier_flatpak, element)
            if os.path.isdir(chemin_complet) and element not in apps_installees:
                taille = self.obtenir_taille_dossier(chemin_complet)
                self.dossiers_residuels.append((chemin_complet, taille))
        
        wx.CallAfter(self.maj_ui_apres_scan)

    def maj_ui_apres_scan(self):
        self.barre_progression.Hide()
        self.bouton_scan.Enable()
        
        if self.dossiers_residuels:
            for chemin_dossier, taille in self.dossiers_residuels:
                self.liste_ctrl.AppendItem([chemin_dossier, self.formater_taille(taille), False])
            self.bouton_nettoyage.Enable()
        else:
            self.liste_ctrl.AppendItem(["Aucun répertoire résiduel trouvé.", "", False])

    def obtenir_apps_installees(self):
        resultat = subprocess.run(["flatpak", "list", "--app", "--columns=application"], capture_output=True, text=True)
        return resultat.stdout.strip().split('\n')

    def au_nettoyage(self, evenement):
        dlg = wx.MessageDialog(self, "Êtes-vous sûr de vouloir supprimer ces répertoires ?", "Confirmation", wx.YES_NO | wx.ICON_QUESTION)
        resultat = dlg.ShowModal()
        if resultat == wx.ID_YES:
            self.bouton_nettoyage.Disable()
            self.barre_progression.Show()
            fil = threading.Thread(target=self.fil_nettoyage)
            fil.start()

    def fil_nettoyage(self):
        for ligne in range(self.liste_ctrl.GetItemCount()):
            if self.liste_ctrl.GetToggleValue(ligne, 2):
                dossier_a_supprimer = self.dossiers_residuels[ligne][0]
                try:
                    shutil.rmtree(dossier_a_supprimer)
                except Exception as e:
                    print(f"Erreur lors de la suppression de {dossier_a_supprimer}: {str(e)}")
        
        wx.CallAfter(self.maj_ui_apres_nettoyage)

    def maj_ui_apres_nettoyage(self):
        self.barre_progression.Hide()
        self.liste_ctrl.DeleteAllItems()
        self.dossiers_residuels = []
        self.liste_ctrl.AppendItem(["Nettoyage terminé.", "", False])
        self.bouton_nettoyage.Disable()

    def obtenir_taille_dossier(self, chemin):
        taille_totale = 0
        for chemin_dossier, noms_dossiers, noms_fichiers in os.walk(chemin):
            for f in noms_fichiers:
                fp = os.path.join(chemin_dossier, f)
                taille_totale += os.path.getsize(fp)
        return taille_totale

    def formater_taille(self, taille):
        for unite in ['B', 'KB', 'MB', 'GB', 'TB']:
            if taille < 1024.0:
                return f"{taille:.1f} {unite}"
            taille /= 1024.0

if __name__ == "__main__":
    app = wx.App()
    fenetre = FlatsweepLight()
    fenetre.Show()
    app.MainLoop()
