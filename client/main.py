import platform
import subprocess
import pickle

#Initialize config
#Need to use Kivy's modified ConfigParser
from kivy.config import ConfigParser
#We won't call this config so it can't be confused with the App's config later
iniconfig = ConfigParser()
iniconfig.read('main.ini')

lang = iniconfig.get('language','language')
debug = iniconfig.getboolean('debugging','debug')
requires_avx = iniconfig.getboolean('dependencies','requires_avx')

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

#function to retrieve info from a .ini file
#this should be changed to just keep a configparser object instead of converting to dictionary
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
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.factory import Factory
from kivy.uix.popup import Popup

#import GPT2
#this MUST be imported after Kivy. See https://github.com/tensorflow/tensorflow/issues/27312
import gpt_2_simple as gpt2

#function to load a model
def LoadModel(modelname):
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess,
                   checkpoint_dir="characters",
                   run_name=modelname)
    return sess

def GenerateLine(run_name,prefix,length,temperature):
    sess = App.get_running_app().session
    return gpt2.generate(sess,
                         checkpoint_dir="characters",
                         run_name=run_name,
                         prefix=prefix,
                         length=length,
                         temperature=temperature,
                         return_as_list=True
                         )[0]

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
            #put together technical details
            App.get_running_app().bio_technical = "Version: " + dictionary["techinfo"]["version"] + "\nModel: " + dictionary["techinfo"]["modeltype"]
        else:
            print("selection removed for {0}".format(rv.data[index]))

class CharacterList(RecycleView):
    def __init__(self, **kwargs):
        super(CharacterList, self).__init__(**kwargs)
        self.data = [{'text': str(x[:-4])} for x in availablecharacters] #set label to be file names without .ini
        self.characterfile = availablecharacters

#Put together the Menu
class MenuScreen(Screen):
    pass

