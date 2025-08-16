# 💰 Analyseur de Sous-évaluation d'Entreprises

## 🎯 Description

Ce programme analyse automatiquement si une entreprise est sous-évaluée en calculant et comparant plusieurs ratios financiers importants. **Maintenant avec récupération automatique des données via API !**

## 🚀 Nouvelles fonctionnalités

- **Analyse automatique** : Tapez juste le nom de l'entreprise !
- **API Alpha Vantage** : Données financières en temps réel
- **Analyses mondiales** : Toutes les entreprises cotées en bourse
- **Interface améliorée** : Plus intuitive et guidée

## 📊 Ratios analysés

1. **P/E Ratio** - Prix/Bénéfices
2. **P/B Ratio** - Prix/Valeur comptable  
3. **PEG Ratio** - (P/E)/Croissance
4. **Croissance des revenus**
5. **Ratio d'endettement**

## 🛠️ Installation

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer le programme
python3 placement.py
```

## 🔑 Configuration API (Gratuite)

1. Allez sur : https://www.alphavantage.co/support/#api-key
2. Inscrivez-vous gratuitement (limite : 5 requêtes/minute, 500/jour)
3. Copiez votre clé API
4. Utilisez l'option 4 dans le menu pour la configurer

**Pour tester rapidement :** Utilisez 'demo' comme clé API (limité mais fonctionnel)

## 📝 Utilisation

### Analyse automatique (Recommandée)
```
1. Lancez le programme
2. Choisissez l'option 1 (Analyse automatique)
3. Entrez le nom de l'entreprise ou son symbole boursier
4. Laissez la magie opérer ! ✨
```

### Exemples d'entreprises à tester
- **Par nom** : Apple, Microsoft, Google, Tesla, Amazon
- **Par symbole** : AAPL, MSFT, GOOGL, TSLA, AMZN

### Analyse manuelle
Si l'API ne trouve pas votre entreprise, vous pouvez toujours saisir les données manuellement.

## 📈 Interprétation des résultats

- **Score ≥ 75** : 🚀 Fortement sous-évaluée → Achat recommandé
- **Score 60-74** : ✅ Sous-évaluée → Bon potentiel
- **Score 40-59** : ⚖️ Valorisation équitable → Analyser davantage
- **Score < 40** : ⚠️ Possiblement surévaluée → Éviter

## ⚠️ Avertissement

**Ce programme est à des fins éducatives uniquement.**
- Consultez toujours un conseiller financier professionnel
- Diversifiez vos investissements
- Les données passées ne garantissent pas les performances futures

## 🐛 Dépannage

### L'entreprise n'est pas trouvée ?
- Vérifiez l'orthographe
- Essayez avec le symbole boursier (ex: AAPL pour Apple)
- Assurez-vous que l'entreprise est cotée en bourse
- Utilisez l'analyse manuelle en dernier recours

### Erreur API ?
- Vérifiez votre clé API
- Vous avez peut-être atteint la limite de requêtes
- Attendez une minute et réessayez

## 🔧 Structure du code

- `RecuperateurDonneesAPI` : Gère les appels à l'API Alpha Vantage
- `AnalyseurSousEvaluation` : Calcule les ratios et scores
- `DonneesEntreprise` : Structure des données financières
- Interface utilisateur interactive et guidée

## 📚 APIs utilisées

- **Alpha Vantage** : API financière principale (gratuite)
- **Alternative** : Code adaptable pour d'autres APIs

---

**Créé avec ❤️ pour l'analyse financière**
# analyse-entreprise
