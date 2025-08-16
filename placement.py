#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DonneesEntreprise:
    """Structure pour stocker les données financières d'une entreprise"""
    nom: str
    symbole: str  # Ticker symbol (ex: AAPL, GOOGL)
    prix_action: float
    benefice_par_action: float  # EPS
    valeur_comptable_par_action: float  # Book Value per Share
    revenus_actuels: float
    revenus_annee_precedente: float
    dette_totale: float
    capitaux_propres: float
    croissance_benefices_prevue: float  # en pourcentage annuel
    secteur: str
    capitalisation_boursiere: float


class RecuperateurDonneesAPI:
    """
    Classe pour récupérer les données financières via l'API Alpha Vantage
    """
    
    def __init__(self, api_key: str = "demo"):
        """
        Initialise le récupérateur avec une clé API
        Utilisez 'demo' pour les tests, mais obtenez une vraie clé sur alphavantage.co
        """
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        
        # Mapping des secteurs en anglais vers français
        self.secteurs_mapping = {
            "TECHNOLOGY": "technologie",
            "FINANCIAL SERVICES": "finance",
            "HEALTHCARE": "sante",
            "INDUSTRIALS": "industrie",
            "CONSUMER DISCRETIONARY": "consommation",
            "CONSUMER STAPLES": "consommation",
            "ENERGY": "energie",
            "UTILITIES": "energie",
            "MATERIALS": "industrie",
            "REAL ESTATE": "finance",
            "COMMUNICATION SERVICES": "technologie"
        }
    
    def rechercher_symbole(self, nom_entreprise: str) -> Optional[str]:
        """
        Recherche le symbole boursier d'une entreprise à partir de son nom
        """
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": nom_entreprise,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if "bestMatches" in data and len(data["bestMatches"]) > 0:
                # Prendre le premier résultat (le plus pertinent)
                match = data["bestMatches"][0]
                symbole = match["1. symbol"]
                nom_complet = match["2. name"]
                print(f"✅ Entreprise trouvée: {nom_complet} ({symbole})")
                return symbole
            else:
                print(f"❌ Aucune entreprise trouvée pour: {nom_entreprise}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return None
    
    def obtenir_apercu_entreprise(self, symbole: str) -> Optional[Dict]:
        """
        Récupère les informations générales de l'entreprise
        """
        params = {
            "function": "OVERVIEW",
            "symbol": symbole,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if "Symbol" in data:
                return data
            else:
                print(f"❌ Données d'aperçu non disponibles pour {symbole}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de l'aperçu: {e}")
            return None
    
    def obtenir_revenus_annuels(self, symbole: str) -> Optional[Dict]:
        """
        Récupère les revenus annuels de l'entreprise
        """
        params = {
            "function": "INCOME_STATEMENT",
            "symbol": symbole,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if "annualReports" in data:
                return data
            else:
                print(f"⚠️ Données de revenus non disponibles pour {symbole}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des revenus: {e}")
            return None
    
    def obtenir_bilan(self, symbole: str) -> Optional[Dict]:
        """
        Récupère le bilan de l'entreprise
        """
        params = {
            "function": "BALANCE_SHEET",
            "symbol": symbole,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if "annualReports" in data:
                return data
            else:
                print(f"⚠️ Données de bilan non disponibles pour {symbole}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du bilan: {e}")
            return None
    
    def convertir_valeur(self, valeur_str: str) -> float:
        """
        Convertit une chaîne de caractères en float, gère 'None' et les valeurs vides
        """
        if not valeur_str or valeur_str == "None" or valeur_str == "-":
            return 0.0
        try:
            return float(valeur_str)
        except:
            return 0.0
    
    def detecter_secteur(self, secteur_api: str) -> str:
        """
        Convertit le secteur de l'API en secteur français
        """
        secteur_upper = secteur_api.upper()
        return self.secteurs_mapping.get(secteur_upper, "defaut")
    
    def recuperer_donnees_entreprise(self, nom_entreprise: str) -> Optional[DonneesEntreprise]:
        """
        Récupère toutes les données nécessaires pour une entreprise
        """
        print(f"🔍 Recherche des données pour: {nom_entreprise}")
        print("-" * 50)
        
        # 1. Rechercher le symbole
        symbole = self.rechercher_symbole(nom_entreprise)
        if not symbole:
            return None
        
        print("⏳ Récupération des données financières...")
        
        # 2. Récupérer l'aperçu général (ratios principaux)
        apercu = self.obtenir_apercu_entreprise(symbole)
        if not apercu:
            return None
        
        # Petite pause pour éviter de surcharger l'API
        time.sleep(1)
        
        # 3. Récupérer les revenus
        revenus_data = self.obtenir_revenus_annuels(symbole)
        
        # Petite pause pour éviter de surcharger l'API
        time.sleep(1)
        
        # 4. Récupérer le bilan
        bilan_data = self.obtenir_bilan(symbole)
        
        try:
            # Extraction des données de l'aperçu
            nom = apercu.get("Name", nom_entreprise)
            prix_action = self.convertir_valeur(apercu.get("50DayMovingAverage", "0"))
            if prix_action == 0:  # Fallback si pas de prix moyen
                prix_action = self.convertir_valeur(apercu.get("PreviousClose", "100"))
            
            benefice_par_action = self.convertir_valeur(apercu.get("EPS", "0"))
            valeur_comptable_par_action = self.convertir_valeur(apercu.get("BookValue", "0"))
            capitalisation_boursiere = self.convertir_valeur(apercu.get("MarketCapitalization", "0")) / 1_000_000  # Conversion en millions
            
            pe_ratio = self.convertir_valeur(apercu.get("PERatio", "0"))
            secteur = self.detecter_secteur(apercu.get("Sector", ""))
            
            # Estimation de la croissance des bénéfices
            peg_ratio = self.convertir_valeur(apercu.get("PEGRatio", "0"))
            if peg_ratio > 0 and pe_ratio > 0:
                croissance_benefices_prevue = pe_ratio / peg_ratio if peg_ratio != 0 else 10.0
            else:
                croissance_benefices_prevue = 10.0  # Valeur par défaut
            
            # Extraction des revenus
            revenus_actuels = 0
            revenus_annee_precedente = 0
            
            if revenus_data and "annualReports" in revenus_data and len(revenus_data["annualReports"]) >= 2:
                revenus_actuels = self.convertir_valeur(revenus_data["annualReports"][0].get("totalRevenue", "0")) / 1_000_000
                revenus_annee_precedente = self.convertir_valeur(revenus_data["annualReports"][1].get("totalRevenue", "0")) / 1_000_000
            
            # Extraction du bilan
            dette_totale = 0
            capitaux_propres = 0
            
            if bilan_data and "annualReports" in bilan_data and len(bilan_data["annualReports"]) >= 1:
                dernier_bilan = bilan_data["annualReports"][0]
                dette_totale = self.convertir_valeur(dernier_bilan.get("totalDebt", "0")) / 1_000_000
                if dette_totale == 0:  # Fallback
                    dette_totale = self.convertir_valeur(dernier_bilan.get("longTermDebt", "0")) / 1_000_000
                
                capitaux_propres = self.convertir_valeur(dernier_bilan.get("totalShareholderEquity", "0")) / 1_000_000
            
            # Validation des données essentielles
            if benefice_par_action <= 0:
                print("⚠️ Attention: Bénéfice par action manquant ou négatif")
            if valeur_comptable_par_action <= 0:
                print("⚠️ Attention: Valeur comptable par action manquante")
            
            print("✅ Données récupérées avec succès!")
            
            return DonneesEntreprise(
                nom=nom,
                symbole=symbole,
                prix_action=prix_action,
                benefice_par_action=benefice_par_action,
                valeur_comptable_par_action=valeur_comptable_par_action,
                revenus_actuels=revenus_actuels,
                revenus_annee_precedente=revenus_annee_precedente,
                dette_totale=dette_totale,
                capitaux_propres=capitaux_propres,
                croissance_benefices_prevue=croissance_benefices_prevue,
                secteur=secteur,
                capitalisation_boursiere=capitalisation_boursiere
            )
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement des données: {e}")
            return None


class AnalyseurSousEvaluation:
    """
    Classe principale pour analyser si une entreprise est sous-évaluée
    """
    
    def __init__(self):
        # Valeurs de référence moyennes par secteur (exemples réalistes)
        self.references_secteur = {
            "technologie": {"pe_moyen": 25, "pb_moyen": 4.5, "croissance_moyenne": 15},
            "finance": {"pe_moyen": 12, "pb_moyen": 1.2, "croissance_moyenne": 8},
            "sante": {"pe_moyen": 18, "pb_moyen": 3.0, "croissance_moyenne": 12},
            "industrie": {"pe_moyen": 16, "pb_moyen": 2.5, "croissance_moyenne": 6},
            "consommation": {"pe_moyen": 20, "pb_moyen": 3.5, "croissance_moyenne": 10},
            "energie": {"pe_moyen": 14, "pb_moyen": 1.8, "croissance_moyenne": 5},
            "defaut": {"pe_moyen": 18, "pb_moyen": 2.8, "croissance_moyenne": 10}
        }
        
    def calculer_ratio_pe(self, donnees: DonneesEntreprise) -> float:
        """
        Calcule le ratio Price-to-Earnings (P/E)
        P/E = Prix de l'action / Bénéfice par action
        """
        if donnees.benefice_par_action <= 0:
            return float('inf')
        return donnees.prix_action / donnees.benefice_par_action
    
    def calculer_ratio_pb(self, donnees: DonneesEntreprise) -> float:
        """
        Calcule le ratio Price-to-Book (P/B)
        P/B = Prix de l'action / Valeur comptable par action
        """
        if donnees.valeur_comptable_par_action <= 0:
            return float('inf')
        return donnees.prix_action / donnees.valeur_comptable_par_action
    
    def calculer_ratio_peg(self, donnees: DonneesEntreprise) -> float:
        """
        Calcule le ratio PEG (Price/Earnings to Growth)
        PEG = P/E / Taux de croissance des bénéfices
        Un PEG < 1 indique généralement une sous-évaluation
        """
        pe_ratio = self.calculer_ratio_pe(donnees)
        if pe_ratio == float('inf') or donnees.croissance_benefices_prevue <= 0:
            return float('inf')
        return pe_ratio / donnees.croissance_benefices_prevue
    
    def calculer_croissance_revenus(self, donnees: DonneesEntreprise) -> float:
        """
        Calcule le taux de croissance des revenus (en pourcentage)
        """
        if donnees.revenus_annee_precedente <= 0:
            return 0
        return ((donnees.revenus_actuels - donnees.revenus_annee_precedente) / 
                donnees.revenus_annee_precedente) * 100
    
    def calculer_ratio_endettement(self, donnees: DonneesEntreprise) -> float:
        """
        Calcule le ratio d'endettement
        Ratio = Dette totale / Capitaux propres
        """
        if donnees.capitaux_propres <= 0:
            return float('inf')
        return donnees.dette_totale / donnees.capitaux_propres
    
    def obtenir_references(self, secteur: str) -> Dict[str, float]:
        """
        Obtient les valeurs de référence pour un secteur donné
        """
        secteur_key = secteur.lower()
        return self.references_secteur.get(secteur_key, self.references_secteur["defaut"])
    
    def evaluer_ratio_pe(self, pe_ratio: float, references: Dict[str, float]) -> Tuple[int, str]:
        """
        Évalue le ratio P/E par rapport aux références du secteur
        Retourne un score (0-100) et une explication
        """
        pe_reference = references["pe_moyen"]
        
        if pe_ratio == float('inf'):
            return 0, "P/E infini (pas de bénéfices) - très risqué"
        
        if pe_ratio < pe_reference * 0.7:  # 30% sous la moyenne
            return 90, f"P/E très faible ({pe_ratio:.1f} vs {pe_reference:.1f}) - potentiellement sous-évaluée"
        elif pe_ratio < pe_reference * 0.85:  # 15% sous la moyenne
            return 70, f"P/E faible ({pe_ratio:.1f} vs {pe_reference:.1f}) - possiblement sous-évaluée"
        elif pe_ratio < pe_reference * 1.15:  # Dans la normale
            return 50, f"P/E normal ({pe_ratio:.1f} vs {pe_reference:.1f}) - valorisation équitable"
        elif pe_ratio < pe_reference * 1.5:  # Élevé
            return 30, f"P/E élevé ({pe_ratio:.1f} vs {pe_reference:.1f}) - possiblement surévaluée"
        else:
            return 10, f"P/E très élevé ({pe_ratio:.1f} vs {pe_reference:.1f}) - probablement surévaluée"
    
    def evaluer_ratio_pb(self, pb_ratio: float, references: Dict[str, float]) -> Tuple[int, str]:
        """
        Évalue le ratio P/B par rapport aux références du secteur
        """
        pb_reference = references["pb_moyen"]
        
        if pb_ratio < pb_reference * 0.6:
            return 85, f"P/B très faible ({pb_ratio:.1f} vs {pb_reference:.1f}) - forte sous-évaluation possible"
        elif pb_ratio < pb_reference * 0.8:
            return 65, f"P/B faible ({pb_ratio:.1f} vs {pb_reference:.1f}) - sous-évaluation possible"
        elif pb_ratio < pb_reference * 1.2:
            return 50, f"P/B normal ({pb_ratio:.1f} vs {pb_reference:.1f}) - valorisation équitable"
        else:
            return 25, f"P/B élevé ({pb_ratio:.1f} vs {pb_reference:.1f}) - possiblement surévaluée"
    
    def evaluer_ratio_peg(self, peg_ratio: float) -> Tuple[int, str]:
        """
        Évalue le ratio PEG (indépendant du secteur)
        """
        if peg_ratio == float('inf'):
            return 20, "PEG non calculable - croissance ou bénéfices insuffisants"
        elif peg_ratio < 0.5:
            return 95, f"PEG excellent ({peg_ratio:.2f}) - très sous-évaluée"
        elif peg_ratio < 1.0:
            return 80, f"PEG bon ({peg_ratio:.2f}) - sous-évaluée"
        elif peg_ratio < 1.5:
            return 50, f"PEG acceptable ({peg_ratio:.2f}) - valorisation équitable"
        elif peg_ratio < 2.0:
            return 30, f"PEG élevé ({peg_ratio:.2f}) - possiblement surévaluée"
        else:
            return 10, f"PEG très élevé ({peg_ratio:.2f}) - probablement surévaluée"
    
    def evaluer_croissance(self, croissance_revenus: float, references: Dict[str, float]) -> Tuple[int, str]:
        """
        Évalue la croissance des revenus
        """
        croissance_ref = references["croissance_moyenne"]
        
        if croissance_revenus > croissance_ref * 1.5:
            return 80, f"Excellente croissance ({croissance_revenus:.1f}% vs {croissance_ref:.1f}%)"
        elif croissance_revenus > croissance_ref:
            return 65, f"Bonne croissance ({croissance_revenus:.1f}% vs {croissance_ref:.1f}%)"
        elif croissance_revenus > 0:
            return 45, f"Croissance modérée ({croissance_revenus:.1f}% vs {croissance_ref:.1f}%)"
        else:
            return 20, f"Croissance négative ({croissance_revenus:.1f}%) - préoccupant"
    
    def evaluer_endettement(self, ratio_endettement: float) -> Tuple[int, str]:
        """
        Évalue le niveau d'endettement
        """
        if ratio_endettement == float('inf'):
            return 0, "Endettement critique - capitaux propres négatifs"
        elif ratio_endettement < 0.3:
            return 80, f"Endettement faible ({ratio_endettement:.2f}) - situation financière saine"
        elif ratio_endettement < 0.6:
            return 60, f"Endettement modéré ({ratio_endettement:.2f}) - situation acceptable"
        elif ratio_endettement < 1.0:
            return 40, f"Endettement élevé ({ratio_endettement:.2f}) - surveillance nécessaire"
        else:
            return 20, f"Endettement très élevé ({ratio_endettement:.2f}) - risque important"
    
    def analyser_entreprise(self, donnees: DonneesEntreprise) -> Dict:
        """
        Analyse complète d'une entreprise pour déterminer si elle est sous-évaluée
        """
        print(f"\n🔍 ANALYSE DE {donnees.nom.upper()}")
        print("=" * 50)
        
        # Calcul des ratios
        pe_ratio = self.calculer_ratio_pe(donnees)
        pb_ratio = self.calculer_ratio_pb(donnees)
        peg_ratio = self.calculer_ratio_peg(donnees)
        croissance_revenus = self.calculer_croissance_revenus(donnees)
        ratio_endettement = self.calculer_ratio_endettement(donnees)
        
        # Obtenir les références du secteur
        references = self.obtenir_references(donnees.secteur)
        
        # Évaluation de chaque métrique
        score_pe, explication_pe = self.evaluer_ratio_pe(pe_ratio, references)
        score_pb, explication_pb = self.evaluer_ratio_pb(pb_ratio, references)
        score_peg, explication_peg = self.evaluer_ratio_peg(peg_ratio)
        score_croissance, explication_croissance = self.evaluer_croissance(croissance_revenus, references)
        score_endettement, explication_endettement = self.evaluer_endettement(ratio_endettement)
        
        # Calcul du score final pondéré
        # Les poids reflètent l'importance relative de chaque métrique
        poids = {
            "pe": 0.25,      # 25% - Très important pour la valorisation
            "pb": 0.20,      # 20% - Important pour la valeur intrinsèque
            "peg": 0.25,     # 25% - Très important (combine P/E et croissance)
            "croissance": 0.20,  # 20% - Important pour le potentiel futur
            "endettement": 0.10  # 10% - Important pour la stabilité
        }
        
        score_final = (
            score_pe * poids["pe"] +
            score_pb * poids["pb"] +
            score_peg * poids["peg"] +
            score_croissance * poids["croissance"] +
            score_endettement * poids["endettement"]
        )
        
        # Détermination de la conclusion
        if score_final >= 75:
            conclusion = "FORTEMENT SOUS-ÉVALUÉE 🚀"
            recommandation = "Achat fortement recommandé"
        elif score_final >= 60:
            conclusion = "SOUS-ÉVALUÉE ✅"
            recommandation = "Achat recommandé"
        elif score_final >= 40:
            conclusion = "VALORISATION ÉQUITABLE ⚖️"
            recommandation = "Tenir ou analyser davantage"
        elif score_final >= 25:
            conclusion = "POSSIBLEMENT SURÉVALUÉE ⚠️"
            recommandation = "Éviter ou vendre"
        else:
            conclusion = "SURÉVALUÉE ❌"
            recommandation = "Vente recommandée"
        
        # Affichage des résultats
        print(f"\n📊 RATIOS CALCULÉS:")
        print(f"  • P/E Ratio: {pe_ratio:.2f}" if pe_ratio != float('inf') else "  • P/E Ratio: N/A (pas de bénéfices)")
        print(f"  • P/B Ratio: {pb_ratio:.2f}")
        print(f"  • PEG Ratio: {peg_ratio:.2f}" if peg_ratio != float('inf') else "  • PEG Ratio: N/A")
        print(f"  • Croissance revenus: {croissance_revenus:.1f}%")
        print(f"  • Ratio endettement: {ratio_endettement:.2f}" if ratio_endettement != float('inf') else "  • Ratio endettement: N/A")
        
        print(f"\n📈 ÉVALUATIONS DÉTAILLÉES:")
        print(f"  • P/E: {score_pe}/100 - {explication_pe}")
        print(f"  • P/B: {score_pb}/100 - {explication_pb}")
        print(f"  • PEG: {score_peg}/100 - {explication_peg}")
        print(f"  • Croissance: {score_croissance}/100 - {explication_croissance}")
        print(f"  • Endettement: {score_endettement}/100 - {explication_endettement}")
        
        print(f"\n🎯 RÉSULTAT FINAL:")
        print(f"  Score global: {score_final:.1f}/100")
        print(f"  Conclusion: {conclusion}")
        print(f"  Recommandation: {recommandation}")
        
        return {
            "entreprise": donnees.nom,
            "secteur": donnees.secteur,
            "ratios": {
                "pe": pe_ratio,
                "pb": pb_ratio,
                "peg": peg_ratio,
                "croissance_revenus": croissance_revenus,
                "ratio_endettement": ratio_endettement
            },
            "scores": {
                "pe": score_pe,
                "pb": score_pb,
                "peg": score_peg,
                "croissance": score_croissance,
                "endettement": score_endettement,
                "final": score_final
            },
            "conclusion": conclusion,
            "recommandation": recommandation
        }


def analyser_entreprise_par_nom(nom_entreprise: str, api_key: str = "demo") -> bool:
    """
    Analyse une entreprise en récupérant automatiquement ses données via API
    """
    recuperateur = RecuperateurDonneesAPI(api_key)
    
    # Récupérer les données via l'API
    donnees = recuperateur.recuperer_donnees_entreprise(nom_entreprise)
    
    if donnees:
        # Analyser l'entreprise
        analyseur = AnalyseurSousEvaluation()
        resultat = analyseur.analyser_entreprise(donnees)
        return True
    else:
        print("❌ Impossible de récupérer les données de l'entreprise.")
        print("💡 Suggestions:")
        print("  - Vérifiez l'orthographe du nom")
        print("  - Essayez avec le symbole boursier (ex: AAPL pour Apple)")
        print("  - Assurez-vous que l'entreprise est cotée en bourse")
        return False


def saisir_donnees_entreprise() -> DonneesEntreprise:
    """
    Interface pour saisir manuellement les données d'une entreprise
    """
    print("📝 SAISIE MANUELLE DES DONNÉES")
    print("=" * 40)
    
    nom = input("Nom de l'entreprise: ")
    symbole = input("Symbole boursier (optionnel): ")
    prix_action = float(input("Prix actuel de l'action (€): "))
    benefice_par_action = float(input("Bénéfice par action - EPS (€): "))
    valeur_comptable_par_action = float(input("Valeur comptable par action (€): "))
    revenus_actuels = float(input("Revenus actuels (millions €): "))
    revenus_annee_precedente = float(input("Revenus année précédente (millions €): "))
    dette_totale = float(input("Dette totale (millions €): "))
    capitaux_propres = float(input("Capitaux propres (millions €): "))
    croissance_benefices_prevue = float(input("Croissance bénéfices prévue (%/an): "))
    capitalisation_boursiere = float(input("Capitalisation boursière (millions €): "))
    
    print("\nSecteurs disponibles:")
    print("  - technologie")
    print("  - finance") 
    print("  - sante")
    print("  - industrie")
    print("  - consommation")
    print("  - energie")
    secteur = input("Secteur d'activité: ").lower()
    
    return DonneesEntreprise(
        nom=nom,
        symbole=symbole,
        prix_action=prix_action,
        benefice_par_action=benefice_par_action,
        valeur_comptable_par_action=valeur_comptable_par_action,
        revenus_actuels=revenus_actuels,
        revenus_annee_precedente=revenus_annee_precedente,
        dette_totale=dette_totale,
        capitaux_propres=capitaux_propres,
        croissance_benefices_prevue=croissance_benefices_prevue,
        secteur=secteur,
        capitalisation_boursiere=capitalisation_boursiere
    )


def configurer_api_key():
    """
    Permet à l'utilisateur de configurer sa clé API Alpha Vantage
    """
    print("🔑 CONFIGURATION DE LA CLÉ API")
    print("=" * 40)
    print("Pour utiliser l'analyse automatique, vous avez besoin d'une clé API gratuite.")
    print("1. Allez sur: https://www.alphavantage.co/support/#api-key")
    print("2. Inscrivez-vous gratuitement")
    print("3. Copiez votre clé API")
    print()
    print("Note: Vous pouvez utiliser 'demo' pour tester, mais avec des limitations.")
    print()
    
    api_key = input("Entrez votre clé API (ou 'demo' pour tester): ").strip()
    if not api_key:
        api_key = "demo"
    
    return api_key


def exemple_analyse():
    """
    Fonction d'exemple - analyses automatiques et manuelles
    """
    print("🎯 EXEMPLES D'ANALYSES")
    print("=" * 30)
    
    print("\n1️⃣ Exemples d'analyses automatiques (via API):")
    print("=" * 50)
    
    exemples_entreprises = [
        "Apple", "Microsoft", "Google", "Tesla", "Amazon",
        "AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"
    ]
    
    print("Entreprises suggérées pour test:")
    for i, entreprise in enumerate(exemples_entreprises, 1):
        print(f"  {i}. {entreprise}")
    
    print("\n2️⃣ Exemple d'analyse manuelle (données fictives):")
    print("=" * 50)
    
    # Exemple d'entreprise sous-évaluée fictive
    entreprise_sous_evaluee = DonneesEntreprise(
        nom="ValueCorp SA",
        symbole="VCORP",
        prix_action=25.0,
        benefice_par_action=3.50,
        valeur_comptable_par_action=18.0,
        revenus_actuels=1200,
        revenus_annee_precedente=1000,
        dette_totale=300,
        capitaux_propres=800,
        croissance_benefices_prevue=15.0,
        secteur="industrie",
        capitalisation_boursiere=500
    )
    
    analyseur = AnalyseurSousEvaluation()
    analyseur.analyser_entreprise(entreprise_sous_evaluee)


def main():
    """
    Fonction principale du programme
    """
    print("💰 ANALYSEUR DE SOUS-ÉVALUATION D'ENTREPRISES")
    print("=" * 50)
    print("Ce programme vous aide à déterminer si une entreprise")
    print("est sous-évaluée en analysant ses ratios financiers.")
    print()
    print("🚀 NOUVEAU: Analyse automatique via API financière!")
    print("   Tapez juste le nom de l'entreprise et laissez-nous faire le reste.")
    print()
    
    # Variable pour stocker la clé API
    api_key = None
    
    while True:
        print("\nQue souhaitez-vous faire ?")
        print("1. 🤖 Analyser une entreprise automatiquement (via API)")
        print("2. ✏️  Analyser une entreprise manuellement (saisie des données)")
        print("3. 🎯 Voir des exemples d'analyses")
        print("4. 🔑 Configurer/Changer la clé API")
        print("5. ❓ Aide sur l'utilisation des APIs")
        print("6. 🚪 Quitter")
        
        choix = input("\nVotre choix (1-6): ")
        
        if choix == "1":
            # Analyse automatique via API
            if not api_key:
                print("\n🔑 Configuration de la clé API nécessaire:")
                api_key = configurer_api_key()
            
            nom_entreprise = input("\n📝 Entrez le nom de l'entreprise (ou symbole boursier): ").strip()
            if nom_entreprise:
                try:
                    print(f"\n⏳ Analyse en cours de '{nom_entreprise}'...")
                    succes = analyser_entreprise_par_nom(nom_entreprise, api_key)
                    if not succes:
                        print("\n💡 Voulez-vous essayer avec un autre nom ou saisir les données manuellement ?")
                except Exception as e:
                    print(f"❌ Erreur lors de l'analyse automatique: {e}")
                    print("💡 Essayez l'analyse manuelle (option 2)")
            else:
                print("❌ Veuillez entrer un nom d'entreprise.")
        
        elif choix == "2":
            # Analyse manuelle
            try:
                donnees = saisir_donnees_entreprise()
                analyseur = AnalyseurSousEvaluation()
                resultat = analyseur.analyser_entreprise(donnees)
            except ValueError:
                print("❌ Erreur: Veuillez saisir des valeurs numériques valides.")
            except Exception as e:
                print(f"❌ Erreur inattendue: {e}")
        
        elif choix == "3":
            exemple_analyse()
        
        elif choix == "4":
            api_key = configurer_api_key()
            print(f"✅ Clé API configurée: {api_key[:10]}..." if len(api_key) > 10 else f"✅ Clé API configurée: {api_key}")
        
        elif choix == "5":
            print("\n📚 AIDE SUR LES APIS FINANCIÈRES")
            print("=" * 40)
            print("🔹 Alpha Vantage (recommandé):")
            print("   - Gratuit: 5 requêtes/minute, 500/jour")
            print("   - Inscription: https://www.alphavantage.co/support/#api-key")
            print("   - Données: Entreprises mondiales cotées en bourse")
            print()
            print("🔹 Conseils d'utilisation:")
            print("   - Utilisez les symboles boursiers pour plus de précision (ex: AAPL)")
            print("   - Les entreprises non cotées ne sont pas disponibles")
            print("   - Attendez quelques secondes entre les analyses")
            print()
            print("🔹 Symboles boursiers populaires:")
            print("   - Apple: AAPL")
            print("   - Microsoft: MSFT")
            print("   - Google: GOOGL")
            print("   - Tesla: TSLA")
            print("   - Amazon: AMZN")
            print("   - Meta: META")
            print("   - Netflix: NFLX")
        
        elif choix == "6":
            print("\n👋 Merci d'avoir utilisé l'analyseur!")
            print("💡 N'oubliez pas:")
            print("   - Cette analyse est à des fins éducatives")
            print("   - Consultez toujours un conseiller financier")
            print("   - Diversifiez vos investissements")
            print("\nBonne chance avec vos investissements! 📈")
            break
        
        else:
            print("❌ Choix invalide. Veuillez choisir entre 1 et 6.")


if __name__ == "__main__":
    main()
