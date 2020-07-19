import pymysql
import mysql.connector
from flask import jsonify
import configparser


def getConnection():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    db = mysql.connector.connect(
        host=config["UserManagement"]['MYSQL_DATABASE_HOST'],
        user=config["UserManagement"]['MYSQL_DATABASE_USER'],
        password=config["UserManagement"]['MYSQL_DATABASE_PASSWORD'],
        database = config["UserManagement"]['MYSQL_DATABASE_DB']
    )
    return db
    
def hasNumbers(s):
     return any(char.isdigit() for char in s)

def getAll():
    db = getConnection()
    mycursor = db.cursor(dictionary=True)


    mycursor.execute("select firstname,lastname,username,id,active from users")
    rows=mycursor.fetchall()
    resp = jsonify(rows)
    db.close()
    return resp

def get(col,val):
    try:
        db = getConnection()
        mycursor = db.cursor(dictionary=True)
        q = "select firstname,lastname,username,id,active from users where {} = %s".format(col)
        mycursor.execute(q,(val,))
        rows=mycursor.fetchall()
        resp = jsonify(rows)
        db.close()
        return resp
    except pymysql.err.InternalError:
        print("error")
        return("Invalid column entered")
    
def deleteUser(username):
    try:
        db = getConnection()
        mycursor = db.cursor(pymysql.cursors.DictCursor)
        q = "delete from users where username = %s"
        
        mycursor.execute(q,(username,))
        db.commit()
        db.close()
        return getAll()

    except pymysql.err.InternalError:
        print("error")
        return("Username does not exist")
    
def delete(col,val):
    try:
        db = getConnection()
        mycursor = db.cursor(pymysql.cursors.DictCursor)
        
        q = "delete from users where {} = %s".format(col)

        mycursor.execute(q,(val,))
        db.commit()
        db.close()
    
        return getAll()
    except pymysql.err.InternalError:
        print("error")
        return("Column does not exist")
    


def update(col,val,username):
    
    
    if col.lower()=='firstname':
        if (val.isalpha()==False):
            return "firstname can only contain letters"
        
    if col.lower()=='lastname':
        if (val.isalpha()==False):
            return "lastname can only contain letters"
    
    if col.lower()=='active':
        if (val!='1'and val!='0'):
            return "active can be 1 or 0"
    
        
    try:
        db = getConnection()
        mycursor = db.cursor(pymysql.cursors.DictCursor)
        q = "Update users set {} = %s where username = %s".format(col)
        mycursor.execute(q,(val,username))
        db.commit()
        db.close()
    
        return getAll()
    except pymysql.err.InternalError:
        print("error")
        return("Enter a valid column")
    except pymysql.err.ProgrammingError:
        print("error")
        return("Enter a valid column")
    except pymysql.err.IntegrityError:
        return("Invalid username value")



def updateAll(firstname,lastname,newusername,password,email,active,username):
    if not newusername:
        return("Username cant be empty")
    if active:
        if (active!='1'and active!='0'):
            return "active can be 1 or 0"
        
        
    try:
        db = getConnection()
        mycursor = db.cursor(pymysql.cursors.DictCursor)
        q = "Update users set firstname = %s,lastname = %s,username = %s ,password = %s,email= %s, active=%s where username = %s"
        mycursor.execute(q,(firstname,lastname,newusername,password,email,active,username))
    
        db.commit()
        db.close()
    
        return getAll()
        
    except pymysql.err.IntegrityError:
        return("Invalid value for new username") 
    
    
def create(firstname,lastname,username,password,email,active):
    if not username:
        return "Username cant be empty"
    if active:
        if (active!='1'and active!='0'):
            return "active can be 1 or 0"
    
    try:
        db = getConnection()
        mycursor = db.cursor(pymysql.cursors.DictCursor)
        q = "insert into users(Firstname,Lastname,Username,Password,Email,Active) values(%s,%s,%s,%s,%s,%s)"
        mycursor.execute(q,(firstname,lastname,username,password,email,active))
        db.commit()
        db.close()

        return getAll()
    except pymysql.err.IntegrityError:
        return("Invalid value for username")
    except pymysql.err.InternalError:
        return("Invalid value for active")
    
    
