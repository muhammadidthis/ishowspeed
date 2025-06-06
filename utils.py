import praw
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

def load_posts(filepath='ishowspeed_posts.csv'):
    return pd.read_csv(filepath)

def load_comments(filepath='ishowspeed_comments_sentiment.csv'):
    return pd.read_csv(filepath)

def fetch_and_analyze_sentiment(client_id, client_secret, user_agent, subreddit_name='Ishowspeed', limit=10):
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    sia = SentimentIntensityAnalyzer()
    subreddit = reddit.subreddit(subreddit_name)

    comment_data = []

    for submission in subreddit.top(limit=limit, time_filter='all'):
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            score = sia.polarity_scores(comment.body)['compound']
            label = (
                'positive' if score >= 0.05
                else 'negative' if score <= -0.05
                else 'neutral'
            )
            comment_data.append({
                'comment_id': comment.id,
                'comment_text': comment.body,
                'author': str(comment.author),
                'score': comment.score,
                'post_id': submission.id,
                'timestamp': comment.created_utc,
                'sentiment_score': score,
                'sentiment_label': label
            })

    df = pd.DataFrame(comment_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    return df

