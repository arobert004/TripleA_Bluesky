#########   IMPORTS & SETUPS   ##########

from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import requests
import json
import re
import random
from dateutil import parser
from atproto import Client
import pandas as pd
import numpy as np 
import joblib
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ML / DL Models

from transformers import pipeline

# Emotion model
emotion_model = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)
# Fact or Opinion model
fact_or_opi = pipeline("text-classification", model="lighteternal/fact-or-opinion-xlmr-el")
# Positive or Negative model
pos_or_neg = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
# Bot Detection
bot_detection_model = joblib.load(os.path.join(BASE_DIR, "models", "bot_detector_model.joblib"))



# APP

app = Flask(__name__)
app.secret_key = 'testibou'


#########   BLUESKY API GET DATAS FUNCTIONS   ##########

def extract_post_info(url):
    """Extraire les informations d'un post à partir de l'URL Bluesky"""
    # Format attendu: https://bsky.app/profile/[handle]/post/[id]
    pattern = r'bsky\.app/profile/([^/]+)/post/([a-zA-Z0-9]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def extract_feed_info(url):
    """Extraire les informations d'un feed à partir de l'URL"""
    try:
        # Pattern pour l'URL de feed Bluesky
        pattern = r'https://bsky\.app/profile/([^/]+)/feed/([^/]+)'
        match = re.match(pattern, url)
        
        if match:
            actor, feed_id = match.groups()
            print(actor, feed_id)
            # Initialiser le client
            client = Client()
            client.login(login='aro402@hotmail.fr', password='gamertag')
            
            # Récupérer le DID de l'utilisateur
            did = client.app.bsky.actor.get_profile({'actor': actor}).model_dump()['did']
            
            return {
                'did': did,
                'feed_id': feed_id
            }
    except Exception as e:
        print(f"Erreur lors de l'extraction des informations du feed: {str(e)}")
    return None

def get_post_data(handle, post_id):
    """Récupérer les données d'un post Bluesky"""
    try:
        # Initialiser le client
        client = Client()
        client.login(login='aro402@hotmail.fr', password='gamertag')
        
        # Construire l'URI du post
        uri = f'at://{handle}/app.bsky.feed.post/{post_id}'
        
        # Récupérer le post
        response = client.app.bsky.feed.get_post_thread({'uri': uri})
        thread_data = response.model_dump()
        
        if not thread_data or 'thread' not in thread_data or 'post' not in thread_data['thread']:
            return None
            
        post = thread_data['thread']['post']
        
        # Extraire les images si présentes
        images = []
        try:
            if 'embed' in post and post['embed'] and 'images' in post['embed']:
                for img in post['embed']['images']:
                    images.append({
                        'alt': img.get('alt', ''),
                        'url': img.get('fullsize', img.get('thumb', None))
                    })
        except Exception as e:
            print(f"Erreur lors de l'extraction des images: {str(e)}")
            pass
        
        

        # Obtenir les résultats des modèles
        try:
            
            # Récupérer les 3 émotions les plus probables
            emotion_results = emotion_model(post['record']['text'])[0][:3]
            
            emotion_results = [{
                'label': r['label'],
                'score': round(r['score'] * 100)
            } for r in emotion_results]
            
            
            # Analyse fact/subjectif
            fact_opinion_result = fact_or_opi(post['record']['text'])[0]
            fact_opinion_score = round(fact_opinion_result['score'] * 100)
            fact_opinion_label = "Objectif" if fact_opinion_result['label'] == 'LABEL_1' else "Subjectif"
                
            # Analyse sentiment
            sentiment_result = pos_or_neg(post['record']['text'])[0]
            sentiment_score = round(sentiment_result['score'] * 100)
            sentiment_label = sentiment_result['label'].capitalize()
            
            # Perplexity answer 
            
            perplexity_answer = {'fake_news_prob': 0.85,
                'source1': 'https://www.france24.com/fr/%C3%A9co-tech/20250430-etats-unis-economie-pib-recule-donald-trump-accuse-joe-biden-droits-douane',
                'source2': 'https://www.ofce.sciences-po.fr/blog2024/fr/20250428_CB/',
                'source3': 'https://www.lemonde.fr/economie/article/2025/02/11/donald-trump-va-t-il-saborder-l-economie-americaine_6541097_3234.html'}
                            
            
        except Exception as e:
            # print(f"sentim - Erreur lors de l'analyse des modèles : {str(e)}")
            # Valeurs par défaut en cas d'erreur
            emotion_results = []
            fact_opinion_score = 50
            fact_opinion_label = "Non disponible"
            sentiment_score = 50
            sentiment_label = "Non disponible"

        
        return {
            'author': {
                'handle': post['author']['handle'],
                'display_name': post['author'].get('displayName', post['author']['handle']),
                'avatar': post['author'].get('avatar', None),
            },
            'content': post['record']['text'],
            'created_at': parser.parse(post['indexed_at']).strftime("%d/%m/%Y %H:%M"),
            'images': images,
            
            'analysis': {
                'emotions': emotion_results,
                'fact_opinion': {
                    'score': fact_opinion_score,
                    'label': fact_opinion_label
                },
                'sentiment': {
                    'score': sentiment_score,
                    'label': sentiment_label
                },
                'perplexity' : perplexity_answer
            },
            'likes': post['like_count'],
            'reposts': post['repost_count'],
            'timestamp': parser.parse(post['indexed_at']).strftime("%d/%m/%Y %H:%M")
        }
    except Exception as e:
        print(f"Erreur lors de la récupération du post: {str(e)}")
        return None

