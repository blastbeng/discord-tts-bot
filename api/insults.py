import random
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from os.path import dirname
from os.path import join
from pathlib import Path

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger('werkzeug')
log.setLevel(int(os.environ.get("LOG_LEVEL")))

def change_gender(string):
    dictionary = { 
    "aborto":"aborto",
    "alcolizzato":"alcolizzato",
    "analfabeta":"analfabeta",
    "autoinculati":"autoinculati",
    "baciacazzi":"baciacazzi",
    "baciaculi":"baciaculi",
    "baciami il culo":"baciami il culo",
    "baciami il cazzo":"baciami il cazzo",
    "baciami la minchia":"baciami la minchia",
    "bagascia":"bagascia",
    "bastardo":"bastarda",
    "battone":"battona",
    "bestia di satana":"bestia di satana",
    "bestia":"bestia",
    "bimbominkia":"bimbominkia",
    "bitume":"bitume",
    "blatta":"blatta",
    "bocchinaro" :"bocchinara" ,
    "brutto":"brutta",
    "buzzurro":"buzzurra",
    "cafone":"cafona",
    "cagata bianca":"cagata bianca",
    "cagacazzi":"cagacazzi",
    "cagaminchia":"cagaminchia",
    "cannato":"cannata",
    "capezzolo":"capezzolo",
    "carciofo":"carciofo",
    "carogna":"carogna",
    "cattivo":"cattiva",
    "cazzone":"cazzona",
    "cimice":"cimice",
    "ciucciami la minchia":"ciucciami la minchia",
    "ciucciami lo scroto":"ciucciami lo scroto",
    "cocainomane":"cocainomane",
    "coglionazzo":"coglionazza",
    "coglione":"cogliona",
    "colata di sborra":"colata di sborra",
    "colata di merda":"colata di merda",
    "crucco":"crucca",
    "culattone":"culattona",
    "culo sfondato":"culo sfondato",
    "deficiente":"deficiente",
    "disagio":"disagio",
    "disagiato":"disagiata",
    "drogato":"drogata",
    "ebete":"ebete",
    "energumeno":"energumena",
    "eroinomane":"eroinomane",
    "fancazzista":"fancazzista",
    "fammi un bocchino":"fammi un bocchino",
    "fammi una sega":"fammi una sega",
    "farabutto":"farabutta",
    "fetido":"fetida",
    "ficcati un dito in culo":"ficcati un dito in culo",
    "fogna" :"fogna",
    "frocio":"frocia",
    "fuso":"fusa",
    "fuso mentale":"fusa mentale",
    "gallinaio":"gallinaia",
    "gay":"gay",
    "iena":"iena",
    "ignobile":"ignobile",
    "ignorante":"ignorante",
    "imbecille":"imbecille",
    "immondizia":"immondizia",
    "impazzito":"impazzita",
    "impertinente":"impertinente",
    "incapace":"incapace",
    "infame":"infame",
    "infetto":"infetta",
    "inginocchiati e baciami":"inginocchiati e baciami",
    "larva":"larva",
    "latrina" :"latrina",
    "lavativo" :"lavativa",
    "leccaculo":"leccaculo",
    "leccafighe":"leccafighe",
    "leccami il cazzo":"leccami il cazzo",
    "lecchino":"lecchina",
    "lesbica":"lesbica",
    "lestofante":"lestofante",
    "liquame":"liquame",
    "lo sai cosa sei vero? brutto":"lo sai cosa sei vero? brutta",
    "lombrico" :"lombrica",
    "lurido":"lurida",
    "microcefalo":"microcefala",
    "maiale":"maiale",
    "malandrino":"malandrina",
    "melanzana":"melanzana",
    "merda":"merda",
    "merdaccia":"merdaccia",
    "mi fai ribrezzo":"mi fai ribrezzo",
    "mi fai schifo":"mi fai schifo",
    "mi fai venire voglia di suicidarmi":"mi fai venire voglia di suicidarmi",
    "mignotta":"mignotta",
    "mignottone":"mignottona",
    "minchione":"minchiona",
    "mongoloide":"mongoloide",
    "muori":"muori",
    "muori male":"muori male",
    "nababbo":"nababba",
    "ninfomane":"ninfomane",
    "nutria":"nutria",
    "omosessuale":"omosessuale",
    "pantofolaio":"pantofolaia",
    "pazzo":"pazza",
    "pezzente":"pezzente",
    "pezzo di merda":"pezza di merda",
    "pezzo di culo":"pezza di culo",
    "prostituta":"prostituta",
    "pulisciti il culo":"pulisciti il culo",
    "pulisciti la bocca":"pulisciti la bocca",
    "pulisciti la figa":"pulisciti la figa",
    "pusillanime":"pusillanime",
    "puttaniere":"puttaniera",
    "quaquaraqua":"quaquaraqua",
    "ratto":"ratto",
    "reietto":"reietta",
    "rompicazzo":"rompicazzo",
    "rompicoglioni":"rompicoglioni",
    "sacco di merda" :"sacco di merda",
    "sadomasochista":"sadomasochista",
    "scarafaggio":"scarafaggia",
    "scassacazzi":"scassacazzi",
    "scemo":"scema",
    "schifo" :"schifo",
    "schifezza" :"schifezza", 
    "schifoso":"schifosa",
    "secchione":"secchiona",
    "segaiolo":"segaiola",
    "sessodipendente":"sessodipendente",
    "spacciatore" :"spacciatrice",
    "spazzatura":"spazzatura",
    "spruzzata di merda":"spruzzata di merda",
    "stercorario":"stercorario",
    "stronzo":"stronza",
    "stronzone":"stronzona",
    "stupido":"stupida",
    "succhiacazzi" :"succhiacazzi",
    "succhiami la minchia" :"succhiami la minchia",
    "tamarro":"tamarra",
    "terrone":"terrona",
    "testa di cazzo":"testa di cazzo",
    "testa di culo":"testa di culo",
    "testa di figa":"testa di figa",
    "testa di minchia":"testa di minchia",
    "truzzo":"truzza",
    "topo":"topa",
    "topo di fogna":"topa di fogna",
    "usuraio":"usuraia",
    "vaffanculo":"vaffanculo",
    "vai a cagare":"vai a cagare",
    "vai a fare in culo":"vai a fare in culo",
    "vai a dare via il culo":"vai a dare via il culo",
    "vai a morire male":"vai a morire male",
    "vegetale" :"vegetale",
    "verme":"verme",
    "villano":"villana",
    "viscido":"viscida",
    "vucumpra":"vucumpra",
    "zucchina":"zucchina",                                 
    }
 
    string += ' '  # Append a space at the end
 
    n = len(string)
 
    # 'temp' string will hold the intermediate words
    # and 'ans' string will be our result
    temp = ""
    ans = ""
 
    for i in range(n):
        if string[i] != ' ':
            temp += string[i]
        else:
            # If this is a 'male' or a 'female' word then
            # swap this with its counterpart
            if temp in dictionary:
                temp = dictionary[temp]
 
            ans += temp + ' '
            temp = ""
 
    return ans

def get_insults(gender=True):
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
        if gender:
            insult_female = change_gender(insult)
            return insult_female
        else:
            return insult
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
      return "stronzo mi sono spaccato male, blast deve sistemarmi"
