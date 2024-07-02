
from transliterate import translit, get_available_language_codes,detect_language
from transliterate.base import TranslitLanguagePack, registry

class MyLanguageRuPack(TranslitLanguagePack):
    #https://en.wikipedia.org/wiki/Russian_alphabet
    language_code = "castom_ru"
    language_name = "Castom_ru"
    character_ranges = ((0x0400, 0x04FF), (0x0500, 0x052F))
    detectable = True
    mapping = (
        u"абвгдезийклмнопрстуфхцЦъыьАБВГДЕЗИЙКЛМНОПРСТУФХЪЫЬ",
        u"abvgdezijklmnoprstufhcC_y_ABVGDEZIJKLMNOPRSTUFH_Y_",
    )

    reversed_specific_mapping = (
        u"eeEE",
        u"ёэЁЭ",
    )

    pre_processor_mapping = {
        u"ь":u"",
        u"ъ":u"",
        u"Ъ":u"",
        u"Ь":u"",
        u"э":u"e",
        u"ё":u"e",
        u"Ё":u"E",
        u"Э":u"E",
        u"ж":u"zh",
        u"ц":u"ts",
        u"ч":u"ch",
        u"ш":u"sh",
        u"щ":u"sch",
        u"ю":u"yu", #u"ju": u"ю",
        u"я":u"ya", #u"ja": u"я",
        u"Ж":u"Zh",
        u"Ц":u"Ts",
        u"Ч":u"Ch",
        u"Ш":u"Sh",
        u"Щ":u"Sch",
        u"Ю":u"Yu",#u"Ju": u"Ю",
        u"Я":u"Ya" #u"Ja": u"Я"
    }
registry.register(MyLanguageRuPack)

def my_detect_language(text):
    return detect_language(text)

def my_translite(text):
    return translit(text, 'castom_ru')


if __name__ == '__main__':
    print(my_detect_language('русский'))
    print(my_detect_language('русский или ne russci'))
    print(my_detect_language('ne russci'))