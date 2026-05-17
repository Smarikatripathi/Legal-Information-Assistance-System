from langdetect import detect


def detect_language(text):

    try:
        return detect(text)

    except:
        return "en"