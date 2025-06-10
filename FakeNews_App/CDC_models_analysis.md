Nous allons changer les scores aléatoires de la page analysis.html. 

J'ai rajouté et pull beaucoup de changement. Prends en connaissance.

3 modeles sont ajoutés dans app.py, avec leurs résultats par rapport au post (ligne 102+) : 

        - result_emotion_model = emotion_model(post['record']['text'])[0][:3]

        ==> Retourne par exemple :
            [{'label': 'admiration', 'score': 0.6758760213851929},
            {'label': 'neutral', 'score': 0.30907952785491943},
            {'label': 'approval', 'score': 0.0780540257692337}]

        - result_fact_or_opi = fact_or_opi(post['record']['text'])

        ==> Retourne LABEL 0 = Opinion / subjectif. Label 1 = Factuel / objectif: 
            [{'label': 'LABEL_0', 'score': 0.9971644282341003}]

        - result_pos_or_neg = pos_or_neg(post['record']['text'])
        
        ==> Retourne positive, negative ou neutre: exemple :
        [{'label': 'positive', 'score': 0.9484643936157227}]


Ton cahier des charges :

- Changer le analysis.html pour accueillir ses nouvelles métriques.

- En dessous du résumé du postes (texte, image etc ...) je veux que tu insères 4 sections :
        1) Section Fake News : Pour l'instant vide, nous insérerons autre chose plus tard.
        2) Analyse de l'objectivité du tweet avec le modele "fact_or_opi"
            FORME : Jauge ou équivalent
        3) Analyse de sentiments, avec le modèle "emotion_model". On doit pouvoir voir explicitement chaque label de ce top 3 et leur score (arrondi, sans chiffre apres la virgule). 
            FORME : Graphique bar
        4) Analyse du ton, avec le modele "pos_or_neg".
            FORME : Jauge ou équivalent

    La section 1) Fake News au dessus, les trois autres en dessous, équitablement réparti dans l'espace.