def get_feed_data(did, feed_id):
    """Récupérer les données d'un feed Bluesky"""
    try:
        # print(f"Tentative de récupération du feed pour {did}/{feed_id}")
        # Initialiser le client
        client = Client()
        client.login(login='aro402@hotmail.fr', password='gamertag')
        
        # Récupérer les posts du feed
        feed_uri = f"at://{did}/app.bsky.feed.generator/{feed_id}"
        feed = client.app.bsky.feed.get_feed({"feed": feed_uri, "limit": 10})
        feed_data = feed.model_dump()
        
        if not feed_data or 'feed' not in feed_data:
            print("Aucun post trouvé dans le feed")
            return None

        posts_data = []
        total_fake_news_prob = 0
        total_sentiment = 0
        total_controversy = 0
        total_reliability = 0

        for item in feed_data['feed']:
            post = item['post']
            print(f"Traitement du post: {post['record']['text'][:100]}...")
            
            # Générer des scores aléatoires pour chaque post
            fake_news_prob = random.uniform(0, 100)
            sentiment = random.uniform(-1, 1)
            controversy = random.uniform(0, 100)
            reliability = random.uniform(0, 100)

            # Accumuler pour les moyennes
            total_fake_news_prob += fake_news_prob
            total_sentiment += sentiment
            total_controversy += controversy
            total_reliability += reliability

            # Extraire les images si présentes
            images = []
            try:
                if 'embed' in post and post['embed'] and 'images' in post['embed']:
                    for img in post['embed']['images']:
                        images.append({
                            'alt': img.get('alt', ''),
                            'url': img.get('fullsize', img.get('thumb', None))
                        })
            except Exception as e:
                print(f"Erreur lors de l'extraction des images: {str(e)}")
                pass

            # Formater les données du post
            post_data = {
                'author': {
                    'handle': post['author']['handle'],
                    'display_name': post['author'].get('displayName', post['author']['handle']),
                    'avatar': post['author'].get('avatar', None),
                },
                'content': post['record']['text'],
                'created_at': parser.parse(post['indexed_at']).strftime("%d/%m/%Y %H:%M"),
                'images': images,
                'stats': {
                    'fake_news_probability': round(fake_news_prob, 1),
                    'sentiment_score': round(sentiment, 2),
                    'controversy_index': round(controversy, 1),
                    'reliability_score': round(reliability, 1)
                }
            }
            posts_data.append(post_data)

        # Calculer les moyennes pour le feed entier
        num_posts = len(posts_data)
        feed_stats = {
            'fake_news_probability': round(total_fake_news_prob / num_posts, 1),
            'sentiment_score': round(total_sentiment / num_posts, 2),
            'controversy_index': round(total_controversy / num_posts, 1),
            'reliability_score': round(total_reliability / num_posts, 1)
        }

        # Récupérer les informations du feed
        feed_info = client.app.bsky.feed.get_feed_generator({'feed': feed_uri}).model_dump()
        
        return {
            'feed_info': {
                'name': feed_info['view'].get('displayName', 'Feed Bluesky'),
                'description': feed_info['view'].get('description', 'Un feed Bluesky'),
                'avatar': feed_info['view'].get('avatar', None),
            },
            'stats': feed_stats,
            'posts': posts_data
        }

    except Exception as e:
        print(f"Erreur lors de la récupération du feed: {str(e)}")
        return None


