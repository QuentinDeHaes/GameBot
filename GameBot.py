
import random

from BotDatabase import DatabaseUpdate
import discord
from BotDatabase import AddGame

from BotDatabase import RemoveGame
from BotDatabase import getgames
from BotDatabase import RemovePlayer
from BotDatabase import GetAllGames
from BotDatabase import addCategory
from BotDatabase import getCategories
from BotDatabase import AddTTS
from BotDatabase import RemoveTTS
from BotDatabase import PlayTTS
from BotDatabase import ChangeName
from BotDatabase import addToAll
BotID = '<@538788024541118494>' #the ID of the bot
TOKEN = ''

BOTNAME = "GameBot"
def getAllgamesList(list):
    string =""
    currentgame = ""
    for x in list:
        if x[0]==currentgame:
            string += " -" + x[1]
        else:
            string+= "\n"+ x[0]
            string += " -" + x[1]
            currentgame=x[0]

    return string



def makePrettyList(list):
    string = ""
    list2 = []
    for x in list:
        string+= x[0]
        string+= '\n'
        list2.append(x[0])
    return string,list2


def unsplit(list):
    string =""
    for x in list:
        string+=x
        string+=" "
    return string



def run():
    client = discord.Client()
    parser = DatabaseUpdate()
    # server =discord.Server()



    @client.event
    async def on_ready():
        parser.run()


    @client.event
    async def on_message(message):
        server = message.server

        if message.author == client.user:
            return
        if client.user not in message.mentions:
            return

        text = message.content
        list = text.split(' ')
        # remove the Botname from the text
        list.remove(BotID)

        if(len(list)!=0):
            command = list[0].lower()
        else:
            command = "help"

        if (command=="help"):
            await client.send_message(message.channel, "These are the different commands:\n "
                                                       "-> help: shows this screen\n"
                                                       "-> add + GAMENAME: adds the game to your setup\n"
                                                       "-> remove + GAMENAME: removes the game from your setup\n"
                                                       "-> getallgames: gets all the games and their owners\n"
                                                       "-> gameinfo + GAMENAME :gets the categories of a game \n"
                                                       "-> addcategory + CATEGORY +GAMENAME: adds a category to a game\n"
                                                       "-> play +@players: makes a list of all possible games, and my personal choice\n"
                                                       "-> play.help : gives extra explanaion about plays extra features\n"
                                                       "-> tts: gives all tts commands\n"
                                                       "-> settings: gives all changeable settings in commands")
        elif(command=="play.help"):
            await client.send_message(message.channel, "play has some postfixes:\n"
                                                       "help -A @players :only shows my choice, not all the options\n"
                                                       "help -C Category @players: shows all possible games within a category")

        elif(command =="tts"):
            await client.send_message(message.channel, "tts commands:\n"
                                                       "tts.add + GAMENAME: adds to all games in tts \n"
                                                       "tts.remove + GAMENAME: removes a game from tts\n"
                                                       "tts.play: pick a random game from tts\n"
                                                       "tts.all: shows a list of all games in tts")
        elif(command=="tts.add"):
            if(len(list)>=2):
                gamename = unsplit(list[1:])
                AddTTS(gamename)
                await client.send_message(message.channel, "Game "+gamename+ "added\n")
        elif(command=="tts.remove"):
            if (len(list) >= 2):
                gamename = unsplit(list[1:])

                RemoveTTS(gamename)
                await client.send_message(message.channel, "Game " + gamename + "removed\n")
        elif(command=="tts.play"):
            choices =PlayTTS()
            gamename = random.choice(choices)[0]

            await client.send_message(message.channel, "Game I picked = " + gamename)

        elif(command=='tts.all'):
            all = PlayTTS()
            string = "All games in tts:\n"
            for x in all:
                string+='- '+x[0]

            await client.send_message(message.channel, string)
        elif(command =="settings"):
            await client.send_message(message.channel, "settings:\n"
                                                       "settings.changename +NAME: changes your name in getallgames \n"
                                                       )
        elif(command=="add"):
            gamename = unsplit(list[1:])
            print(message.author.id)
            AddGame(gamename,message.author.id,message.author.name)
            await client.send_message(message.channel,gamename+"added to " +message.author.mention)

        elif(command=="remove"):
            gamename = unsplit(list[1:])
            RemoveGame(gamename,message.author.id,message.author.name)
            await client.send_message(message.channel, gamename + "removed from "+message.author.mention )
        elif(command=="play") :
            mentions = message.mentions
            if (len(list) >= 3 and list[1] == "-C"):
                cat = list[2]
                listmentions =getgames(mentions,cat.lower())
            else:
                listmentions = getgames(mentions)

            prettylist = makePrettyList(listmentions)

            if(len(prettylist[1])==0):
                prettylist[1].append("nothing")
            if(len(list )>=2 and list[1]=="-A"):
                await client.send_message(message.channel,
                                         "My Choice: \n" + random.choice(
                                              prettylist[1]))
            else:
                await client.send_message(message.channel, " Possible Games:\n" + prettylist[0]+"\n My Choice: \n" + random.choice(prettylist[1]))

        elif (command == "getallgames"):
            list = GetAllGames()
            await client.send_message(message.channel,
                                      " all Games:\n" + getAllgamesList(list) )

        elif(command == "addcategory"):
            if(len(list)>=3):
                category = list[1]
                gamename = unsplit(list[2:])

                bool = addCategory(gamename,category.lower())
                if(bool):
                    await client.send_message(message.channel,
                                              " SuccesFully added Category: " + category + " to " + gamename)
                else:
                    await client.send_message(message.channel,
                                              " Failed: no game " + gamename +" found")

        elif(command=="gameinfo"):
            if(len(list)>=2):
                gamename = unsplit(list[1:])
                list =getCategories(gamename)
                string = gamename+":\n"
                for i in list:
                    string+= '-'+i[0]+"\n"

                await client.send_message(message.channel,
                                          string)

        elif(command == "settings.changename"):
            if (len(list) >= 2):
                name = unsplit(list[1:])
                ChangeName(message.author.id,name)
                await client.send_message(message.channel,message.author.mention+ " changed his name to " +name)

        elif(command =="deleteplayer" and message.author==server.owner):
            mentions= message.mentions
            for x in mentions:
                if(x.name != BOTNAME):
                    RemovePlayer(x)

        elif (command == "addtoall" and message.author == server.owner):
            if (len(list) >= 2):
                name = unsplit(list[1:])
                addToAll(name)
                await client.send_message(message.channel,
                                          "Added "+ name+"to @everyone" )


        else:
            await client.send_message(message.channel,
                                      "No command recognised, use help to find a list of all commands")







        return

        # get the requested menus


        # force a menu update if nothing could be found initially



    client.run(TOKEN)


if __name__ == '__main__':
    run()
    
