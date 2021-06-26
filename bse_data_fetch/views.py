from django.shortcuts import render
import datetime, time
import requests, zipfile, os
from threading import Timer
import threading
import pandas as pd
import redis, json, os
from django.http import JsonResponse


# Create your views here.
def home(request):
    active_threads = []
    for thread in threading.enumerate():
        active_threads.append(thread.name)
    # print("Active Threads",threading.active_count(),active_threads)
    if "timer_thread" not in active_threads:
        start_timer()
    # print("Active Threads",threading.active_count())

    Client = redis.from_url(os.environ.get("REDIS_URL"))
    keys = Client.keys("*")
    file_name = get_latest_file(keys)

    Client.close()

    return render(request, 'index.html' , {'file_name':file_name})

def sending_json_data(request,q=None):
    Client = redis.from_url(os.environ.get("REDIS_URL"))
    keys = Client.keys("*")
    data = []
    
    for key in keys:
        sc_code = Client.hget(key,"SC_CODE").decode('utf8')
        sc_name = Client.hget(key,"SC_NAME").decode('utf8')
        open_ = Client.hget(key,"OPEN").decode('utf8')
        high_ = Client.hget(key,"HIGH").decode('utf8')
        low_ = Client.hget(key,"LOW").decode('utf8')
        close_ = Client.hget(key,"CLOSE").decode('utf8')
        # data[key.decode('utf8')] = [sc_name,open_,high_,low_,close_]
        data.append({"SC_CODE":sc_code,"SC_NAME":sc_name,"OPEN":open_,"HIGH":high_,"LOW":low_,"CLOSE":close_})

    if q != None:
        query_data = []
        for i in data:
            if q.lower() in i['SC_NAME'].replace(" ","").lower():
                query_data.append(i)
        data = query_data

    Client.close()

    return JsonResponse({'data':data})



found = False

def download_extract(d = None):
    global found
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    url = "https://www.bseindia.com/download/BhavCopy/Equity/"
    if d == None:
        d = datetime.date.today()
    filename = "EQ"+str(d.strftime("%d"))+str(d.strftime("%m"))+str(d.strftime("%y"))+"_CSV.zip"
    filename_ = "EQ"+str(d.strftime("%d"))+str(d.strftime("%m"))+str(d.strftime("%y"))+".csv"
    
    if not os.path.exists(os.path.join("Extracted_files",filename_)):
        downloadUrl = url+filename
        req = requests.get(downloadUrl,headers = headers)
        if req.status_code != 404:
            with open(filename,'wb') as zip_file:
                for chunk in req.iter_content(chunk_size=1024):
                    if chunk:
                        zip_file.write(chunk)
                time.sleep(0.001)
            zf = zipfile.ZipFile(filename,'r')
            zf.extractall("Extracted_files")
            zf.close()
            parse_file(os.path.join("Extracted_files",filename_))
        else:
            print("File Not Found on the server!!!")
            if not found:
                d = d-datetime.timedelta(days=1)
                filename_ = "EQ"+str(d.strftime("%d"))+str(d.strftime("%m"))+str(d.strftime("%y"))+".csv"
                if os.path.exists(os.path.join("Extracted_files",filename_)):
                    found = True
                    parse_file(os.path.join("Extracted_files",filename_))
                else:
                    download_extract(d)



def get_latest_file(keys = None):
    print("Finding Latest File...")
    d = datetime.datetime.today()
    try:
        while True:
            filename_ = "EQ"+str(d.strftime("%d"))+str(d.strftime("%m"))+str(d.strftime("%y"))+".csv"
            if os.path.exists(os.path.join("Extracted_files",filename_)):
                if keys == None:
                    filename_ = parse_file(os.path.join("Extracted_files",filename_))
                break
            else:
                d = d-datetime.timedelta(days=1)
        return filename_
    except:
        download_extract()
        get_latest_file()
    return filename_


def parse_file(filename):
    print(filename)
    df = pd.read_csv(filename)
    df = df.drop(['SC_GROUP','SC_TYPE','LAST','PREVCLOSE','NO_TRADES','NO_OF_SHRS','NET_TURNOV','TDCLOINDI'], 1)
    print(df.head())
    print(filename[-12:])
    write_to_redis(df)
    return filename

def write_to_redis(df):
    Client = redis.from_url(os.environ.get("REDIS_URL"))
    Client.flushall()
    for i in range(len(df)):
        data = {'SC_CODE':str(df['SC_CODE'][i]),'SC_NAME':df['SC_NAME'][i],'OPEN':str(df['OPEN'][i]),'HIGH':str(df['HIGH'][i]),'LOW':str(df['LOW'][i]),'CLOSE':str(df['CLOSE'][i])}
        Client.hmset(str(df["SC_CODE"][i]),data)

    Client.close()
        

def start_timer():
    current_dt = datetime.datetime.now()
    if current_dt.hour < 18:
        next_timer = current_dt.replace(day=current_dt.day, hour=18, minute=0, second=0, microsecond=0)
    else:
        next_timer = current_dt.replace(day=current_dt.day, hour=18, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    timer_ = next_timer - current_dt

    # print(current_dt)
    # print(next_timer.strftime("%d-%m-%y: %I:%M:%S %p"))
    print(timer_)
    total_timer_seconds = timer_.total_seconds()

    t = Timer(total_timer_seconds,download_extract,args={})
    t.name = "timer_thread"
    t.start()

    
    

# download_extract()
# start_timer()