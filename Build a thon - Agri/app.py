import pickle
import numpy as np
from flask import Flask,request,render_template,redirect,url_for
import os
import tensorflow as tf
import numpy as np
from tensorflow import keras
from skimage import io
from tensorflow.keras.preprocessing import image
import sqlite3
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
conn=sqlite3.connect('everything4agri.db')

us_name=[]
app=Flask(__name__)

with open("crop_model.pkl","rb") as f:
     crop_model=pickle.load(f)


model =tf.keras.models.load_model('PlantDNet.h5',compile=False)




def model_predict(img_path, model):
    img = image.load_img(img_path, grayscale=False, target_size=(64, 64))
    show_img = image.load_img(img_path, grayscale=False, target_size=(64, 64))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = np.array(x, 'float32')
    x /= 255
    preds = model.predict(x)
    return preds


@app.route('/disease_pred', methods=['GET'])
def diseasepred():
    # Main page
    return render_template('disease_pred.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)
        print(preds[0])

        # x = x.reshape([64, 64]);
        disease_class = ['Pepper__bell___Bacterial_spot', 'Pepper__bell___healthy', 'Potato___Early_blight',
                         'Potato___Late_blight', 'Potato___healthy', 'Tomato_Bacterial_spot', 'Tomato_Early_blight',
                         'Tomato_Late_blight', 'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot',
                         'Tomato_Spider_mites_Two_spotted_spider_mite', 'Tomato__Target_Spot',
                         'Tomato__Tomato_YellowLeaf__Curl_Virus', 'Tomato__Tomato_mosaic_virus', 'Tomato_healthy']
        a = preds[0]
        ind=np.argmax(a)
        print('Prediction:', disease_class[ind])
        result=disease_class[ind]
        return result
    return None

@app.route('/crop_predict',methods=['POST','GET'])
def click():
    with open("crop_model.pkl","rb") as f:
        crop_model=pickle.load(f)
    a=float(request.form['nitrogen'])
    b=float(request.form['phosphorus'])
    c=float(request.form['potassium'])
    d=float(request.form['potassium'])
    e=float(request.form['temperature'])
    f=float(request.form['humidity'])
    g=float(request.form['ph'])
    x_test=[[a,b,c,d,e,f,g]]
    # Predict labels for test data
    y_pred = crop_model.predict(x_test)
    res="Proffitable crop : "+y_pred[0]
    print(res)


    return render_template("crop.html",pred=res)

@app.route('/crop_recmnd')
def crop_recmnd():
    return render_template("crop.html")

@app.route('/')
def logreg():
    return render_template("login.html",alert="",pwalert="")

@app.route('/log',methods=['POST','GET'])
def home():
    conn=sqlite3.connect('everything4agri.db')
    a=request.form['em_log'].strip()
    b=request.form['pw_log'].strip()
    uname=[]
    email=[]
    pw=[]
    
    cur=conn.cursor()    
    cur.execute("select *from users")
    li=cur.fetchall()
    for i in range(0,len(li)):
        uname.append(li[i][0])
        email.append(li[i][1])
        pw.append(li[i][2])
    

    if a not in email:
        return render_template("login.html",alert="\nUser not found!\n")
    else:
        n=email.index(a)
        if b!=pw[n]:
            return render_template("login.html",pwalert="\nwrong password!\n")
        else:
            tmp=cur.execute("select name from users where email='{}'".format(a))
            tmp=tmp.fetchone()[0]
            us_name.append(tmp)
            cur.execute("update username set uname_soln='{}'".format(tmp))
            conn.commit()
            return render_template("home.html")
        
@app.route('/search',methods=['POST','GET'])
def search():
    a=request.form['strcont'].strip()
    a=a.lower()
    conn=sqlite3.connect('everything4agri.db')
    cur=conn.cursor()
    li=cur.execute("select *from community")
    li=li.fetchall()
    li_id=[]
    li_uname=[]
    li_subject=[]
    li_content=[]
    li_soln=[]
    for i in li:
        li_id.append(i[0])
        li_uname.append(i[1].lower())
        li_subject.append(i[2].lower())
        li_content.append(i[3].lower())
        li_soln.append(i[4].lower())
    comm=[]
    i_li=[]
    for i in range(len(li_content)):
        if a in li_content[i]:
            i_li.append(i)
            print("Substring found in element", i)
            
            comm.append((li_id[i],li_uname[i],li_subject[i],li_content[i],li_soln[i]))

    
    for i in range(len(li_subject)):
        if a in li_subject[i]:
            i_li.append(i)
            print("Substring found in element", i)
            
            comm.append((li_id[i],li_uname[i],li_subject[i],li_content[i],li_soln[i]))

    
    for i in range(len(li_soln)):
        if a in li_soln[i]:
            i_li.append(i)
            print("Substring found in element", i)
            
            comm.append((li_id[i],li_uname[i],li_subject[i],li_content[i],li_soln[i]))
    
    
    return render_template("community.html",community=comm)






@app.route('/reg',methods=['POST','GET'])
def reg():
    conn=sqlite3.connect('everything4agri.db')
    a=request.form['nm_reg'].strip()
    b=request.form['em_reg'].strip()
    c=request.form['pw_reg']
    print(a,b,c)
    
    cur=conn.cursor()
    cur.execute("insert into users values('{}','{}','{}')".format(a,b,c))
    conn.commit()
    cur.execute("select *from users")
    
    li=cur.fetchall()
    print(li)
    return render_template("login.html",alert="",pwalert="")

@app.route('/community')
def comm():
    conn=sqlite3.connect('everything4agri.db')
    cur=conn.cursor()
    li=cur.execute("select *from community order by id desc")

    return render_template("community.html",community=li,user_id=1)

@app.route('/home')
def index():
    return render_template("home.html")

@app.route('/sol/<int:id>')
def sol(id):
    return render_template("soln1.html",slid=id)

@app.route('/soladd/<int:sid>',methods=['POST','GET'])
def sol2(sid):
    slid=sid
    a=request.form['soln']
    conn=sqlite3.connect('everything4agri.db')
    cur=conn.cursor()
    solli = cur.execute("SELECT uname FROM community WHERE id={}".format(slid))
    result = solli.fetchone()
    res=cur.execute("select *from username")
    res=res.fetchone()[0]
    unm=cur.execute("select soln from community where id={}".format(slid))
    result=unm.fetchone()
    result=result[0]
    result+="\n"
    result+=res
    result+=" :"
    result+=a
    cur.execute("update community set soln='{}' where id={}".format(result,slid))
    conn.commit()
    cur.execute("select *from community order by id desc")
    li=cur.fetchall()
    print(li)

    id_con=cur.execute("select * from users")
    id_con=id_con.fetchall()
    name=[]
    for i in id_con:
        name.append(i[0])
    print(name)
    n_id=name.index("santhosh")+1    

    return render_template("community.html",community=li,sid=slid,user_id=n_id)

@app.route('/addprob/<int:id>', methods=['GET','POST'])
def topost(id):
    return render_template("post.html",sid=id)



@app.route('/post2/<int:sid>', methods=['GET','POST'])
def topost2(sid):
    slid=sid
    a=request.form['post_sub']
    b=request.form['post_content']
    conn=sqlite3.connect('everything4agri.db')
    cur=conn.cursor()
    solli = cur.execute("SELECT name FROM users ")
    result = solli.fetchone()[0]
    cur.execute("insert into community(uname,subject,content,soln) values('{}','{}','{}','')".format(us_name[0],a,b))
    conn.commit()

    li=cur.execute("select *from community order by id desc")

    return render_template("community.html",community=li)

@app.route('/smart')
def smart():
    conn=sqlite3.connect('everything4agri.db')
    c=conn.cursor()
    li=c.execute("select watering from water")
    result=int(li.fetchone()[0])
    return render_template("smart.html",wtr=result)

@app.route('/water')
def changewatering():
    conn=sqlite3.connect('everything4agri.db')
    c=conn.cursor()

    li=c.execute("select watering from water")
    result=int(li.fetchone()[0])

    print(result)

    if result==0:
        c.execute('update water set watering=1')
        conn.commit()
        li=c.execute("select watering from water")
        result_wtr=int(li.fetchone()[0])

    if result==1:
        c.execute('update water set watering=0')
        conn.commit()
        li=c.execute("select watering from water")
        result_wtr=int(li.fetchone()[0])

    return render_template("smart.html",wtr=result_wtr)


    


if __name__=="__main__":
    app.run()

