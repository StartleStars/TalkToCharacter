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

#Find all character .ini files in directory
import os
availablecharacters = []
for file in os.listdir("./characters"):
    if file.endswith(".ini"):
        availablecharacters.append(file)
selectedcharacter = ""

#Create function to retrieve info from a .ini file
def GetCharacterIni(configname):
    config = ConfigParser()
    config.read("./characters/"+configname)
    dictionary = {}
    for section in config.sections():
        dictionary[section] = {}
        for option in config.options(section):
            dictionary[section][option] = config.get(section, option)
    return dictionary

#Initialize Kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.properties import StringProperty
from kivy.uix.scrollview import ScrollView

#Put together character selection list
#This is from the example here(https://kivy.org/doc/stable/api-kivy.uix.recycleview.html)
#Except we use the list of available characters
#And use the selection on the list to set the "selectedcharacter" variable

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
            App.get_running_app().selectedcharacter = rv.characterfile[index]
            #we need to update all the bio information from the .ini
            dictionary = GetCharacterIni(rv.characterfile[index])
            App.get_running_app().bio_characterbio = dictionary["bio"]["bio"]
            App.get_running_app().bio_imagesource = "./characters/" + dictionary["technical"]["characterfolder"]+"/"+dictionary["bio"]["image"]
        else:
            print("selection removed for {0}".format(rv.data[index]))

class CharacterList(RecycleView):
    def __init__(self, **kwargs):
        super(CharacterList, self).__init__(**kwargs)
        self.data = [{'text': str(x[:-4])} for x in availablecharacters] #set label to be file names without .ini
        self.characterfile = availablecharacters

#Put together the Main Menu

class MainMenu(App):
    #get locale strings for all text
    locale_menu = StringProperty(_('Menu'))
    locale_appname = StringProperty(_('TalkToCharacter'))
    locale_charfolder = StringProperty(_('Open Character Folder'))
    locale_chardownload = StringProperty(_('Download Characters'))
    locale_feed = StringProperty(_('News Feed'))
    locale_technical = StringProperty(_('Technical Details'))
    locale_settings = StringProperty(_('Settings'))
    locale_start = StringProperty(_('Start Chat'))
    bio_imagesource = StringProperty('./example.png')
    bio_characterbio = StringProperty(_('Character Bio'))
    pass

if __name__ == '__main__':
    app = MainMenu()
    app.run()
