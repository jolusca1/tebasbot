from deep_translator import GoogleTranslator

def translate_elo(elo: str) -> str:
    return GoogleTranslator(source='auto', target='pt').translate(elo)
