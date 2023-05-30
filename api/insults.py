import random
import logging
import os
from dotenv import load_dotenv
from os.path import dirname
from os.path import join

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger('werkzeug')
log.setLevel(int(os.environ.get("LOG_LEVEL")))


def get_insults():
    try:

        words = [ 
        "aborto",
        "alcolizzato",
        "analfabeta",
        "autoinculati",
        "baciacazzi",
        "baciaculi",
        "baciami il culo",
        "baciami il cazzo",
        "baciami la minchia",
        "bagascia",
        "bastardo",
        "battone",
        "bestia di satana",
        "bestia",
        "bimbominkia",
        "bitume",
        "blatta",
        "bocchinaro", 
        "brutto",
        "buzzurro",
        "cafone",
        "cagata bianca",
        "cagacazzi",
        "cagaminchia",
        "cannato",
        "capezzolo",
        "carciofo",
        "carogna",
        "cattivo",
        "cazzone",
        "cimice",
        "ciucciami la minchia",
        "ciucciami lo scroto",
        "cocainomane",
        "coglionazzo",
        "coglione",
        "colata di sborra",
        "colata di merda",
        "crucco",
        "culattone",
        "culo sfondato"
        "deficiente",
        "disagio",
        "disagiato",
        "drogato",
        "ebete",
        "energumeno",
        "eroinomane",
        "fancazzista",
        "fammi un bocchino",
        "fammi una sega",
        "farabutto",
        "fetido",
        "ficcati un dito in culo",
        "fogna", 
        "frocio",
        "fuso mentale",
        "gallinaio",
        "gay",
        "iena",
        "ignobile",
        "ignorante",
        "imbecille",
        "immondizia",
        "impazzito",
        "impertinente",
        "incapace",
        "infame",
        "infetto",
        "inginocchiati e baciami",
        "larva",
        "latrina", 
        "lavativo", 
        "leccaculo",
        "leccafighe",
        "leccami il cazzo",
        "lecchino",
        "lesbica",
        "lestofante",
        "liquame",
        "lo sai cosa sei vero? brutto",
        "lombrico", 
        "lurido",
        "microcefalo",
        "maiale",
        "malandrino",
        "melanzana",
        "merda",
        "merdaccia",
        "mi fai ribrezzo",
        "mi fai schifo",
        "mi fai venire voglia di suicidarmi",
        "mignotta",
        "mignottone",
        "minchione",
        "mongoloide",
        "muori",
        "muori male",
        "nutria",
        "omosessuale",
        "pantofolaio",
        "pazzo"
        "pezzente"
        "pezzo di merda"
        "pezzo di culo"
        "prostituta"
        "pulisciti il culo",
        "pulisciti la bocca",
        "pulisciti la figa",
        "pusillanime",
        "puttaniere",
        "quaquaraqua",
        "ratto",
        "reietto",
        "rompicazzo",
        "rompicoglioni",
        "sacco di merda", 
        "sadomasochista",
        "scarafaggio",
        "scassacazzi",
        "scemo",
        "schifo", 
        "schifezza", 
        "schifoso",
        "secchione",
        "segaiolo",
        "sessodipendente",
        "spacciatore", 
        "spazzatura",
        "spruzzata di merda",
        "stercorario",
        "stronzo",
        "stronzone",
        "stupido",
        "succhiacazzi", 
        "succhiami la minchia", 
        "tamarro",
        "terrone",
        "testa di cazzo",
        "testa di culo",
        "testa di figa",
        "testa di minchia",
        "truzzo",
        "topo",
        "topo di fogna",
        "usuraio",
        "vaffanculo",
        "vai a cagare",
        "vai a fare in culo",
        "vai a dare via il culo",
        "vai a morire male",
        "vegetale", 
        "verme",
        "villano",
        "viscido",
        "vucumpra",
        "zucchina" ]

        size = len(words)
        n = random.randint(0,size-1)
        sentence = words[n]
        #sentence = random.choice(words);

        words2 = words;
        words2.remove(sentence)
        
        size2 = len(words2)
        n2 = random.randint(0,size2-1)
        sentence2 = words2[n2]

        words3 = words2;
        words3.remove(sentence2)
        
        size3 = len(words3)
        n3 = random.randint(0,size3-1)
        sentence3 = words3[n3]

        insult = sentence + " " + sentence2 + " " + sentence3
        return insult
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      raise Exception(e)
