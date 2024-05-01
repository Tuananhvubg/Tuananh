import os
import pypdf
import json

path_dir = "D:/AUTOSAR 4.4.0/BodyAndComfort"
file_name = "AUTOSAR_SWS_FlashEEPROMEmulation.pdf"
path_file = os.path.abspath(path_dir+"/"+os.listdir(path_dir)[0])

reader = pypdf.PdfReader("AUTOSAR_SWS_FlashEEPROMEmulation.pdf")

SWS_Dict_List = []

temp_SWS = {
        "ID":"",
        "Content" : "",
        "MotherSRS" :""
    }

def parsePage_SWS(pageNumber,count):
    global reader
    global SWS_Dict_List
    global temp_SWS
    found_SWS = 0
    start_SWS = 0
    SWS_Dict = {
        "ID":"",
        "Content" : "",
        "MotherSRS" :""
    }
    page = reader.pages[pageNumber]
    for line in page.extract_text().split("\n")[count+1:]:
        if temp_SWS["ID"] == "":
            if line.find("SWS_") != -1:
                SWS_Dict["ID"] = '_'.join(text_.strip() for text_ in line.split("]")[0].split("[")[-1].split("_"))
                found_SWS = 1
            if line.find("⌈") != -1 and found_SWS == 1:
                start_SWS = 1
        else:
            SWS_Dict = temp_SWS
            start_SWS = 1
        if start_SWS == 1:
            SWS_Dict["Content"] += "\n" + ' '.join(text_.strip() for text_ in line.split("⌈")[-1].split("⌋")[0].strip().split(" "))
        if start_SWS == 1 and line.find("⌋") != -1:
            start_SWS = 0
            found_SWS = 0
            SWS_Dict["MotherSRS"] = '_'.join(text_.strip() for text_ in line.split("⌋")[-1].split("(")[-1].split(")")[0].split("_"))
            SWS_Dict_List.append(SWS_Dict)
            SWS_Dict = {
                "ID":"",
                "Content" : "",
                "MotherSRS" :""
            }
            temp_SWS = {
                "ID":"",
                "Content" : "",
                "MotherSRS" :""
            }
    if found_SWS == 1:
        temp_SWS = SWS_Dict

def parsePage_ECUC(pageNumber,count):
    global reader
    global SWS_Dict_List
    global temp_SWS
    found_SWS = 0
    start_SWS = 0
    SWS_Dict = {
        "ID":"",
        "Content" : "",
        "MotherSRS" :""
    }
    page = reader.pages[pageNumber]
    for line in page.extract_text().split("\n")[count+1:]:
        if temp_SWS["ID"] == "":
            if line.find("SWS Item") != -1:
                SWS_Dict["ID"] = '_'.join(text_.strip() for text_ in line.split("SWS Item ")[-1].split(" :")[0].split("_"))
                found_SWS = 1
            if line.find("Name") != -1 and found_SWS == 1:
                start_SWS = 1
        else:
            SWS_Dict = temp_SWS
            start_SWS = 1
        if start_SWS == 1 and line.find("SWS Item") == -1 and line.find("ECUC") == -1:
            SWS_Dict["Content"] +=  ' '.join(text_.strip() for text_ in line.strip().split(" ")) + "\n"
        if start_SWS == 1 and line.find("No Included Containers") != -1 or line.find("Scope / Dependency") != -1 or line.find("Configuration Parameters") != -1:
            start_SWS = 0
            found_SWS = 0
            SWS_Dict["Content"] = SWS_Dict["Content"].replace("Name\n","Name ")
            SWS_Dict_List.append(SWS_Dict)
            
            SWS_Dict = {
                "ID":"",
                "Content" : "",
                "MotherSRS" :""
            }
            temp_SWS = {
                "ID":"",
                "Content" : "",
                "MotherSRS" :""
            }
    if found_SWS == 1:
        temp_SWS = SWS_Dict
def compareString(str1,str2):
    countDif = abs(len(str1)-len(str2))
    for t in range (0,min(len(str1),len(str2)) - 1):
        if str1[t] != str2[t]:
            countDif += 1
    if countDif < 3:
        return True
    else: return False
    
def findingFootageHeader():
    global reader
    result = []
    list_line = []
    list_temp_line = []
    for t in range(0,1000):
        result.append(0)
        list_line.append("")
    list_line = reader.pages[0].extract_text().split("\n")
    for pagecnt in range(1,len(reader.pages)-1):
        page = reader.pages[pagecnt]
        list_temp_line = page.extract_text().split("\n")
        min_cnt = min(len(list_line),len(list_temp_line))
        for t in range(0,min_cnt):
            if compareString(list_line[t].strip(),list_temp_line[t].strip()):
                result[t] = 1
            else: result[t] = 0
    return len(result) - result[-1::-1].index(1) -1
ftH = findingFootageHeader()
for pagecnt in range(0,len(reader.pages)-1):
    parsePage_SWS(pagecnt,ftH)
    parsePage_ECUC(pagecnt,ftH)
    
with open("output.json","w") as f:
    f.write(json.dumps(SWS_Dict_List, indent=4))
import pandas
pandas.read_json("output.json").to_excel(file_name.split(".")[0] + ".xlsx")
