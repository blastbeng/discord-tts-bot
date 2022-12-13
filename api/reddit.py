import os
import sys
import logging
from dotenv import load_dotenv
from os.path import dirname
from os.path import join
from pathlib import Path
from datetime import datetime

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_KEY = os.environ.get("REDDIT_API_KEY")
API_SECRET = os.environ.get("REDDIT_API_SECRET")
SUBREDDITS = os.environ.get("SUBREDDITS").split(",")

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger('werkzeug')
log.setLevel(int(os.environ.get("LOG_LEVEL")))

class Post():
  def __init__(self, text, content, content_type):
      self.text = text
      self.content = content
      self.content_type = content_type

reddit = praw.Reddit(
    client_id=API_KEY,
    client_secret=API_SECRET,
    user_agent="Udoo_docker_instance",
)

def search(words: str):
    try:
        for submission in reddit.subreddit("all").search(words):
            logging.info("%s", submission.title)
    except Esception as error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    return Post("TODO", "TODO", "TODO")