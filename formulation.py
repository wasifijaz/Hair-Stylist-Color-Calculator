import pymysql
from flask import Flask, request, render_template, flash
from werkzeug.utils import secure_filename
import pandas as pd
import os
from fractions import Fraction
import logging
import sys
import re 

logging.basicConfig(filename='error.log', level=logging.DEBUG)


app = Flask(__name__)

HOST = "YOUR_HOST"
PORT = YOUR_PORT
USER = "YOUR_USER"
PASSWORD = "YOUR_PASS"
DATABASE = "YOUR_DB"
ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/match/createtable', methods=("POST", "GET"))
def create_table():
    mydb = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASSWORD, database=DATABASE)
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', message="No file selected!")
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', message="No file selected!")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = os.path.splitext(filename)[0]
            
            df = pd.read_csv(request.files.get('file'))
            dbcol, pk, i, colList = "", "", 0, []
            for col in df.columns:
                col = col.lower()
                col = col.rstrip()
                col = col.replace(" ", "_")
                if i == 0:
                    dbcol += col + " VARCHAR(255) NOT NULL, "
                    pk = col
                else:
                    dbcol += col + " VARCHAR(255), "
                colList.append(col)
                i += 1

            dbcol += "PRIMARY KEY (" + pk + ")"
            
            mycursor = mydb.cursor()
            mydb.ping()
            mycursor.execute("CREATE TABLE " + filename + " (" + dbcol + ")")
            
            cols = "`,`".join(colList)

            for i,row in df.iterrows():
                logging.debug(row)
                sql = "INSERT INTO " + filename + " (`" + cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
                mydb.ping()
                mycursor.execute(sql, tuple(row))
                mydb.commit()

            return render_template('upload.html', message="File is uploaded Successfully!")
        else:
            return render_template('upload.html', message="Invalid CSV file!")
        mydb.close()
    return render_template('upload.html')


@app.route('/match/viewdata/<tablename>')
def view_table_data(tablename):
    mydb = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASSWORD, database=DATABASE)
    sql = "SELECT * FROM `" + tablename + "`"
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    
    result = mycursor.fetchall()
    for i in result:
        print(i)
    mycursor.close()
    mydb.close()

    return str(result)


@app.route('/match/droptable/<tablename>')
def drop_table(tablename):
    mydb = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()
    mycursor.execute("DROP TABLE " + tablename )
    mycursor.close()
    mydb.close()

    return "Table Dropped"


