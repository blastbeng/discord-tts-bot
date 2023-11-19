

import os
import logging
import image
import utils
import insults
import audiodb
import threading
import sys
import glob
from io import BytesIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask, request, send_file, Response, jsonify, make_response, after_this_request, g
from flask_restx import Api, Resource, reqparse
from flask_apscheduler import APScheduler
from flask_caching import Cache
from os.path import join, dirname
from dotenv import load_dotenv
from threading import Thread
from bestemmie import Bestemmie
from libretranslator import LibreTranslator
from exceptions import AudioLimitException
from time import strftime
from utils import SentenceToLearn

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger('werkzeug')
log.setLevel(int(os.environ.get("LOG_LEVEL")))

TMP_DIR = os.environ.get("TMP_DIR")
ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_PASS = os.environ.get("ADMIN_PASS")
API_USER = os.environ.get("API_USER")
API_PASS = os.environ.get("API_PASS")

app = Flask(__name__)
class Config:    
    CACHE_TYPE = os.environ['CACHE_TYPE']
    CACHE_REDIS_HOST = os.environ['CACHE_REDIS_HOST']
    CACHE_REDIS_PORT = os.environ['CACHE_REDIS_PORT']
    CACHE_REDIS_DB = os.environ['CACHE_REDIS_DB']
    CACHE_REDIS_URL = os.environ['CACHE_REDIS_URL']
    CACHE_DEFAULT_TIMEOUT = os.environ['CACHE_DEFAULT_TIMEOUT']
    SCHEDULER_API_ENABLED = True

scheduler = APScheduler()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
    storage_uri="memory://",
)

