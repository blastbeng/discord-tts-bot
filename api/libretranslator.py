from libretranslatepy import LibreTranslateAPI

class TranslationError(Exception):
    pass

class LibreTranslator():
    """
    @LibreProvider: This is a integration with LibreTranslate translation API.
    Website: https://libretranslate.com/
    Documentation: https://libretranslate.com/docs/
    Github: https://github.com/LibreTranslate/LibreTranslate
    """

    name = "Libre"

    def __init__(self, to_lang, from_lang='en', secret_access_key=None, region=None, base_url=None, **kwargs):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebit/535.19'
                                      '(KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19'}
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.secret_access_key = secret_access_key
        self.region = region
        self.kwargs = kwargs

        self.base_url = base_url
        self.api = LibreTranslateAPI(base_url, secret_access_key)

    def translate(self, text):
        if self.from_lang == self.to_lang:
            return text
        if self.from_lang == 'autodetect':
            from_lang = self.api.detect(text)[0]['language']
        else:
            from_lang = self.from_lang
        try:
            return self.api.translate(text, from_lang, self.to_lang)
        except Exception as e:
            raise TranslationError(e)