class ChatScreen(Screen):
    def on_enter(self):
        #check if we need to load a character
        if App.get_running_app().selectedcharacter != App.get_running_app().loadedcharacter:
            #prepare to load character
            App.get_running_app().chat_history = _('Loading Character, this may take a while...')
            #we need to get info about the character from the ini
            characterini = GetCharacterIni(App.get_running_app().selectedcharacter)
            #save this for later
            App.get_running_app().characterini = characterini
            #these files are huge so need seperate thread to load
            #otherwise windows will think the application is not responding
            #UNFINISHED - NEED TO RESEARCH HOW TO DO THIS
            #Do try except in case the character doesn't exist
            try:
                App.get_running_app().session = LoadModel(characterini["technical"]["characterfolder"])
            except:
                print(_("Error: No character data could be loaded"))
                App.get_running_app().chat_history = _('Character not loaded, suitable data not found')
                App.get_running_app().loadedcharacter = "None"
                App.get_running_app().generic_popup(_('Error'),_('Character not loaded, suitable data not found'),_('Close'))
                return
            #App.get_running_app().chat_history = characterini["bio"]["charactername"] + _(' has been loaded.')
            #we don't want to reload the same character twice in a row
            App.get_running_app().loadedcharacter = App.get_running_app().selectedcharacter
            #setup prefix and message history
            App.get_running_app().messagehistory.append(characterini["bio"]["charactername"] + _(' has been loaded.\n'))
            App.get_running_app().messagehistory.append(characterini["technical"]["defaultnametoken"] + ' Hello ' + characterini["technical"]["defaultuser"] + '!\n')
            App.get_running_app().prefixhistory.append(characterini["technical"]["defaultnametoken"] + ' Hello ' + characterini["technical"]["defaultuser"] + '!\n')
            #Display initial text
            self.update_chat()

    def generate_response(self, playerline):
        #prevent the player from talking to a character that hasn't loaded
        if App.get_running_app().loadedcharacter == "None":
            print(_("Error: Trying to send message to a character that doesn't exist"))
            App.get_running_app().generic_popup(_('Error'),_('Please load a character first'),_('Close'))
            return
        #ensure a blank line hasn't been sent
        if playerline != '':
            #Clear the player's input now that we've recieved it
            App.get_running_app().chat_input = ''
            #Might need to improve how config is retrieved
            appconfig = App.get_running_app().config
            maxprefix = appconfig.getint('generate','maxprefix')
            tokensafterprefix = appconfig.getint('generate','tokensafterprefix')
            temperature = appconfig.getfloat('generate','temperature')
            #Need to get dictionary containing the character .ini
            characterini = App.get_running_app().characterini
            #Update chat history
            messageline = characterini["technical"]["defaultusertoken"] + ' ' + playerline + '\n'
            App.get_running_app().messagehistory.append(messageline)
            self.update_chat()
            #Make the program think player is the username
            prefixline = characterini["technical"]["defaultusertoken"] + ' ' + playerline + '\n'
            App.get_running_app().prefixhistory.append(prefixline)
            #stack together previous lines to generate the prefix
            if len(App.get_running_app().prefixhistory) <= maxprefix:
                prefix = ''.join(App.get_running_app().prefixhistory)
                prefixlinecount = len(App.get_running_app().prefixhistory)
            else:
                prefix = ''.join(App.get_running_app().prefixhistory[-maxprefix:])
                prefixlinecount = maxprefix
            #debug contents of prefix
            print('Prefix:\n' + prefix)
            #how long does output need to be?
            length = len(prefix.split()) + tokensafterprefix
            #prepare to generate
            success = 0
            while success == 0:
                aitext = GenerateLine(characterini["technical"]["characterfolder"],prefix,length,temperature)
                #debug contents of generated text
                print('Generated text:\n' + aitext)
                #Split output into individual lines
                aitext = aitext.splitlines()
                #Chop off the prefix
                aitext = aitext[prefixlinecount:]
                #Fetch the lines where AI speaks
                aitext = [i for i in aitext if i.startswith(characterini["technical"]["defaultnametoken"])]
                #If there is at least one appropriate line, this works
                if len(aitext) > 0:
                    success = 1
                    #Use the first reply, most likely to be appropriate
                    aitext = aitext[0]
                    App.get_running_app().prefixhistory.append(aitext + '\n')
                    App.get_running_app().messagehistory.append(aitext + '\n')
            #Update chat history
            self.update_chat()
        pass
    
    def generate_redo(self):
        #A lot of this function is duplicating code from generate_response
        if App.get_running_app().loadedcharacter == "None":
            print(_("Error: Trying to redo message with a character that doesn't exist"))
            App.get_running_app().generic_popup(_('Error'),_('Please load a character first'),_('Close'))
            return
        #Should clean that up
        App.get_running_app().chat_input = ''
        #Might need to improve how config is retrieved
        appconfig = App.get_running_app().config
        maxprefix = appconfig.getint('generate','maxprefix')
        tokensafterprefix = appconfig.getint('generate','tokensafterprefix')
        temperature = appconfig.getfloat('generate','temperature')
        #Need to get dictionary containing the character .ini
        characterini = App.get_running_app().characterini
        #Remove last AI line from prefix and message history
        App.get_running_app().prefixhistory.pop()
        App.get_running_app().messagehistory.pop()
        #stack together previous lines to generate the prefix
        if len(App.get_running_app().prefixhistory) <= maxprefix:
            prefix = ''.join(App.get_running_app().prefixhistory)
            prefixlinecount = len(App.get_running_app().prefixhistory)
        else:
            prefix = ''.join(App.get_running_app().prefixhistory[-maxprefix:])
            prefixlinecount = maxprefix
        #debug contents of prefix
        print('Prefix:\n' + prefix)
        #how long does output need to be?
        length = len(prefix.split()) + tokensafterprefix
        #prepare to generate
        success = 0
        while success == 0:
            aitext = GenerateLine(characterini["technical"]["characterfolder"],prefix,length,temperature)
            #debug contents of generated text
            print('Generated text:\n' + aitext)
            #Split output into individual lines
            aitext = aitext.splitlines()
            #Chop off the prefix
            aitext = aitext[prefixlinecount:]
            #Fetch the lines where AI speaks
            aitext = [i for i in aitext if i.startswith(characterini["technical"]["defaultnametoken"])]
            #If there is at least one appropriate line, this works
            if len(aitext) > 0:
                success = 1
                #Use the first reply, most likely to be appropriate
                aitext = aitext[0]
                App.get_running_app().prefixhistory.append(aitext + '\n')
                App.get_running_app().messagehistory.append(aitext + '\n')
        #Update chat history
        self.update_chat()
    pass

    def update_chat(self):
        App.get_running_app().chat_history = ''.join(App.get_running_app().messagehistory)

    def save_chat(self):
        pickle.dump([App.get_running_app().prefixhistory, App.get_running_app().messagehistory], open( "save.p", "wb"))
        App.get_running_app().generic_popup(_('Notice'),_('Conversation saved as save.p'),_('Close'))

    def load_chat(self):
        try:
            App.get_running_app().prefixhistory, App.get_running_app().messagehistory = pickle.load(open( "save.p", "rb"))
            self.update_chat()
            App.get_running_app().generic_popup(_('Notice'),_('Loaded save.p'),_('Close'))
        except:
            print(_("Error: Could not load the file. Does it even exist?"))
            App.get_running_app().generic_popup(_('Error'),_('Could not load the saved conversation'),_('Close'))
            
