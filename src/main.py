# module gui cross-platforme
import wx
import wx.dataview as dv
import wx.adv
# module de manipulation de l'os et des threads
import threading
from cleaner import Cleaner
from infos import *
from langs import *

class FlatsweepLight(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title=f"{nomApp} v{versionApp}")
        self.SetSize(522, 600)
        self.SetMinSize((400, 300))
        self.icone = wx.Icon(chemin_fichier_icon, wx.BITMAP_TYPE_PNG)
        self.SetIcon(self.icone)
        self.cleaner = Cleaner()
        self.init_ui()

    def init_ui(self):
        # ------------------------ contenu de la gui
        self.panneau = wx.Panel(self)
        self.sizer_principal = wx.BoxSizer(wx.VERTICAL)
        # ------------------------ bande de titre personnalisée
        self.bande_titre = wx.Panel(self.panneau)
        self.bande_titre.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_ACTIVECAPTION))
        self.sizer_bande_titre = wx.BoxSizer(wx.HORIZONTAL)
        # ------------------------ conteneur vertical pour titre et sous-titre
        self.sizer_titres = wx.BoxSizer(wx.VERTICAL)
        # ------------------------ titre à gauche
        self.titre = wx.StaticText(self.bande_titre, label=f"{nomApp}")
        self.titre.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.sizer_titres.Add(self.titre, 0, wx.BOTTOM, 5)
        # ------------------------ sous titre sous le titre à gauche
        self.sous_titre = wx.StaticText(self.bande_titre, label=txt_sous_titre)
        self.sous_titre.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.sizer_titres.Add(self.sous_titre, 0)
        # ------------------------ ajouter le conteneur des titres au sizer de la bande
        self.sizer_bande_titre.Add(self.sizer_titres, 1, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, 10)
        # ------------------------ bouton "A propos" à droite
        self.bouton_infos = wx.Button(self.bande_titre, label=txt_bouton_info, size=(80, -1))
        self.bouton_infos.Bind(wx.EVT_BUTTON, self.afficher_about)
        self.sizer_bande_titre.Add(self.bouton_infos, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP | wx.BOTTOM, 10)
        self.bande_titre.SetSizer(self.sizer_bande_titre)
        # ------------------------ ajouter la bande de titre au sizer principal
        self.sizer_principal.Add(self.bande_titre, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 0)       # self.sizer_principal.Add(self.bande_titre, 0, wx.EXPAND)

        # ------------------------------------------------ reste de la fenêtre
        # ------------------------ sizer horizontal pour les boutons
        self.sizer_boutons = wx.BoxSizer(wx.HORIZONTAL)
        # ------------------------ bouton pour scanner les éléments inutiles
        self.bouton_scan = wx.Button(self.panneau, label=txt_bouton_scan)
        self.bouton_scan.Bind(wx.EVT_BUTTON, self.event_scan)
        self.sizer_boutons.Add(self.bouton_scan, 0, wx.RIGHT, 5)
        # ------------------------ bouton pour effacer les éléments inutiles
        self.bouton_nettoyage = wx.Button(self.panneau, label=txt_bouton_clean)
        self.bouton_nettoyage.Bind(wx.EVT_BUTTON, self.event_nettoyage)
        self.bouton_nettoyage.Disable()
        self.sizer_boutons.Add(self.bouton_nettoyage, 0, wx.LEFT, 5)
        # ajouter le sizer des boutons au sizer principal
        self.sizer_principal.Add(self.sizer_boutons, 0, wx.ALL | wx.CENTER, 10)
        # ------------------------ barre de progression
        self.barre_progression = wx.Gauge(self.panneau, range=100, style=wx.GA_HORIZONTAL)
        self.sizer_principal.Add(self.barre_progression, 0, wx.ALL | wx.EXPAND, 10)
        self.barre_progression.Hide()
        # ------------------------ liste des éléments inutiles trouvés
        self.liste_ctrl_elements_trouves = dv.DataViewListCtrl(self.panneau, style=dv.DV_ROW_LINES | dv.DV_VERT_RULES)
        self.liste_ctrl_elements_trouves.AppendTextColumn("Chemin", width=300)
        self.liste_ctrl_elements_trouves.AppendTextColumn("Taille", width=100)
        self.liste_ctrl_elements_trouves.AppendToggleColumn("Sélectionner", width=100)
        self.sizer_principal.Add(self.liste_ctrl_elements_trouves, 1, wx.ALL | wx.EXPAND, 10)
        
        self.panneau.SetSizer(self.sizer_principal)

    def event_scan(self, event):
        self.bouton_scan.Disable()
        self.barre_progression.Show()
        self.liste_ctrl_elements_trouves.DeleteAllItems()
        self.bouton_nettoyage.Disable()
        
        fil = threading.Thread(target=self.thread_scan)
        fil.start()

    def thread_scan(self):
        self.dossiers_residuels = self.cleaner.scanner()
        wx.CallAfter(self.maj_interface_apres_scan)

    def maj_interface_apres_scan(self):
        self.barre_progression.Hide()
        self.bouton_scan.Enable()
        
        if self.dossiers_residuels:
            for chemin_dossier, taille in self.dossiers_residuels:
                self.liste_ctrl_elements_trouves.AppendItem([chemin_dossier, self.cleaner.formater_taille(taille), False])
            self.bouton_nettoyage.Enable()
        else:
            self.liste_ctrl_elements_trouves.AppendItem(["Aucun répertoire résiduel trouvé.", "", False])

    def event_nettoyage(self, event):
        dlg = wx.MessageDialog(self, "Êtes-vous sûr de vouloir supprimer ces répertoires ?", "Confirmation", wx.YES_NO | wx.ICON_QUESTION)
        resultat = dlg.ShowModal()
        if resultat == wx.ID_YES:
            self.bouton_nettoyage.Disable()
            self.barre_progression.Show()
            fil = threading.Thread(target=self.thread_nettoyage)
            fil.start()

    def thread_nettoyage(self):
        dirs_to_clean = [self.dossiers_residuels[ligne][0] for ligne in range(self.liste_ctrl_elements_trouves.GetItemCount()) if self.liste_ctrl_elements_trouves.GetToggleValue(ligne, 2)]
        errors = self.cleaner.clean(dirs_to_clean)
        wx.CallAfter(self.maj_interface_apres_nettoyage, errors)

    def maj_interface_apres_nettoyage(self, errors):
        self.barre_progression.Hide()
        self.liste_ctrl_elements_trouves.DeleteAllItems()
        if errors:
            for dir_path, error_msg in errors:
                self.liste_ctrl_elements_trouves.AppendItem([f"Erreur lors de la suppression de {dir_path}: {error_msg}", "", False])
        else:
            self.liste_ctrl_elements_trouves.AppendItem(["Nettoyage terminé.", "", False])
        self.bouton_nettoyage.Disable()

    def afficher_about(self, event):
        # afficher boîte de dialogue "À propos"
        info = wx.adv.AboutDialogInfo()
        info.SetName(nomApp)
        info.SetIcon(self.icone)
        info.SetVersion(versionApp)
        info.SetDescription(descriptionApp)
        info.SetLicence(licenceApp)
        info.SetWebSite(lienApp)
        info.AddDeveloper(auteurApp)
        wx.adv.AboutBox(info)

if __name__ == "__main__":
    app = wx.App()
    fenetre = FlatsweepLight()
    fenetre.Show()
    app.MainLoop()