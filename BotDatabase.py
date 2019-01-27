import datetime
import itertools
import logging
import os
import re
import sqlite3
import tempfile
import urllib.parse
import discord

import dateparser
import lxml.html
import pdfquery
import requests


# disable low-level pdfminer logging
logging.getLogger('pdfminer').setLevel(logging.WARNING)

databasename = "Gaming.db"
BOTNAME = "GameBot"



def intersect(listofLists):
    instersection =[]
    if len(listofLists)!=0:
        for obj in listofLists[0]:
            bool =True
            for list in listofLists:
                bool2 = False
                for obj2 in list:
                    if obj == obj2:
                        bool2=True
                        break
                if not bool2:
                    bool = False
                    break
            if(bool):
                instersection.append(obj)
    return instersection

def InsertUser(playerID,playerName, conn):
    c = conn.cursor()
    c.execute('SELECT DiscordID FROM peoplez WHERE  DiscordID =?', [playerID])
    list = c.fetchall()
    if (len(list) == 0):

        c.execute('INSERT INTO peoplez VALUES (?,?)', [playerID, playerName])

    conn.commit()

def addToAll(gameName):
    conn = sqlite3.connect(databasename)
    c = conn.cursor()
    c.execute('SELECT gameID FROM gamz WHERE  gameName =?', [gameName])
    list = c.fetchall()
    if(len(list)==0):
        c.execute('INSERT INTO gamz(gameName) VALUES (?)', [gameName])
        c.execute('SELECT gameID FROM gamz WHERE  gameName =?', [gameName])
        list = c.fetchall()
    gameID=list[0][0]
    c.execute('SELECT DISTINCT DiscordID FROM peoplez')
    list=c.fetchall()
    for x in list:
        if not GameLookup(gameID, x[0],conn):
            c.execute('INSERT INTO plays(DiscordID,gameID) VALUES (?,?)', [x[0],gameID])

    conn.commit()
    conn.close()
    return list

def printall():
    conn = sqlite3.connect(databasename)

    c = conn.cursor()
    c.execute('SELECT gameName FROM gamz')
    list = c.fetchall()

    conn.commit()
    conn.close()
    return list

def ChangeName(DiscordID, NewName):
    conn = sqlite3.connect(databasename)

    InsertUser(DiscordID, NewName, conn)
    c = conn.cursor()
    c.execute('UPDATE peoplez SET playerName=? WHERE DiscordID = ?', [NewName,DiscordID])
    conn.commit()
    conn.close()


def GameLookup(gameID,DiscordID,conn):
    c = conn.cursor()
    c.execute('SELECT * FROM plays WHERE gameID=? AND DiscordID=? ',[gameID,DiscordID])
    list = c.fetchall()
    if(len(list)==0):
        return False
    return True

def addCategory(gameName, category):
    conn = sqlite3.connect(databasename)

    c = conn.cursor()
    c.execute('SELECT gameID FROM gamz WHERE gameName=?',[gameName])
    listGame = c.fetchall()
    if(len(listGame)==0):
        return False

    c.execute('SELECT catID FROM categories WHERE catName=?',[category])
    list = c.fetchall()
    if(len(list)==0):
        c.execute('INSERT INTO categories (catName) VALUES(?)',[category])
        c.execute('SELECT catID FROM categories WHERE catName=?', [category])
        list = c.fetchall()
    catID = list[0][0]
    GameID= listGame[0][0]
    c.execute('SELECT catID FROM gameCategory WHERE catID=? AND gameID=?',(catID,GameID))
    list= c.fetchall()
    if(len(list)==0):
        c.execute('INSERT INTO gameCategory (catID,gameID) VALUES(?,?)',(catID,GameID))
    conn.commit()
    conn.close()
    return True


def getgames(members, category="all"):
    if(len(members)==1):
        return []
    conn = sqlite3.connect(databasename)
    c=conn.cursor()
    category=category.lower()
    list =[]

    Varlist = []
    executable= 'SELECT DISTINCT gameName, gameID FROM plays p NATURAL JOIN gamz g '
    if(category!= 'all'):
        Varlist.append(category)
        executable+= 'NATURAL JOIN gameCategory NATURAL JOIN categories c WHERE c.catName = ? AND EXISTS( SELECT * FROM'

    else:
        executable+='WHERE EXISTS( SELECT * FROM'


    string2 = ' WHERE '
    string3 ='AND '

    for i in range (len(members)):
        if(members[i].name!= BOTNAME):

            InsertUser(members[i].id,members[i].name, conn)

            executable+= ' plays p'+str(i)+","

            string2+='p.gameID=p'+str(i)+'.gameID AND '
            string3+='p'+str(i)+'.DiscordID=? AND '

            Varlist.append(members[i].id)


    executable=executable[0:-1]
    string2=string2[0:-4]
    string3=string3[0:-4]
    executable+=string2+string3
    executable+=')'


    c.execute(executable, Varlist)
    list = c.fetchall()

    # inter = intersect(list)
    conn.commit()
    conn.close()

    return list