app.config.from_object(Config())

    
@app.after_request
def after_request(response):
  if not request.path.startswith('/utils/healthcheck'):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logging.info('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
  #if request.path.startswith('/chatbot_audio/repeat/learn/'):
  #  request_args = {**request.view_args, **request.args} if request.view_args else {**request.args}
  #  if "text" in request_args and "chatid" in request_args "lang" in request_args:
  #    text = request.view_args['text']
  #    chatbot = get_chatbot_by_id(chatid=request.view_args['chatid'], lang=request.view_args['lang'])
  #    daemon = Thread(target=chatbot.get_response, args=(text,), daemon=True, name="repeat-learn"+utils.get_random_string(24))
  #    daemon.start()
  return response

cache = Cache(app)
api = Api(app)

nstext = api.namespace('chatbot_text', 'Accumulators Chatbot Text APIs')

parserinsult = reqparse.RequestParser()
parserinsult.add_argument("lang", type=str)
parserinsult.add_argument("text", type=str)
parserinsult.add_argument("chatid", type=str)

def get_response_str(text: str):
  r = Response(response=text, status=200, mimetype="text/xml")
  r.headers["Content-Type"] = "text/xml; charset=utf-8"
  return r

def get_response_json(data):
  r = Response(response=data, status=200, mimetype="application/json")
  r.headers["Content-Type"] = "application/json; charset=utf-8"
  return r

def get_response_limit_error(text: str):
  r = make_response("TTS Limit Exceeded", 400)
  r.headers['X-Generated-Text'] = text.encode('utf-8').decode('latin-1')
  return r

def get_response_filters_error(text: str):
  r = make_response("This sentence contains a word that is blocked by filters", 406)
  r.headers['X-Generated-Text'] = text.encode('utf-8').decode('latin-1')
  return r


@nstext.route('/repeat/<string:text>/')
@nstext.route('/repeat/<string:text>/<string:chatid>')
class TextRepeatClass(Resource):
  @cache.cached(timeout=7200, query_string=True)
  def get (self, text: str, chatid = "000000"):
    return get_response_str(text)


@nstext.route('/curse/')
@nstext.route('/curse/<string:chatid>/')
@nstext.route('/curse/<string:chatid>/<string:lang>')
class TextCurseClass(Resource):
  @cache.cached(timeout=1, query_string=True)
  def get (self, chatid = "000000", lang="it"):
    cursez = Bestemmie().random().lower()
    if lang == "it":
      return get_response_str(cursez)
    else:
      return get_response_str(LibreTranslator(from_lang="it", to_lang=lang, base_url=os.environ.get("TRANSLATOR_BASEURL")).translate(cursez))


@limiter.limit("1/second")
@nstext.route('/random/')
@nstext.route('/random/<string:chatid>/')
@nstext.route('/random/<string:chatid>/<string:text>')
class TextRandomClass(Resource):
  def get (self, chatid = "000000", text = None):
    sentence = utils.get_random_from_bot(chatid, text)
    if sentence is not None:
      return get_response_str(sentence)
    else:
      response = make_response("Text not found", 204)
      response.headers['X-Generated-Text'] = text.encode('utf-8').decode('latin-1')
      return response

@nstext.route('/repeat/learn/<string:text>/')
@nstext.route('/repeat/learn/<string:text>/<string:chatid>/')
@nstext.route('/repeat/learn/<string:text>/<string:chatid>/<string:lang>')
class TextRepeatLearnClass(Resource):
  @cache.cached(timeout=7200, query_string=True)
  def get (self, text: str, chatid = "000000", lang = "it"):
    response = get_response_str(text)
    chatbot = get_chatbot_by_id(chatid=chatid, lang=lang)
    daemon = Thread(target=chatbot.get_response, args=(text,), daemon=True, name="repeat-learn"+utils.get_random_string(24))
    daemon.start()
    return response


@nstext.route('/repeat/learn/user/<string:user>/<string:text>/')
@nstext.route('/repeat/learn/user/<string:user>/<string:text>/<string:chatid>/')
@nstext.route('/repeat/learn/user/<string:user>/<string:text>/<string:chatid>/<string:lang>')
class AudioRepeatLearnUserClass(Resource):
  @cache.cached(timeout=7200, query_string=True)
  def get (self, user: str, text: str, chatid = "000000", lang = "it"):
    chatbot = get_chatbot_by_id(chatid=chatid, lang=lang)
    daemon = Thread(target=chatbot.get_response, args=(text,), daemon=True, name="repeat-learn-user"+utils.get_random_string(24))
    daemon.start()

    audiodb.insert_or_update(text.strip(), chatid, None, "google", lang, is_correct=1, user=user)

    return get_response_str(text)


@nstext.route('/ask/<string:text>/')
@nstext.route('/ask/<string:text>/<string:chatid>/')
@nstext.route('/ask/<string:text>/<string:chatid>/<string:lang>')
class TextAskClass(Resource):
  @cache.cached(timeout=10, query_string=True)
  def get (self, text: str, chatid = "000000", lang = "it"):
    chatbot_response = get_chatbot_by_id(chatid=chatid, lang=lang).get_response(text).text
    return get_response_str(chatbot_response)


@nstext.route('/ask/nolearn/<string:text>/')
@nstext.route('/ask/nolearn/<string:text>/<string:chatid>/')
@nstext.route('/ask/nolearn/<string:text>/<string:chatid>/<string:lang>')
class TextAskNoLearnClass(Resource):
  def get (self, text: str, chatid = "000000", lang = "it"):
    chatbot_response = get_chatbot_by_id(chatid=chatid, lang=lang).get_response(text, learn=False).text
    return get_response_str(chatbot_response)


@nstext.route('/ask/user/<string:user>/<string:text>/')
@nstext.route('/ask/user/<string:user>/<string:text>/<string:chatid>/')
@nstext.route('/ask/user/<string:user>/<string:text>/<string:chatid>/<string:lang>')
class TextAskUserClass(Resource):
  @cache.cached(timeout=10, query_string=True)
  def get (self, user: str, text: str, chatid = "000000", lang = "it"):
    chatbot_response = get_chatbot_by_id(chatid=chatid, lang=lang).get_response(text, learn=True).text
    audiodb.insert_or_update(text.strip(), chatid, None, "google", lang, is_correct=1, user=user)

    return get_response_str(chatbot_response)


@nstext.route('/search/<string:text>/')
@nstext.route('/search/<string:text>/<string:chatid>/')
@nstext.route('/search/<string:text>/<string:chatid>/<string:lang>')
class TextSearchClass(Resource):
  @cache.cached(timeout=7200, query_string=True)
  def get (self, text: str, chatid = "000000", lang = "it"):
    wikisaid = utils.wiki_summary(text,lang)
    if wikisaid is None:
      wikisaid = LibreTranslator(from_lang="it", to_lang=lang, base_url=os.environ.get("TRANSLATOR_BASEURL")).translate("Non ho trovato nessun risultato per") + ': "' + text +'"'
    return get_response_str(wikisaid)


@nstext.route('/learn/<string:text>/<string:response>/')
@nstext.route('/learn/<string:text>/<string:response>/<string:chatid>/')
@nstext.route('/learn/<string:text>/<string:response>/<string:chatid>/<string:lang>')
class TextLearnClass(Resource):
  @cache.cached(timeout=10, query_string=True)
  def get (self, text: str, response: str, chatid = "000000", lang = "it"):
    utils.learn(text, response, get_chatbot_by_id(chatid=chatid, lang=lang))
    return "Ho imparato: " + text + " => " + response



@nstext.route('/translate/<string:from_lang>/<string:to_lang>/<string:text>/')
@nstext.route('/translate/<string:from_lang>/<string:to_lang>/<string:text>/<string:chatid>')
class TextTranslateClass(Resource):
  @cache.cached(timeout=7200, query_string=True)
  def get (self, from_lang: str, to_lang: str, text: str, chatid = "000000"):
    try:
      text_out = LibreTranslator(from_lang=from_lang, to_lang=to_lang, base_url=os.environ.get("TRANSLATOR_BASEURL")).translate(text)
      if text_out is not None:
        response = get_response_str(text_out)
        response.headers['X-Generated-Text'] = text_out.encode('utf-8').decode('latin-1')
        return response
      else:
        @after_this_request
        def clear_cache(response):
          cache.delete_memoized(TextTranslateClass.get, self, str, str, str)
          return make_response("Translate Error!", 500)
    except Exception as e:
      g.request_error = str(e)
      @after_this_request
      def clear_cache(response):
        cache.delete_memoized(TextTranslateClass.get, self, str, str, str)
        return make_response(g.get('request_error'), 500)


@nstext.route('/insult')
class TextInsultClass(Resource):
  @api.expect(parserinsult)
  def get (self):

    sentence = insults.get_insults()

    lang = request.args.get("lang")
    if lang is None:
      lang = "it"  

    if lang != "it":
      sentence = LibreTranslator(from_lang="it", to_lang=lang, base_url=os.environ.get("TRANSLATOR_BASEURL")).translate(sentence)

    chatid = request.args.get("chatid")
    if chatid is None:
      chatid = "000000"

    text = request.args.get("text")
    if text and text != '' and text != 'none':
      sentence = text + " " + sentence
    if chatid == "000000":
      chatbot = get_chatbot_by_id(chatid=chatid, lang=lang)
      threading.Thread(target=lambda: chatbot.get_response(sentence)).start()
    response = Response(sentence)
    return response


nsimage = api.namespace('image', 'Accumulators Image APIs')


@nsimage.route('/generate/bytext/<string:text>/')
@nsimage.route('/generate/bytext/<string:text>/<string:chatid>')
class ImageGenerateByText(Resource):
  @cache.cached(timeout=7200, query_string=True)
  def get (self, text: str, chatid = "000000"):
    try:
      image = utils.generate_image(text)
      if image is not None:
        return send_file(image, attachment_filename='image.png', mimetype='image/png')
      else:
        @after_this_request
        def clear_cache(response):
          cache.delete_memoized(ImageGenerateByText.get, self, str, str, str)
          return make_response("Generation Error!", 500)
    except Exception as e:
      g.request_error = str(e)
      @after_this_request
      def clear_cache(response):
        cache.delete_memoized(ImageGenerateByText.get, self, str, str, str)
        return make_response(g.get('request_error'), 500)


nsaudio = api.namespace('chatbot_audio', 'Accumulators Chatbot TTS audio APIs')


@nsaudio.route('/repeat/<string:text>/<string:voice>/')
@nsaudio.route('/repeat/<string:text>/<string:voice>/<string:chatid>')
@nsaudio.route('/repeat/<string:text>/<string:voice>/<string:chatid>/<string:language>')
class AudioRepeatClass(Resource):
  @cache.cached(timeout=7200, query_string=True)
  def get (self, text: str, voice: str, chatid = "000000", language = "it"):
    try:
      tts_out = utils.get_tts(text, chatid=chatid, voice=voice, language=language, limit=False, save=False)
      if tts_out is not None:
        response = send_file(tts_out, attachment_filename='audio.mp3', mimetype='audio/mpeg')
        response.headers['X-Generated-Text'] = text.encode('utf-8').decode('latin-1')
        return response
      else:
        @after_this_request
        def clear_cache(response):
          cache.delete_memoized(AudioRepeatClass.get, self, str, str, str)
          return make_response("TTS Generation Error!", 500)
    except Exception as e:
      g.request_error = str(e)
      @after_this_request
      def clear_cache(response):
        cache.delete_memoized(AudioRepeatClass.get, self, str, str, str)
        return make_response(g.get('request_error'), 500)



@nsaudio.route('/repeat/save/<string:text>/<string:voice>/')
@nsaudio.route('/repeat/save/<string:text>/<string:voice>/<string:chatid>')
@nsaudio.route('/repeat/save/<string:text>/<string:voice>/<string:chatid>/<string:language>')
class AudioSaveRepeatClass(Resource):
  @cache.cached(timeout=7200, query_string=True)
  def get (self, text: str, voice: str, chatid = "000000", language = "it"):
    try:
      tts_out = utils.get_tts(text, chatid=chatid, voice=voice, language=language, save=True)
      if tts_out is not None:
        response = send_file(tts_out, attachment_filename='audio.mp3', mimetype='audio/mpeg')
        response.headers['X-Generated-Text'] = text.encode('utf-8').decode('latin-1')
        return response
      else:
        @after_this_request
        def clear_cache(response):
          cache.delete_memoized(AudioSaveRepeatClass.get, self, str, str, str)
          return make_response("TTS Generation Error!", 500)
    except AudioLimitException:
      return get_response_limit_error(text)
    except Exception as e:
      g.request_error = str(e)
      @after_this_request
      def clear_cache(response):
        cache.delete_memoized(AudioSaveRepeatClass.get, self, str, str, str)
        return make_response(g.get('request_error'), 500)


@nsaudio.route('/curse/<string:voice>/')
@nsaudio.route('/curse/<string:voice>/<string:chatid>/')
@nsaudio.route('/curse/<string:voice>/<string:chatid>/<string:lang>')
class AudioCurseClass(Resource):
  @cache.cached(timeout=1, query_string=True)
  def get (self, voice = "google", chatid = "000000", lang = "it"):
    cursez = ""
    try:
      cursez = Bestemmie().random().lower()
      if lang != "it":
        cursez = LibreTranslator(from_lang="it", to_lang=lang, base_url=os.environ.get("TRANSLATOR_BASEURL")).translate(cursez)
      tts_out = utils.get_tts(cursez, chatid=chatid, voice=voice, language=lang, save=False, call_fy=False, limit=False)
      if tts_out is not None:
        response = send_file(tts_out, attachment_filename='audio.mp3', mimetype='audio/mpeg')
        response.headers['X-Generated-Text'] = cursez.encode('utf-8').decode('latin-1')
        return response
      else:
        @after_this_request
        def clear_cache(response):
          cache.delete_memoized(AudioCurseClass.get, self, str, str, str)
          return make_response("TTS Generation Error!", 500)
    except AudioLimitException:
      return get_response_limit_error(cursez)
    except Exception as e:
      g.request_error = str(e)
      @after_this_request
      def clear_cache(response):
        cache.delete_memoized(AudioCurseClass.get, self, str, str, str)
        return make_response(g.get('request_error'), 500)

@limiter.limit("1/second")
@nsaudio.route('/random/')
@nsaudio.route('/random/<string:voice>/')
@nsaudio.route('/random/<string:voice>/<string:chatid>/')
@nsaudio.route('/random/<string:voice>/<string:chatid>/<string:lang>/')
@nsaudio.route('/random/<string:voice>/<string:chatid>/<string:lang>/<string:text>')
class AudioRandomClass(Resource):
  def get (self, voice = "random", chatid = "000000", lang = "it", text = None):
    try:
      tts_out, text_response = audiodb.select_by_chatid_voice_language_random(chatid,voice,lang,text)
      if not text_response:
          text = "Audio not found"
          response = make_response(text, 204)
          response.headers['X-Generated-Text'] = text.encode('utf-8').decode('latin-1')
          return response
      elif tts_out is not None:
        response = send_file(tts_out, attachment_filename='audio.mp3', mimetype='audio/mpeg')
        response.headers['X-Generated-Text'] = text_response.encode('utf-8').decode('latin-1')
        return response
      if tts_out is None:
        return make_response("TTS Generation Error!", 500)
    except Exception as e:
      return make_response(g.get('request_error'), 500)
      

@nsaudio.route('/repeat/learn/<string:text>/<string:voice>/')
@nsaudio.route('/repeat/learn/<string:text>/<string:voice>/<string:chatid>/')
@nsaudio.route('/repeat/learn/<string:text>/<string:voice>/<string:chatid>/<string:lang>/')
@nsaudio.route('/repeat/learn/<string:text>/<string:voice>/<string:chatid>/<string:lang>/<string:filename>')
class AudioRepeatLearnClass(Resource):
  @cache.cached(timeout=7200, query_string=True)
  def get (self, text: str, voice: str, chatid = "000000", lang = "it", filename = "audio.mp3"):
    try:
      tts_out = utils.get_tts(text, chatid=chatid, voice=voice, language=lang)
      if tts_out is not None:
        response = send_file(tts_out, attachment_filename=filename, mimetype='audio/mpeg')
        response.headers['X-Generated-Text'] = text.encode('utf-8').decode('latin-1')
        chatbot = get_chatbot_by_id(chatid=chatid, lang=lang)
        daemon = Thread(target=chatbot.get_response, args=(text,), daemon=True, name="repeat-learn-user"+utils.get_random_string(24))
        daemon.start()
        return response
      else:
        @after_this_request
        def clear_cache(response):
          cache.delete_memoized(AudioRepeatLearnClass.get, self, str, str, str)
          return make_response("TTS Generation Error!", 500)
    except AudioLimitException:
      return get_response_limit_error(text)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      g.request_error = str(e)
      @after_this_request
      def clear_cache(response):
        cache.delete_memoized(AudioRepeatLearnClass.get, self, str, str, str)
        return make_response(g.get('request_error'), 500)


@nsaudio.route('/repeat/learn/user/<string:user>/<string:text>/<string:voice>/')
@nsaudio.route('/repeat/learn/user/<string:user>/<string:text>/<string:voice>/<string:chatid>/')
@nsaudio.route('/repeat/learn/user/<string:user>/<string:text>/<string:voice>/<string:chatid>/<string:lang>/')
@nsaudio.route('/repeat/learn/user/<string:user>/<string:text>/<string:voice>/<string:chatid>/<string:lang>/<string:filename>')
class AudioRepeatLearnUserClass(Resource):
  @cache.cached(timeout=7200, query_string=True)
  def get (self, user: str, text: str, voice: str, chatid = "000000", lang = "it", filename = "audio.mp3"):
    try:
      tts_out = utils.get_tts(text, chatid=chatid, voice=voice, language=lang, user=user)
      if tts_out is not None:     
        response = send_file(tts_out, attachment_filename=filename, mimetype='audio/mpeg')
        response.headers['X-Generated-Text'] = text.encode('utf-8').decode('latin-1')
        chatbot = get_chatbot_by_id(chatid=chatid, lang=lang)
        daemon = Thread(target=chatbot.get_response, args=(text,), daemon=True, name="repeat-learn-user"+utils.get_random_string(24))
        daemon.start()
        return response
      else:
        @after_this_request
        def clear_cache(response):
          cache.delete_memoized(AudioRepeatLearnUserClass.get, self, str, str, str)
          return make_response("TTS Generation Error!", 500)
    except AudioLimitException:
      return get_response_limit_error(text)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      g.request_error = str(e)
      @after_this_request
      def clear_cache(response):
        cache.delete_memoized(AudioRepeatLearnUserClass.get, self, str, str, str)
        return make_response(g.get('request_error'), 500)

@nsaudio.route('/ask/<string:text>/')
@nsaudio.route('/ask/<string:text>/<int:learn>/')
@nsaudio.route('/ask/<string:text>/<int:learn>/<string:voice>/')
@nsaudio.route('/ask/<string:text>/<int:learn>/<string:voice>/<string:chatid>/')
@nsaudio.route('/ask/<string:text>/<int:learn>/<string:voice>/<string:chatid>/<string:lang>/')
class AudioAskClass(Resource):
  @cache.cached(timeout=30, query_string=True)
  def get (self, text: str, learn = 1, voice = "random", chatid = "000000", lang= "it"):
    try:
      tts_out = None
      dolearn = True if learn == 1 else False
      chatbot_resp = get_chatbot_by_id(chatid=chatid, lang=lang).get_response(text, learn=dolearn).text
      if voice is None or voice == "null" or voice == "random":
        voice = audiodb.select_voice_by_name_chatid_language(chatbot_resp.strip(), chatid, lang)
      if voice is not None:
        tts_out = utils.get_tts(chatbot_resp, chatid=chatid, voice=voice, language=lang)
      else:
        tts_out = utils.get_tts(chatbot_resp, chatid=chatid, voice="google", language=lang)
      if tts_out is not None:
        response = send_file(tts_out, attachment_filename='audio.mp3', mimetype='audio/mpeg')
        response.headers['X-Generated-Text'] = text.encode('utf-8').decode('latin-1')
        response.headers['X-Generated-Response-Text'] = chatbot_resp.encode('utf-8').decode('latin-1')
        return response
      else:
        threading.Thread(target=lambda: utils.populate_tts(chatbot_resp, chatid=chatid, voice=voice, language=lang)).start()
        @after_this_request
        def clear_cache(response):
          cache.delete_memoized(AudioAskClass.get, self, str, int, str, str, str)
          return make_response("TTS Generation Error!", 500)
    except AudioLimitException:
      return get_response_limit_error(chatbot_resp)
    except Exception as e:
      g.request_error = str(e)
      @after_this_request
      def clear_cache(response):
        cache.delete_memoized(AudioAskClass.get, self, str, int, str, str, str)
        return make_response(g.get('request_error'), 500)

@nsaudio.route('/ask/user/<string:text>/<string:user>/')
@nsaudio.route('/ask/user/<string:text>/<string:user>/<int:learn>/')
@nsaudio.route('/ask/user/<string:text>/<string:user>/<int:learn>/<string:voice>/')
@nsaudio.route('/ask/user/<string:text>/<string:user>/<int:learn>/<string:voice>/<string:chatid>/')
@nsaudio.route('/ask/user/<string:text>/<string:user>/<int:learn>/<string:voice>/<string:chatid>/<string:lang>/')
class AudioAskUserClass(Resource):
  @cache.cached(timeout=30, query_string=True)
  def get (self, text: str, user: str, learn = 1, voice = "random", chatid = "000000", lang= "it"):
    try:
      tts_out = None
      dolearn = True if learn == 1 else False
      chatbot_resp = get_chatbot_by_id(chatid=chatid, lang=lang).get_response(text, learn=dolearn).text
      if voice is None or voice == "null" or voice == "random":
        voice = audiodb.select_voice_by_name_chatid_language(chatbot_resp.strip(), chatid, lang)
      if voice is not None:
        tts_out = utils.get_tts(chatbot_resp, chatid=chatid, voice=voice, language=lang, user=user)
      else:
        tts_out = utils.get_tts(chatbot_resp, chatid=chatid, voice="google", language=lang, user=user)
      if tts_out is not None:
        response = send_file(tts_out, attachment_filename='audio.mp3', mimetype='audio/mpeg')
        response.headers['X-Generated-Text'] = text.encode('utf-8').decode('latin-1')
        response.headers['X-Generated-Response-Text'] = chatbot_resp.encode('utf-8').decode('latin-1')
        return response
      else:
        threading.Thread(target=lambda: utils.populate_tts(chatbot_resp, chatid=chatid, voice=voice, language=lang)).start()
        @after_this_request
        def clear_cache(response):
          cache.delete_memoized(AudioAskUserClass.get, self, str, str, int, str, str, str)
          return make_response("TTS Generation Error!", 500)
    except AudioLimitException:
      return get_response_limit_error(chatbot_resp)
    except Exception as e:
      g.request_error = str(e)
      @after_this_request
      def clear_cache(response):
        cache.delete_memoized(AudioAskUserClass.get, self, str, str, int, str, str, str)
        return make_response(g.get('request_error'), 500)

@nsaudio.route('/search/<string:text>/')
@nsaudio.route('/search/<string:text>/<string:chatid>/')
@nsaudio.route('/search/<string:text>/<string:chatid>/<string:lang>')
class AudioSearchClass(Resource):
  @cache.cached(timeout=10, query_string=True)
  def get (self, text: str, chatid = "000000", lang= "it"):
    wikisaid = utils.wiki_summary(text, lang)
    try:     
      if wikisaid is None:
        wikisaid = LibreTranslator(from_lang="it", to_lang=lang, base_url=os.environ.get("TRANSLATOR_BASEURL")).translate("Non ho trovato nessun risultato per") + ' :"' + text +"'"
      tts_out = utils.get_tts(wikisaid, chatid=chatid, voice="google", language=lang, save=False, call_fy=False, limit=False)
      if tts_out is not None:
        response = send_file(tts_out, attachment_filename='audio.mp3', mimetype='audio/mpeg')
        response.headers['X-Generated-Text'] = wikisaid.encode('utf-8').decode('latin-1')
        return response
      else:
        @after_this_request
        def clear_cache(response):
          cache.delete_memoized(AudioSearchClass.get, self, str, str, str)
          return make_response("TTS Generation Error!", 500)
    except AudioLimitException:
      return get_response_limit_error(wikisaid)
    except Exception as e:
      g.request_error = str(e)
      @after_this_request
      def clear_cache(response):
        cache.delete_memoized(AudioSearchClass.get, self, str, str, str)
        return make_response(g.get('request_error'), 500)


@nsaudio.route('/insult')
class AudioInsultClass(Resource):
  @api.expect(parserinsult)
  def get (self):
    sentence = ""
    try:

      sentence = insults.get_insults()
      lang = request.args.get("lang")
      if lang is None:
        lang = "it"  
      if lang != "it":
        sentence = LibreTranslator(from_lang="it", to_lang=lang, base_url=os.environ.get("TRANSLATOR_BASEURL")).translate(sentence)
      chatid = request.args.get("chatid")
      if chatid is None:
        chatid = "000000"
      text = request.args.get("text")
      if text and text != '' and text != 'none':
        sentence = text + " " + sentence
      if chatid == "000000":
        chatbot = get_chatbot_by_id(chatid=chatid, lang=lang)
        threading.Thread(target=lambda: chatbot.get_response(sentence)).start()
      tts_out = utils.get_tts(sentence, chatid=chatid, voice="google", language=lang)
      if tts_out is not None:    
        response = send_file(tts_out, attachment_filename='audio.mp3', mimetype='audio/mpeg')
        response.headers['X-Generated-Text'] = sentence.encode('utf-8').decode('latin-1')
        return response
      else:
        resp = make_response("TTS Generation Error!", 500)
        return resp
    except AudioLimitException:
      return get_response_limit_error(sentence)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      return make_response(str(e), 500)

nsmusic = api.namespace('music', 'Accumulators Chatbot Music APIs')


@nsmusic.route('/youtube/get/<string:url>/')
@nsmusic.route('/youtube/get/<string:url>/<string:chatid>')
class YoutubeGetClass(Resource):
  @cache.cached(timeout=10, query_string=True)
  def get (self, url: str, chatid = "000000"):
    try:
      audio, url = utils.get_youtube_audio(url,chatid)
      if audio is None:
        return make_response("YouTube Error", 500)
      else:
        response = send_file(audio, attachment_filename='song.mp3', mimetype='audio/mp3')
        response.headers['X-Generated-Text'] = url.encode('utf-8').decode('latin-1')
        return response
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      return make_response(str(e), 500)

nssoundboard = api.namespace('soundboard', 'Accumulators Soundboard APIs')

@nssoundboard.route('/random/<string:text>/')
@nssoundboard.route('/random/<string:text>/<string:chatid>')
class SoundboardRandomClass(Resource):
  @cache.cached(timeout=5, query_string=True)
  def get (self, text: str, chatid = "000000"):
    try:
      result = utils.random_myinstants_sound(text)
      if result is not None:
        return jsonify(result)
      else:
        @after_this_request
        def clear_cache(response):
          cache.delete_memoized(SoundboardRandomClass.get, self, str, str, str)
          return make_response("SoundBoard search Error!", 500)
    except Exception as e:
      g.request_error = str(e)
      @after_this_request
      def clear_cache(response):
        cache.delete_memoized(SoundboardRandomClass.get, self, str, str, str)
        return make_response(g.get('request_error'), 500)

@nssoundboard.route('/query/<string:text>/')
@nssoundboard.route('/query/<string:text>/<string:chatid>')
class SoundboardQueryClass(Resource):
  @cache.cached(timeout=5, query_string=True)
  def get (self, text: str, chatid = "000000"):
    try:
      results = utils.query_myinstants_sound(text)
      if len(results) > 0:
        return jsonify(results)
      else:
        @after_this_request
        def clear_cache(response):
          cache.delete_memoized(SoundboardQueryClass.get, self, str, str, str)
          return make_response("SoundBoard query Error!", 500)
    except Exception as e:
      g.request_error = str(e)
      @after_this_request
      def clear_cache(response):
        cache.delete_memoized(SoundboardQueryClass.get, self, str, str, str)
        return make_response(g.get('request_error'), 500)


nsimages = api.namespace('images', 'Accumulators Images APIs')


@nsimages.route('/search/<string:words>')
class AudioSearchClass(Resource):
  def get (self, words: str):
    bytes_img, attachment_filename, mimetype = image.search(words)
    return send_file(bytes_img, attachment_filename=attachment_filename, mimetype=mimetype)



nsutils = api.namespace('utils', 'AccumulatorsUtils APIs')



@nsutils.route('/fakeyou/listvoices/')
@nsutils.route('/fakeyou/listvoices/<string:lang>')
class FakeYouListVoices(Resource):
  @cache.cached(timeout=7200, query_string=True)
  def get(self, lang = "it"):
    try:
      voices = utils.list_fakeyou_voices(lang)
      if voices is not None:
        return jsonify(voices)
      else:
        cache.delete_memoized(FakeYouListVoices.get, self, str)
        return make_response("No voices found!", 500)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      cache.delete_memoized(FakeYouListVoices.get, self, str)
      return make_response(str(e), 500)

@nsutils.route('/fakeyou/deletetts/')
@nsutils.route('/fakeyou/deletetts/<int:limit>')
class FakeYouDeleteTTS(Resource):
  def get(self, limit = 1000):
    try:
      threading.Thread(target=lambda: utils.delete_tts(limit=limit)).start()
      return make_response("Starting thread delete_tts. Watch the logs for errors.", 200)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      cache.delete_memoized(FakeYouListVoices.get, self, str)
      return make_response(str(e), 500)

@nsutils.route('/init/<string:chatid>/')
@nsutils.route('/init/<string:chatid>/<string:lang>')
class InitChatterbotClass(Resource):
  def get(self, chatid = "000000", lang = "it"):
    try:
      #threading.Timer(0, get_chatbot_by_id, args=[chatid]).start()
      #return make_response("Initializing chatterbot. Watch the logs for errors.", 200)
      chatbot = get_chatbot_by_id(chatid=chatid, lang=lang)
      if chatbot is not None:
        return make_response("Initialized chatterbot on chatid " + chatid, 200)
      else:
        return make_response("Initializing chatterbot on chatid " + chatid + " failed", 500)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      return make_response(str(e), 500)

@nsutils.route('/initgenerator/<string:chatid>/<string:lang>')
class InitGeneratorClass(Resource):
  def get(self, chatid = "000000", lang = "it"):
    try:
      threading.Timer(10, utils.init_generator_models, args=[chatid, lang]).start()
      return make_response("Initializing Generator Models. Watch the logs for errors.", 200)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      return make_response(str(e), 500)



@limiter.limit("1/second")
@nsutils.route('/healthcheck')
class Healthcheck(Resource):
  def get (self):
    return "Ok!"

    
@nsutils.route('/sentences/generate/')
@nsutils.route('/sentences/generate/<string:chatid>/')
@nsutils.route('/sentences/generate/<string:chatid>/<int:learn>')
class SentencesGenerateClass(Resource):
  def get(self, chatid = "000000", learn = 0):
    try:
      text = utils.generate_sentence(chatid)
      if learn == 1:
        chatbot = get_chatbot_by_id(chatid)
        daemon = Thread(target=chatbot.get_response, args=(text,), daemon=True, name="sentences-generate"+utils.get_random_string(24))
        daemon.start()
      return make_response(text, 200)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      return make_response(str(e), 500)

    
@nsutils.route('/paragraph/generate/')
@nsutils.route('/paragraph/generate/<string:chatid>')
class ParagraphGenerateClass(Resource):
  def get(self, chatid = "000000"):
    try:
      return make_response(utils.generate_paragraph(chatid), 200)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      return make_response(str(e), 500)



nsdatabase = api.namespace('database', 'Accumulators Database APIs')


@nsdatabase.route('/download/sentences/')
@nsdatabase.route('/download/sentences/<string:chatid>')
class DownloadSentencesDb(Resource):
  def get(self, chatid = "000000"):
    try:      
      pattern = "./backups/" + chatid + "-db_backup_*.txt"
      latest_bk = (max(glob.glob(pattern), key=os.path.getmtime)) 
      if latest_bk is not None:
        return send_file(latest_bk, attachment_filename='trainfile.txt', mimetype="text/plain")
      else:
        return make_response("Failed to download sentences.", 500)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      return make_response(str(e), 500)




@nsdatabase.route('/delete/bytext/<string:text>/')
@nsdatabase.route('/delete/bytext/<string:text>/<string:chatid>')
class DatabaseDeleteByText(Resource):
  def get (self, text: str, chatid = "000000"):
    return get_response_str('Frasi con parola chiave "' + text + '" cancellate dal db chatbot!')



@nsdatabase.route('/audiodb/populate/')
@nsdatabase.route('/audiodb/populate/<int:limit>/')
@nsdatabase.route('/audiodb/populate/<int:limit>/<string:chatid>/')
@nsdatabase.route('/audiodb/populate/<int:limit>/<string:chatid>/<string:lang>/')
@nsdatabase.route('/audiodb/populate/<int:limit>/<string:chatid>/<string:lang>/<int:usetimer>/')
class DatabaseAudiodbPopulate(Resource):
  def get (self, limit = 100, chatid = "000000", lang = "it", usetimer = 0):
    if usetimer == 1:
      threading.Timer(0, utils.populate_audiodb_limited, args=[limit, chatid, lang]).start()
    else:
      threading.Timer(0, utils.populate_audiodb_unlimited, args=[limit, chatid, lang]).start()
    return get_response_str("Starting thread populate_audiodb [count:"+str(limit)+"] [chatid:"+str(chatid)+"] [lang:"+str(lang)+"]. Watch the logs.")
	

@nsdatabase.route('/upload/trainfile/txt')
class DatabaseTrainFile(Resource):
  def post (self):
    try:
      for thread in threading.enumerate(): 
        if thread.name == 'trainer_thread' and thread.is_alive():
          return make_response(str("Trainer thread is still running."), 500)
      chatid = request.form.get("chatid")
      if chatid is None:
        chatid = "000000"
      lang = request.form.get("lang")
      if lang is None:
        lang = "it"
      trf=request.files['trainfile']
      if not trf and utils.allowed_file(trf):
        return get_response_str("Error! Please upload a file name trainfile.txt with a sentence per line.")
      else:
        trainfile=TMP_DIR + utils.get_slashes() + utils.get_random_string(24) + ".txt"
        out_stream = BytesIO()
        trf.save(trainfile)
        #threading.Timer(0, utils.train_txt, args=[trainfile, get_chatbot_by_id(chatid, lang), lang, chatid]).start()
        chatbot = get_chatbot_by_id(chatid, lang)
        daemon = Thread(target=utils.train_txt, args=(trainfile,chatbot, lang, chatid,), daemon=True, name="trainer_thread")
        daemon.start()

        return get_response_str("Done. Watch the logs for errors.")
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      return get_response_str("Error! Please upload a file name trainfile.txt with a sentence per line.")

@nsdatabase.route('/reset/')
@nsdatabase.route('/reset/<string:chatid>')
class FiltersDelete(Resource):
  def get (self, chatid = "000000"):
    try:
      utils.reset(chatid)
      return get_response_str("All the sentences deleted from the database")
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      return make_response(str(e), 500)


@nsdatabase.route('/backup/chatbot/')
@nsdatabase.route('/backup/chatbot/<string:chatid>')
class BackupChatbot(Resource):
  def get (self, chatid = "000000"):
    filename = os.path.dirname(os.path.realpath(__file__)) + utils.get_slashes() + 'config' + utils.get_slashes() + chatid + '-db.txt'
    if utils.extract_sentences_from_chatbot(filename, chatid=chatid):
      utils.backupdb(chatid, "txt")
    return "Databases for chatid "+chatid+" backed up!"


@nsdatabase.route('/forcedelete/bytext/<string:text>/')
@nsdatabase.route('/forcedelete/bytext/<string:text>/<string:chatid>')
class AdminForceDeleteByText(Resource):
  def get (self, text: str, chatid = "000000"):
    try:
      for thread in threading.enumerate(): 
        if thread.name == 'trainer_thread' and thread.is_alive():
          return make_response(str("Trainer thread is still running."), 500)
      response = get_response_str(utils.delete_by_text(chatid, text, force=True))
      return response
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      return make_response(str(e), 500)

def get_chatbot_by_id(chatid = "000000", lang = "it"):
  if chatid + "_" + lang not in chatbots_dict:
    chatbots_dict[chatid + "_" + lang] = utils.get_chatterbot(chatid, os.environ['TRAIN'] == "True", lang = lang)
  return chatbots_dict[chatid + "_" + lang]
  
 
  
@scheduler.task('interval', id='backupdb', hours=12)
def backupdb():
  filename = os.path.dirname(os.path.realpath(__file__)) + '/config/' + chatid + '-db.txt'
  if utils.extract_sentences_from_chatbot(filename, chatid="000000"):
    utils.backupdb("000000", "txt")
  
@scheduler.task('interval', id='delete_tts', hours=12)
def delete_tts():
  utils.delete_tts(limit=100)

#if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
chatbots_dict = {}
cache.init_app(app)
limiter.init_app(app)
scheduler.init_app(app)
scheduler.start()


if __name__ == '__main__':
  app.run()
