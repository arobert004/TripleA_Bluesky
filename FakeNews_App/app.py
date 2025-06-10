#########   IMPORTS & SETUPS   ##########

from flask import Flask, render_template, request, redirect, url_for
import re
import random
from dateutil import parser
from atproto import Client

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
        
        
        ###### INSERT ANALYZE MODEL HERE ######
        # Générer des scores aléatoires 
        fake_news_prob = random.uniform(0, 100)
        sentiment = random.uniform(-1, 1)
        controversy = random.uniform(0, 1)
        reliability = random.uniform(0, 100)
        
        return {
            'author': {
                'handle': post['author']['handle'],
                'display_name': post['author'].get('displayName', post['author']['handle']),
                'avatar': post['author'].get('avatar', None),
            },
            'content': post['record']['text'],
            'created_at': parser.parse(post['indexed_at']).strftime("%d/%m/%Y %H:%M"),
            'images': images,
            
            ###### INSERT RESULT OF THE ANALYZE MODEL HERE ######
            'metrics': {
                'fake_news_probability': round(fake_news_prob, 1),
                'sentiment_score': round(sentiment, 2),
                'controversy_index': round(controversy, 1),
                'reliability_score': round(reliability, 1)
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
                                                        'sort' : 'top'})

        # 'Pas de posts sur ce tag' ? 
        if searchresult.model_dump()['posts'] == [] : 
             
            return False 
            
        posts_data = []
        total_fake_news_prob = 0
        total_sentiment = 0
        total_controversy = 0
        total_reliability = 0

        for item in searchresult.model_dump()['posts']:
            post = item
            # print(f"Traitement du post: {post['record']['text'][:100]}...")
            
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
        allposts_tags_stats = {
            'fake_news_probability': round(total_fake_news_prob / num_posts, 1),
            'sentiment_score': round(total_sentiment / num_posts, 2),
            'controversy_index': round(total_controversy / num_posts, 1),
            'reliability_score': round(total_reliability / num_posts, 1)
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


@app.route('/account_analysis')
def account_analysis():
    return render_template('account_analysis.html')

if __name__ == '__main__':
    app.run(debug=True)