def RemoveGame(game,playerID, playerName):
    conn = sqlite3.connect(databasename)

    InsertUser(playerID, playerName, conn)

    c = conn.cursor()
    c.execute('SELECT gameID FROM gamz WHERE gameName =?', [game])
    list2 = c.fetchall()
    if (len(list2) != 0):
        c.execute('DELETE FROM plays WHERE gameID=? AND DiscordID=?',[list2[0][0],playerID])

        c.execute('SELECT * FROM plays WHERE gameID=?',[list2[0][0]] )
        list3 =c.fetchall()
        if(len(list3)==0):
            c.execute('DELETE FROM gamz WHERE gameID=?',[list2[0][0]])
            c.execute('DELETE FROM gameCategory WHERE gameID=?',[list2[0][0]])
        conn.commit()
        conn.close()
        return True
    conn.commit()
    conn.close()
    return False

def RemovePlayer(member):
    conn = sqlite3.connect(databasename)
    InsertUser(member.id,member.name,conn)
    c = conn.cursor()
    c.execute('DELETE FROM plays WHERE  DiscordID=?', [member.id])
    c.execute('DELETE FROM peoplez WHERE DiscordID=?', [member.id])

    conn.commit()
    conn.close()


def GetAllGames():
    conn = sqlite3.connect(databasename)

    c = conn.cursor()
    #
    c.execute('SELECT DISTINCT gameName, playerName FROM peoplez peo NATURAL JOIN plays p NATURAL JOIN gamz g ORDER BY gameName')
    list = c.fetchall()



    conn.commit()
    conn.close()
    return list

def AddTTS(gamename):
    conn = sqlite3.connect(databasename)

    c = conn.cursor()
    c.execute('INSERT INTO Tabletop(gameName) VALUES(?)',[gamename] )
    conn.commit()
    conn.close()

def RemoveTTS(gamename):
    conn = sqlite3.connect(databasename)

    c = conn.cursor()
    c.execute('DELETE FROM Tabletop WHERE gameName=?', [gamename])
    conn.commit()
    conn.close()

def PlayTTS():
    conn = sqlite3.connect(databasename)

    c = conn.cursor()
    c.execute('SELECT gameName FROM Tabletop')
    list = c.fetchall()
    conn.commit()
    conn.close()
    return list

def getCategories(gameName):
    conn = sqlite3.connect(databasename)

    c = conn.cursor()
    c.execute(
        'SELECT DISTINCT catName'
        ' FROM gamz g NATURAL JOIN gameCategory NATURAL JOIN categories WHERE g.gameName=?',[gameName])
    list =  c.fetchall()
    conn.commit()
    conn.close()
    return list

def AddGame(game ,playerID,playerName):
    """
    Add the game to the player in database
    """
    conn = sqlite3.connect(databasename)

    InsertUser(playerID,playerName,conn)

    c = conn.cursor()


    c.execute('SELECT gameID FROM gamz WHERE gameName =?', [game])
    list2 = c.fetchall()
    if(len(list2)==0):
        c.execute('INSERT INTO gamz (gameName) VALUES (?)', [game])
        c.execute('SELECT gameID FROM gamz WHERE gameName =?', [game])
        list2 = c.fetchall()

    if not GameLookup(list2[0][0],playerID, conn):
        c.execute('INSERT INTO plays (gameID,DiscordID) VALUES(?,?)',[list2[0][0],playerID])


    conn.commit()
    conn.close()


def init_database():
    """
    Initialize the database.

    The database contains 3 tables peaple and their discord id, gamz, games and a given ID, and plays which links the 2`.
    """
    conn = sqlite3.connect(databasename)
    c = conn.cursor()

    c.execute('CREATE TABLE peoplez ( DiscordID VARCHAR(18) NOT NULL , playerName VARCHAR(30),PRIMARY KEY (DiscordID));')
    c.execute('CREATE TABLE gamz( gameID INTEGER PRIMARY KEY AUTOINCREMENT , gameName VARCHAR(100));')

    c.execute("""CREATE TABLE plays(
    gameID INTEGER REFERENCES gamz(gameID),
    DiscordID VARCHAR(18) REFERENCES peoplez(DiscordID),
    PRIMARY KEY (gameID,DiscordID));
    """)

    c.execute('CREATE TABLE categories(catID INTEGER PRIMARY KEY AUTOINCREMENT, catName VARCHAR(30) )')
    c.execute('CREATE TABLE gameCategory(gameID INTEGER REFERENCES gamz(gameID),catID INTEGER REFERENCES categories(catID), PRIMARY KEY(gameID,catID))')

    c.execute('CREATE TABLE Tabletop(gameName VARCHAR(30) primary KEY)')

    conn.commit()
    conn.close()

class DatabaseUpdate:

    def run(self):
        # create the database if needed

        if not os.path.exists(databasename):
            init_database()

         # expects an iterable
        return []
