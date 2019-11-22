import gpt_2_simple as gpt2

#Get the model loaded
run_name='TalkToMiya2'
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess,
               run_name=run_name)

maxprefix = 20 #sets size of max prefix in number of previous lines
tokensafterprefix = 50 #sets how many words to generate after the prefix
defaultname = 'Character' #the spoken of the ai character in the training data
defaultnametoken = 'CHARACTER - ' #the form of the ai's name when starting a line
defaultuser = 'User' #the name of the user in the training data
defaultusertoken = 'USER - ' #the form of the user's name when starting a line

print('Welcome to TalkToCharacter')
print('This program lets you talk to a finetuned AI that resembles a specific character')
playername = input('Please choose a name:')

print(defaultnametoken + 'Hello ' + playername + '!')
#Create stack of previous messages
previousmessages = [defaultnametoken + 'Hello '+ defaultuser + '!\n']
while True:
    playertext = input(playername.upper() + ' - ')
    playertext = defaultusertoken + playertext + '\n' #Make the program think player is the username
    previousmessages.append(playertext)
    #Need code to handle stacking up to 10 previous messages
    if len(previousmessages) <= maxprefix:
        prefix = ''.join(previousmessages)
        prefixlinecount = len(previousmessages)
    else:
        prefix = ''.join(previousmessages[-maxprefix:])
        prefixlinecount = maxprefix
    #print(fulltext)
    success = 0
    while success == 0:
        #Figure out how long the output needs to be
        length = len(prefix.split()) + tokensafterprefix
        aitext = gpt2.generate(sess,
                                run_name=run_name,
                                prefix=prefix,
                                length=length,
                                return_as_list=True
                                )[0]
        #print('start of AI text\n' + aitext +'\n end of AI text')
        #print(prefixlinecount)
        #Split output into individual lines
        aitext = aitext.splitlines()
        #Chop off the prefix
        aitext = aitext[prefixlinecount:]
        #Fetch the lines where AI speaks
        aitext = [i for i in aitext if i.startswith(defaultnametoken)]
        #If there is at least one appropriate line, this works
        if len(aitext) > 0:
            success = 1
            #Use the first reply, most likely to be appropriate
            aitext = aitext[0]
            previousmessages.append(aitext + '\n')
            #Make AI use the player's name
            print(aitext.replace(defaultuser,playername))