def get_tag_datas(user_tag) :
    ''' Récupérer les informations liés à un tag'''
    try:
        client = Client()
        client.login(login='aro402@hotmail.fr', password='gamertag')

        searchresult = client.app.bsky.feed.search_posts({'q' : user_tag,
                                                        'sort' : 'top',
                                                        'limit' : 50})

        # 'Pas de posts sur ce tag' ? 
        if searchresult.model_dump()['posts'] == [] : 
             
            return False 
            
        posts_data = []

        
        total_emotion = {}
        total_fact_opinion = {"Objectif" : 0,
                              "Subjectif" : 0}
        total_sentiment_model = {"Positive" : 0,
                                 "Neutral" : 0,
                                 "Negative" : 0}
        total_gram_mistakes = 0
        

        for item in searchresult.model_dump()['posts']:

            post = item

            # Récupérer l'emotion la plus probable
            emotion_results = emotion_model(post['record']['text'])[0][:1]
            
            emotion_results = [{
                'label': r['label'],
                'score': round(r['score'] * 100)
            } for r in emotion_results][0]
            
            # Analyse fact/subjectif
            fact_opinion_result = fact_or_opi(post['record']['text'])[0]
            fact_opinion_score = round(fact_opinion_result['score'] * 100)
            fact_opinion_label = "Objectif" if fact_opinion_result['label'] == 'LABEL_1' else "Subjectif"
            
            # Analyse sentiment
            sentiment_result = pos_or_neg(post['record']['text'])[0]
            sentiment_score = round(sentiment_result['score'] * 100)
            sentiment_label = sentiment_result['label'].capitalize()
            
            # Gramm mistake - RALENTI TROP LE PROCESS 
            # language = post['record']['langs']
            # if language == None : 
            #     language = 'en'
            # gram_mistakes = count_spelling_errors(post['record']['text'][:20], language)
            # total_gram_mistakes += gram_mistakes


            
            # Stockage pour scores globaux
            
            #EMOTION
            if emotion_results['label'] not in total_emotion.keys() :
                
                total_emotion[emotion_results['label']] = 0
                total_emotion[emotion_results['label']] += 1
                
            else : 
                
                total_emotion[emotion_results['label']] += 1

            #FACTOPI
            total_fact_opinion[fact_opinion_label] += 1 
            
            #SENTIMENT
            total_sentiment_model[sentiment_label] += 1 

            # Extraire les images si présentes
            images = []
            try:
                if 'embed' in post and post['embed'] and 'images' in post['embed']:
                    for img in post['embed']['images']:
                        images.append({
                            'alt': img.get('alt', ''),
                            'url': img.get('fullsize', img.get('thumb', None))
                        })
            except Exception as e:
                print(f"Erreur lors de l'extraction des images: {str(e)}")
                pass

            # Formater les données du post
            post_data = {
                'author': {
                    'handle': post['author']['handle'],
                    'display_name': post['author'].get('displayName', post['author']['handle']),
                    'avatar': post['author'].get('avatar', None),
                },
                'content': post['record']['text'],
                'created_at': parser.parse(post['indexed_at']).strftime("%d/%m/%Y %H:%M"),
                'images': images,
                'stats': {
                    'emotions': emotion_results,
                    'fact_opinion': {
                        'score': fact_opinion_score,
                        'label': fact_opinion_label
                                },
                    'sentiment': {
                        'score': sentiment_score,
                        'label': sentiment_label
                    }
                }
            }
            posts_data.append(post_data)

        # Calculer les moyennes pour le feed entier
        num_posts = len(posts_data)
        allposts_tags_stats = {
            'emotion_total' : sorted(total_emotion.items(), key=lambda x: x[1], reverse=True)[:3],
            'fact_opi_total' : total_fact_opinion,
            'total_sentiment_model' : total_sentiment_model
        }
        
        return {
            'tag_info': {
                'name': user_tag,
                'description': f'Analyse pour le tag : {user_tag}',
                'avatar': ''
            },
            'stats': allposts_tags_stats,
            'posts': posts_data
        }
        
    except Exception as e:
        
        print(f"Erreur lors de l'extraction des images: {str(e)}")
        pass
    