class MainApp(App):
    #get locale strings for all text
    locale_menu = StringProperty(_('Menu'))
    locale_appname = StringProperty(_('TalkToCharacter'))
    locale_charfolder = StringProperty(_('Open Character Folder'))
    locale_chardownload = StringProperty(_('Download Characters'))
    locale_feed = StringProperty(_('News Feed'))
    locale_settings = StringProperty(_('Settings'))
    locale_start = StringProperty(_('Start Chat'))
    locale_send = StringProperty(_('Send'))
    locale_redo = StringProperty(_('Redo'))
    locale_back = StringProperty(_('Back'))
    locale_save = StringProperty(_('Save'))
    locale_load = StringProperty(_('Load'))
    bio_imagesource = StringProperty('./example.png')
    bio_characterbio = StringProperty(_('Character Bio'))
    bio_technical = StringProperty(_('Technical Details'))
    chat_history = StringProperty(_('Text'))
    chat_input = StringProperty(_('Message Area'))
    selectedcharacter = StringProperty(_('None'))
    loadedcharacter = StringProperty(_('None'))
    session = ObjectProperty(None)
    prefixhistory = []
    messagehistory = []
    characterini = {}

    #Load the config
    def build_config(self,config):
        config.setdefaults(
            'user', {
                'username': 'User'})
        config.setdefaults(
            'generate', {
                'maxprefix': '10',
                'temperature': '0.3',
                'tokensafterprefix': '20'})
        config.setdefaults(
            'language', {
                'langauge': 'en'})
        config.setdefaults(
            'debugging', {
                'debug': 'no'})
        config.setdefaults(
            'dependencies', {
                'requires_avx': 'yes'})
                
    #create the settings ui
    def build_settings(self, settings):
        settings.add_json_panel('TalkToCharacter', self.config, 'settingpanel.json')

    #build!
    def build(self):
        config = self.config

    #function to print info about the config change
    def on_config_change(self, config, section, key, value):
        if config is self.config:
            print(section + ':' + key + ' has been set to ' + value)
    
    #function to open a specific folder in explorer or cross-platform equivalent
    def open_folder(self, path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            try:
                subprocess.Popen(["xdg-open", path])
            except:
                print("Could not determine OS for opening folder")

    pass

    #function to create a notice popup where the only interaction is to close it
    def generic_popup(self, title, label, close):
        #Construct Popup
        popupcontent = BoxLayout(orientation='vertical')
        popupcontent.add_widget(Label(text=label))
        popupbutton = Button(text=close, size_hint = (1,0.2), background_color = (1,0,0,1))
        popupcontent.add_widget(popupbutton)
        popup = Popup(title=title,
                content=popupcontent,
                size_hint=(None,None), size=(400,400))
        #have to bind button after the popup has been created
        popupbutton.bind(on_release=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    MainApp().run()
