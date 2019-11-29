#Initialize config
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

username = config.get('user','username')
maxprefix = config.get('ai','maxprefix')
tokensafterprefix = config.get('ai','tokensafterprefix')
temperature = config.get('ai','temperature')
lang = config.get('language','language')
debug = config.getboolean('debugging','debug')
requires_avx = config.getboolean('dependencies','requires_avx')

#Initialize locales
import gettext
def lang_load(lang):
    if lang == 'en':
        _ = lambda s:s #If language is English, just return the default string
    else:
        lang_translations = gettext.translation('main', localedir = 'locales', languages = lang)
        lang_translations.install()
        _ = lang_translations.gettext
    return _
#load language from config
_ = lang_load(lang)
print(_("Language Loaded"))

#Check for AVX instruction set on CPU - default version of tensorflow requires it
import cpufeature
if requires_avx == True:
    if cpufeature.CPUFeature['AVX'] == False:
        print(_("This program requires AVX, which your CPU may not support. A legacy version of TalkToCharacter with support for older CPUs without AVX may be available."))
if requires_avx == False:
    if cpu.feature.CPUFeature['AVX'] == True:
        print(_("Your CPU may support AVX, but this version of TalkToCharacter does not. You may see better performance when using the standard version of TalkToCharacter."))
print(_("CPU Checked"))

#Check system RAM
#INCOMPLETE

