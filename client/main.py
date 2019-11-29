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

#Find characters in directory
import os
availablecharacters = []
for file in os.listdir("./characters"):
    if file.endswith(".ini"):
        availablecharacters.append(file)

#Initialize Kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image

class MainMenu(App):
    def build(self):
        layout = BoxLayout(padding=10,
                           orientation = 'horizontal')
        #build the left side
        left_side = BoxLayout(padding=10,
                              orientation = 'vertical',
                              size_hint = (.3, 1))
        layout.add_widget(left_side)
        #build the left hand side's top bar
        left_side_top = BoxLayout(size_hint = (1, .1))
        left_side.add_widget(left_side_top)
        top_button = Button(text=_('Menu'),
                            background_color = [1,0,0,1],
                            size_hint = (0.2,1))
        left_side_top.add_widget(top_button)
        top_label = Label(text=_('TalkToCharacter'),
                          size_hint = (0.8,1))
        left_side_top.add_widget(top_label)
        #build the character select
        character_selection = Label(text=_('Character Selection'),
                                    size_hint=(1, .7))
        left_side.add_widget(character_selection)
        #build the "open character directory" button
        character_directory = Button(text=_("Open Character Folder"),
                                     background_color = [1,0,0,1],
                                     size_hint =(1, .1))
        left_side.add_widget(character_directory)
        #build the "download characters" button
        character_download = Button(text=_("Download More Characters"),
                                     background_color = [1,0,0,1],
                                     size_hint =(1, .1))
        left_side.add_widget(character_download)
        #build the right side
        right_side = BoxLayout(padding=10,
                               orientation = 'vertical',
                               size_hint = (.7, 1))
        layout.add_widget(right_side)
        #build the feed
        feed_window = Label(text=_('News Feed'),
                            size_hint = (1, .3))
        right_side.add_widget(feed_window)
        #build character info
        character_info = BoxLayout(padding=10,
                                   orientation = 'horizontal',
                                   size_hint = (1, .7))
        right_side.add_widget(character_info)
        #build left side of character info
        character_left = BoxLayout(padding=10,
                                   orientation = 'vertical',
                                   size_hint = (.4, 1))
        character_info.add_widget(character_left)
        #build image of character
        character_image = Image(source='./example.png',
                                size_hint=(1, .4))
        character_left.add_widget(character_image)
        #build technical details
        character_technical = Label(text=_('Technical Details'),
                                    size_hint=(1,.4))
        character_left.add_widget(character_technical)
        #build settings button
        settings_button = Button(text=_("Settings"),
                                 background_color = [1,0,0,1],
                                 size_hint=(1,.2))
        character_left.add_widget(settings_button)
        #build right side of character info
        character_right = BoxLayout(padding=10,
                                    orientation = 'vertical',
                                    size_hint = (.6, 1))
        character_info.add_widget(character_right)
        #build character bio
        character_bio = Label(text=_('Character Bio'),
                              size_hint = (1, .8))
        character_right.add_widget(character_bio)
        #build start button
        start_button = Button(text=_("Start Chat"),
                              background_color = [1,0,0,1],
                              size_hint=(1, .2))
        character_right.add_widget(start_button)
        return layout

if __name__ == '__main__':
    app = MainMenu()
    app.run()
