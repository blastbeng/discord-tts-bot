class AudioLimitException(Exception):
    "Generated TTS length is longer than max limit"
    pass

class BlockedWordException(Exception):
    def __init__(self, word):
        self.message = "This sentence contains a word that is blocked by filters [" + word + "]"
    def __str__(self):
        return self.message

class TimeExceededException(Exception):
    "Max execution time exceeded"
    pass