@app.route('/match/getmatch/<origin>/<desired>/<unit>/<quantity>/<colorcode>')
def get_color_match(origin,desired,unit,quantity,colorcode):
    old_stdout = sys.stdout
    log_file = open("flask.log","w")
    sys.stdout = log_file


    colorcode = colorcode.replace("_","/")
    colorcode = colorcode.replace("[","")
    colorcode = colorcode.replace("]","")
    colorcode = colorcode.strip()
    colorcode = colorcode.split(",")

    quantity = quantity.replace("_","/")
    quantity = quantity.replace("[","")
    quantity = quantity.replace("]","")
    quantity = quantity.strip()
    quantity = quantity.split(",")
    
    tablename = ""

    if origin == "aveda_full_spectrum":
        tablename = "aveda_full_spectrum"
    if origin == "chi_ionic":
        tablename = "chi_ionic"
    if origin == "framesi_2001":
        tablename = "framesi_2001"
    if origin == "goldwell_colorance":
        tablename = "goldwell_colorance"
    if origin == "goldwell_topchic":
        tablename = "goldwell_topchic"
    if origin == "igora_royal":
        tablename = "igora_royal"
    if origin == "kenra":
        tablename = "kenra"
    if origin == "loreal_inoa":
        tablename = "loreal_inoa"
    if origin == "majirel" and (desired == "pm_the_color" or desired == "pravana_chromasilk" or desired == "joico_lumishine" or desired == "fram_2001"):
        tablename = "majirel1"
    if origin == "majirel" and (desired == "wella_koleston"):
        tablename = "Majirel"
    if origin == "matrix_socolor":
        tablename = "Matrix_SoColor"
    if origin == "matrix_socolor_insider":
        tablename = "Matrix_SoColor_Insider"
    if origin == "paul_mitchell_the_color":
        tablename = "Paul_Mitchell_The_Color"
    if origin == "pm_xg":
        tablename = "pm_xg"
    if origin == "redken_chromatics":
        tablename = "redken_chromatics"
    if origin == "redken_color_fusion" and (desired == "joico_lumishine" or desired == "joico_verocolor" or desired == "paul_mitchell_the_color" or desired == "paul_mitchell_the_color_xg" or desired == "framesi_fram_colour" or desired == "wella_koleston" or desired == "wella_color_perfect" or desired == "matrix_so_color" or desired == "goldwell_tophic" or desired == "chi_ionic" or desired == "schwartzkopf_igora" or desired == "loreal_majirel" or desired == "kenra" or desired == "pravana_chromasilk" or desired == "framesi_framcolor_2001"):
        tablename = "Redken_Color_Fusion"
    if origin == "redken_color_fusion1" and (desired == "kenra_color_pf" or desired == "schwarzkopf_igora" or desired == "kenra_color_permanent_formulation"):
        origin = "redken_color_fusion"
        tablename = "Redken_Color_Fusion1"
    if origin == "redken_cover_fusion":
        tablename = "Redken_Cover_Fusion"
    if origin == "redken_gel_lacquers":
        tablename = "Redken_Gel_Lacquers"
    if origin == "redken_shades_eq_cream":
        tablename = "Redken_Shades_EQ_Cream"
    if origin == "schwarzkopf_igora":
        tablename = "Schwarzkopf_Igora"
    if origin == "shades_eq_liquid":
        tablename = "shades_eq_liquid"
    if origin == "wella_color_touch":
        tablename = "wella_color_touch"
    if origin == "wella_koleston":
        tablename = "wella_koleston"
    if origin == 'actyva':
        tablename = "actyva"
    if origin == 'alfa_parf':
        tablename = 'alfa_parf'
    if origin == 'enamels':
        tablename = 'enamels'
    if origin == 'it_ly':
        tablename = 'it_ly'
    if origin == 'tocco_magico':
        tablename = 'tocco_magico'
    if origin == 'nexxus_aloxxi':
        tablename = 'nexxus_aloxxi'
    if origin == 'keune_tinta':
        tablename = 'keune_tinta'    

    results = []

    mydb = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASSWORD, database=DATABASE)
    
    for idx,code in enumerate(colorcode):
        try:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT " + desired + " FROM " + tablename + " WHERE " + origin + "='" +  code + "'")
            codes = mycursor.fetchall()[0][0]

            mycursor.execute("SELECT " + desired + "_composition FROM " + tablename + " WHERE " + origin + "='" +  code + "'")
            comp = mycursor.fetchall()[0][0]
        except Exception:
            return "Invalid Arguements"
        
        # codes = codes.replace(" or ",",")
        codes = codes.split("&")
        comp = comp.split("&")
        print(codes)
        temp = []
        for i in range(0,len(codes)):
            if unit == "oz":
                oz = float(Fraction(comp[i]))
                quan = float(Fraction(quantity[idx]))
                # result = str(round(oz*quan, 2)) + "oz " + codes[i]
                result = round(oz*quan, 2)
            if unit == "g":
                oz = float(Fraction(comp[i]))
                quan = float(Fraction(quantity[idx]))
                grams = round(oz * 28.35, 2)
                # result = str(round(grams*quan, 2)) + "g " + codes[i]
                result = round(grams*quan, 2)
            if unit == "cc":
                oz = float(Fraction(comp[i]))
                quan = float(Fraction(quantity[idx]))
                cc = round(oz * 29.57,2)
                # result = str(round(cc*quan, 2)) + "cc " + codes[i]
                result = round(cc*quan, 2)
            if unit == "pt":
                oz = float(Fraction(comp[i]))
                quan = float(Fraction(quantity[idx]))
                pt = Fraction(round(oz/16,2)).limit_denominator()
                # result = str(round(pt*quan, 2)) + "pt " + codes[i]
                result = round(pt*quan, 2)
            
            temp.append(result)

        if unit == "oz":
            # temp = [round((value * 2) / sum(temp), 2) if sum(temp) != 0 else 0 if value != 0 else 0 for value in temp]
            temp = [str(temp[i]) + 'oz ' + codes[i] for i in range(len(temp))]
        if unit == "g":
            # temp = [round((value * 56.70) / sum(temp), 2) if sum(temp) != 0 else 0 if value != 0 else 0 for value in temp]
            temp = [str(temp[i]) + 'g ' + codes[i] for i in range(len(temp))]
        if unit == "cc":
            # temp = [round((value * 59.15) / sum(temp), 2) if sum(temp) != 0 else 0 if value != 0 else 0 for value in temp]
            temp = [str(temp[i]) + 'cc ' + codes[i] for i in range(len(temp))]
        if unit == "pt":
            # temp = [round((value * 32) / sum(temp), 2) if sum(temp) != 0 else 0 if value != 0 else 0 for value in temp]
            temp = [str(temp[i]) + 'pt ' + codes[i] for i in range(len(temp))]

        result = ' & '.join(temp)
        results.append(result)
        mycursor.close()
    mydb.close()
    
    values = []
    # print(colorcode)
    print(results)
    for item in results:
        if unit == "oz":
            matches = re.findall(r'\d+\.\d+(?=oz)', item)
        if unit == "g":
            matches = re.findall(r'\d+\.\d+(?=g)', item)
        if unit == "cc":
            matches = re.findall(r'\d+\.\d+(?=cc)', item)
        if unit == "pt":
            matches = re.findall(r'\d+\.\d+(?=pt)', item)
        # matches = re.search(r'\d+\.\d+', item)
        # if origin == "aveda_full_spectrum" and desired == "loreal_majirel":
        #     if "7n" not in colorcode and "7N" not in colorcode:
        #         matches = matches[:-1]
        if matches:
            # value = float(matches.group())
            # values.append(value)
            values.extend(map(float, matches))

    print(values)
    temp = values

    if unit == "oz":
        temp = [round((value * 2) / sum(temp), 2) if sum(temp) != 0 else 0 if value != 0 else 0 for value in temp]
    if unit == "g":
        temp = [round((value * 56.70) / sum(temp), 2) if sum(temp) != 0 else 0 if value != 0 else 0 for value in temp]
    if unit == "cc":
        temp = [round((value * 59.15) / sum(temp), 2) if sum(temp) != 0 else 0 if value != 0 else 0 for value in temp]
    if unit == "pt":
        temp = [round((value * 32) / sum(temp), 2) if sum(temp) != 0 else 0 if value != 0 else 0 for value in temp]

    print(temp)
    result = []
    for item in results:
        # print(item)
        for i in range(len(values)):
            if unit == "oz":
                # item = item.replace(str(values[i])+'oz', str(temp[i])+'oz')
                pattern = r"\b" + re.escape(str(values[i])) + r"oz\b"
                item = re.sub(pattern, str(temp[i])+'oz', item)
            if unit == "g":
                # item = item.replace(str(values[i])+'g', str(temp[i])+'g')
                pattern = r"\b" + re.escape(str(values[i])) + r"g\b"
                item = re.sub(pattern, str(temp[i])+'g', item)
            if unit == "cc":
                # item = item.replace(str(values[i])+'cc', str(temp[i])+'cc')
                pattern = r"\b" + re.escape(str(values[i])) + r"cc\b"
                item = re.sub(pattern, str(temp[i])+'cc', item)
            if unit == "pt":
                # item = item.replace(str(values[i])+'pt', str(temp[i])+'pt')
                pattern = r"\b" + re.escape(str(values[i])) + r"pt\b"
                item = re.sub(pattern, str(temp[i])+'pt', item)
        result.append(item)
    print(result)

    sys.stdout = old_stdout
    log_file.close()
    
    return str(result)

if __name__ == "__main__":
    app.run()
