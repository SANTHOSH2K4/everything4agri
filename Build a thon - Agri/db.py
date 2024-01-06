import sqlite3

conn=sqlite3.connect('everything4agri.db')
c=conn.cursor()

#c.execute("create table users(name text,email text,password text)")

#c.execute("insert into users values('santhosh','santhosh2k495@gmail.com','1234')")
c.execute("select *from users")
li=c.fetchall()
uname=[]
email=[]
pw=[]
for i in range(0,len(li)):
    uname.append(li[i][0])
    email.append(li[i][1])
    pw.append(li[i][2])
print(uname)
print(email)
print(pw)
var=tarun@gmail.com
if var in email:
    print("yes")
else:
    print("no")

print(li[1][0])