def usernameContains(word):
    db = getConnection()
    mycursor = db.cursor(dictionary=True)
    q = "Select firstname,lastname,username,id,active from users Where Username like '%{}%' ".format(word)
    mycursor.execute(q)
    rows=mycursor.fetchall()
    resp = jsonify(rows)
    db.close()
    return resp



def getActiveUsers():
    db = getConnection()
    mycursor = db.cursor(dictionary=True)
    mycursor.execute("select firstname,lastname,username,id,active from users where active > 0")
    rows=mycursor.fetchall()
    resp = jsonify(rows)
    db.close()
    return resp


def getInactiveUsers():
    db = getConnection()
    mycursor = db.cursor(dictionary=True)
    mycursor.execute("select firstname,lastname,username,id,active from users where active <= 0")
    rows=mycursor.fetchall()
    resp = jsonify(rows)
    db.close()
    return resp

def getAllGroups():
    db = getConnection()
    mycursor = db.cursor(dictionary=True)

    mycursor.execute("select name from GroupsList")
    rows=mycursor.fetchall()
    resp = jsonify(rows)
    db.close()
    return resp

def createGroup(name):
    if not name:
        return "Group name cant be empty"
    try:
        db = getConnection()
        mycursor = db.cursor(pymysql.cursors.DictCursor)
        q = "create table {} (Id int NOT NULL AUTO_INCREMENT, Username varchar(255) UNIQUE not null, permission ENUM('Admin', 'member', 'viewer', 'collaborator') default 'member', primary key(ID), foreign key(Username) references Users(Username))".format(name)
        q2 = "insert into GroupsList(name) values(%s)"
        mycursor.execute(q2,(name,))
        mycursor.execute(q)
    
        db.commit()
        db.close()
        return getAllGroups()
    except pymysql.err.IntegrityError:
        return("Invalid value for groupname")
    except pymysql.err.InternalError:
        return("Invalid value for groupname")
    except pymysql.err.ProgrammingError:
        print("error")
        return("Invalid value for groupname")
    

def getAllFromGroup(name):
    db = getConnection()
    mycursor = db.cursor(pymysql.cursors.DictCursor)
    q = "Select Id, Username, Permission from {}".format(name)
    mycursor.execute(q)
    rows=mycursor.fetchall()
    resp = jsonify(rows)
    db.close()
    return resp


def getAllUserGroups(username):

    db = getConnection()
    mycursor = db.cursor(dictionary=True)
    mycursor.execute("Select name from GroupsList")
    rows=mycursor.fetchall()
    g = []
    f = []
    for row in rows:
        
        g.append(row['name'])
    for group in g:
        res = {}
        q =  "select permission from {} where username = %s".format(group)
        mycursor.execute(q,(username,))
        re = mycursor.fetchall()
        
        if re:
            
            res[group] = re[0]['permission']
            f.append(res)
            
    
    
    resp = jsonify(f)
    db.close()
    return resp

    

def addUserToGroup(groupname,username,permission):
    if not groupname:
        return "Group name cant be empty"
    if not username:
        return "username cant be empty"
    if permission:
        if (permission.lower()!='admin'and permission.lower()!='member' and permission.lower()!='viewer' and permission.lower()!='collaborator'):
                return "permission can only be set to admin, member, viewer, or collaborator"
    
    try:
        db = getConnection()
        mycursor = db.cursor(pymysql.cursors.DictCursor)
        q = "insert into {} (username,permission) values (%s,%s)".format(groupname)
        mycursor.execute(q,(username,permission))
        db.commit()
        db.close()
        return getAllFromGroup(groupname)
    except pymysql.err.IntegrityError:
        return("Invalid value for username")
    except pymysql.err.InternalError:
        return("Invalid values entered")
    except pymysql.err.ProgrammingError:
       
        return("Invalid values entered")



def getPermissionInGroup(groupname,permission):
    try:
        db = getConnection()
        mycursor = db.cursor(pymysql.cursors.DictCursor)
        q = "select Id,Username,permission from {} where permission = %s".format(groupname)
        mycursor.execute(q,(permission,))
        rows=mycursor.fetchall()
        resp = jsonify(rows)
        db.close()
        return resp
    except pymysql.err.ProgrammingError:       
        return("enter valid groupname and permission")