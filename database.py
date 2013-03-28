import sqlite3 as sql 
import os, errno

def buildListingDb(config) :
  dbPath = config.get('database', 'path')
  dbName = config.get('database', 'name')
  print("[I] Creating db in {0}".format(dbPath))
  try :
    os.makedirs(dbPath) 
  except OSError as exception :
    if exception.errno != errno.EEXIST :
      raise 
  if dbName != ":memory:" :
    db = sql.connect(os.path.join(dbPath, dbName))
  else :
    db = sql.connect(dbName)

  db = initializeDb(db)
  db = populateDB(config, db)
  return db

def initializeDb(db) :
  # It should be create every time.
  c = db.cursor()
  query = 'DROP TABLE IF EXISTS listings'
  c.execute(query)

  query = ''' CREATE TABLE listings (
            name VARCHAR NOT NULL 
            , owner VARCHAR 
            , root VARCHAR NOT NULL 
            , type VARCHAR
            , size INT NOT NULL 
            , lines INT 
            , status VARCHAR
            , PRIMARY KEY(root, name))'''
  c.execute(query)

  query = '''CREATE TABLE IF NOT EXISTS match (
            userA VARCHAR NOT NULL 
            , fileA VARCHAR NOT NULL
            , userB VARCHAR NOT NULL
            , fileB VARCHAR NOT NULL 
            , match REAL NOT NULL 
            , algorithm VARCHAR 
            , result VARCHAR
            , PRIMARY KEY(fileA, fileB, algorithm))
            '''
  c.execute(query)

  c.execute('DROP TABLE IF EXISTS comparisons')
  query = '''CREATE TABLE IF NOT EXISTS comparisons (
    userA VARCHAR NOT NULL
    , userB VARCHAR NOT NULL 
    , file VARCHAR NOT NULL 
    , severity VARCHAR NOT NULL) '''
  c.execute(query)

  db.commit()
  return db


def populateDB(config, db) :
  import re
  c = db.cursor()
  dir = config.get('source', 'dir')
  regex = config.get('source', 'regex')
  if len(regex.strip()) == 0 :
    regex = ".*"
  pat = re.compile(regex, re.IGNORECASE)
  if not os.path.exists(dir) :
    print("[E] source dir does not exists. Check config file.")
    sys.exit(0)
  countFile = 0
  for root, dirs, files in os.walk(dir) :
    for file in files :
      if pat.match(file) :
        countFile += 1
        fileName = file 
        filePath = os.path.join(root, file)
        if not os.path.exists(filePath) :
          print("[W] Something weired has happened. {0} does not \
              exists".format(filePath))
          return 
        sizeOfFile = os.path.getsize(filePath)
        owner = root.replace(dir, "")
        owner = owner.strip("/")
        owner = owner.split("/")[0]
        query = '''INSERT INTO listings (name, root, size, type, owner)
            VALUES (?, ?, ?, ?, ?)'''
        c.execute(query, (fileName, root, sizeOfFile, regex, owner))
  db.commit()
  print("[I] Total {0} programs".format(countFile))
  return db 

def writeContent(config, db) :
  path = config.get('database', 'path')
  srcdir = config.get('source', 'dir')
  srcdir = srcdir.strip("/")
  srcdir += "/"
  name = config.get('database', 'name')
  dbPath = os.path.join(path, name)
  if name == ":memory:" : 
    print("[I] Loading db from memory dump ")
    dbPath = os.path.join(path, "sniffer.sqlite3")
    db = sqlite.connect("")
    db.execute('.read {0}'.format(dbPath))

  db = sql.connect(dbPath)
  c = db.cursor()
  serverity = ["mild", "moderate", "high", "veryhigh", "identical"]
  for s in serverity :
    print("Fetching cases with serverity : {0}".format(s))
    query = '''SELECT userA, userB, fileA, fileB, match FROM match WHERE result=?'''
    with open(os.path.join(path, s+"_serverity.csv"), "w") as f :
      for row in c.execute(query, (s,)) :
        userA, userB, fileA, fileB, match = row 
        fileA = fileA.replace(srcdir, "").strip("/")
        fileB = fileB.replace(srcdir, "").strip("/")
        f.write("\"{0}\",\"{1}\",\"{2}\"\n".format(match,fileA, fileB))


def dump(config, db) :
  path = config.get('database', 'path')
  name = config.get('database', 'name')
  if name == ":memory:" :
    print("[I] Dumping the in memory database to a file : {0}".format(fileToDump))
    # dump it 
    fileToDump = os.path.join(path, "sniffer.sqlite3")
    with open(fileToDump, 'w') as f :
      for line in db.iterdump() :
        f.write('%s\n' % line)
  else : return 


def generateVisual(config, db) :  
  import networkx as nx
  c = db.cursor()
  query = '''SELECT DISTINCT userA FROM match'''
  print("[DB] Fetching distinct first users ..."),
  userAs = c.execute(query).fetchall()
  print("done")
  
  print("[DB] Fetching distinct second users ..."),
  query = '''SELECT DISTINCT userB FROM match'''
  userBs = c.execute(query).fetchall()
  print("done")

  print("Generating information for each pair of students ... "),
  query = '''SELECT fileA, fileB, match FROM match WHERE userA=? AND
      userB=?'''
  nodes = list()
  for userA in userAs :
    for userB in userBs :
      res = c.execute(query, (userA[0], userB[0],)).fetchall()
      nodes.append(res)
  print("done")

  