def extract_user_features(handle):
    
    # Client
    client = Client()
    client.login(login='aro402@hotmail.fr', password='gamertag')
    
    
    # récupération des infos relatives au profil & feed
    profile = client.app.bsky.actor.get_profile({'actor': handle})
    feed = client.app.bsky.feed.get_author_feed({'actor': handle, 'limit': 100})

    # marqueur temporel pour calculer l'ancienneté du compte
    now = datetime.datetime.now(datetime.timezone.utc)
    created_at = profile['created_at']
    created_at = datetime.datetime.fromisoformat(created_at)

    # initialisation des variables à incrémenter 
    posts = feed['feed']
    timestamps = []
    link_count = 0
    reply_count = 0
    repost_count = 0

    # récupération des infos des 100 derniers posts
    
    for item in posts:
        post = item['post']
        record = post['record']

        if not record:
            continue

        timestamp = datetime.datetime.fromisoformat(record['created_at'])
        timestamps.append(timestamp)

        text = getattr(record, 'text', '')
        if 'http://' in text or 'https://' in text:
            link_count += 1

        if record.reply:
            reply_count += 1

        if item.reason and getattr(item.reason, '$type', '') == 'app.bsky.feed.defs#reasonRepost':
            repost_count += 1
            
    # 
    timestamps_sorted = sorted(timestamps)
    intervals = np.diff([ts.timestamp() for ts in timestamps_sorted])
    std_hours = np.std([ts.hour for ts in timestamps_sorted]) if timestamps else 0

    # création des features pour établir un score de fiabilité du compte
    
    if profile['follows_count'] == 0 :
        follows_count = profile['follows_count'] + 1
    else : 
        follows_count = profile['follows_count'] 
 
    features = {
        'posts_per_day': profile['posts_count'] / max((now - created_at).days, 1),
        'follower_following_ratio': profile['followers_count'] / follows_count,
        'account_age_days': (now - created_at).days,
        'link_ratio': link_count / max(len(timestamps), 1),
        'reply_ratio': reply_count / max(len(timestamps), 1),
        'repost_ratio': repost_count / max(len(timestamps), 1)
    }

    return features   

    
def predict_bot_score(handle):
    
    # Client
    client = Client()
    client.login(login='aro402@hotmail.fr', password='gamertag')
    
    try:
        profile = client.app.bsky.actor.get_profile({'actor': handle})
    except Exception as e:
        print(f"Erreur lors de la récupération du profil : {e}")


    # Vérification du statut de vérification
    verification = getattr(profile, 'verification', None)
    verified_raw = getattr(verification, 'verified_status', False) if verification else False
    is_verified = str(verified_raw).lower() == 'true'

    # Extraire les features
    features = extract_user_features(handle)

    if is_verified:
        print("Compte vérifié")
        score = 0.0
    else:
        df = pd.DataFrame([features])
        score = bot_detection_model.predict_proba(df)[0][1]
        
    avatar = profile.model_dump()['avatar']
    display_name = profile.model_dump()["display_name"]
    followers_count = profile.model_dump()["followers_count"]
    follows_count = profile.model_dump()["follows_count"]
    posts_count = profile.model_dump()["posts_count"]

    # Renvoyer toutes les infos dans un dictionnaire
    result = {
        'handle': handle,
        'display_name' : display_name,
        'avatar' : avatar,
        'followers_counts' : followers_count, 
        "follows_count" : follows_count,
        "posts_count" : posts_count,
        'is_verified': is_verified,
        'bot_risk_score': score,
        'features': features
    }

    return result


#########   PAGES LOGIC   ##########


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    post_url = request.form.get('post_url')
    
    if not post_url:
        return redirect(url_for('index'))
        
    # Vérifier si c'est une URL de feed
    feed_info = extract_feed_info(post_url)
    if feed_info:
        feed_data = get_feed_data(feed_info['did'], feed_info['feed_id'])
        if feed_data:
            return render_template('feed_analysis.html', feed=feed_data)
        return redirect(url_for('index'))
            
    # Si ce n'est pas un feed, traiter comme un post normal
    post_info = extract_post_info(post_url)
    if post_info:
        post_data = get_post_data(post_info[0], post_info[1])
        if post_data:
            return render_template('analysis.html', post=post_data)
        
    return redirect(url_for('index'))


@app.route('/tags_analysis', methods=['POST'])
def tag_analyze():
   
    input_tag_user = request.form.get('post_tag')
    post_data = get_tag_datas(input_tag_user)
    
    return render_template('tags_analysis.html', tag = post_data)


@app.route('/account_analysis/<handle>')
def account_analysis(handle):
    
    result = predict_bot_score(handle=handle)
    
    return render_template('account_analysis.html', handle=handle, result=result)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

