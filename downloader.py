#Author : Rohit Bhardwaj
#Email : techvirtuoso.rohit@gmail.com


# need python 2.7.10 or 2.7.11
# it is better to use it in linux
import urllib2,sys,os,ssl
import time
import threading



def get_directory():
	name="download"
	count=1
	while(os.path.exists(name+str(count)) is True):
		count+=1
	return name+str(count)

###### PUT DOWNLOAD LINK BELOW

site = "http://217.219.143.108/3311/Pirates%20of%20the%20Caribbean%20On%20Stranger%20Tides%20(2011)/POTC4.On.Stranger.Tides.2011.720p.mkv"
movies=open("movies.txt", "a")

temp=site.split('/')
speed=0.0
downloaded=0.0
st=" KB"
div=1024.0
no_of_threads=50  #change threads accordingly
stopped_threads=0
lock = threading.Lock()
hdr = {'User-Agent': 'Mozilla/5.0'}
req = urllib2.Request(site,headers=hdr)
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)   # comment this if u have python less than 2.7.10 and remove all context
connection=False
lastsave=0.0
lastdwnld=0.0
gl_flag=True
file_name=temp[len(temp)-1]
if(len(file_name)>100):
	file_name='Unknown'
threads_running=0
folder=get_directory()
os.makedirs(folder)
peak_speed=0
while(connection==False):
		try:
			u = urllib2.urlopen(req,context=context,timeout=10)
			z=u.info()
			if(len(z.getheaders('Content-Length'))>0 ):
				connection=True
			
		except :
    			time.sleep(5)
    			connection=False
meta = u.info()
if(len(meta.getheaders('Content-Disposition'))>0):
	xx=meta.getheaders('Content-Disposition')[0]
	b=xx.split('filename=')
	if(len(b)>1):
		file_name=b[1]
		file_name=file_name[1:len(file_name)-1]
		if(file_name[len(file_name)-1]=='"'):
			file_name=file_name[0:len(file_name)-1]
			
print "\nFile Name => "+file_name+"\n"
count=0
file_size = int(meta.getheaders("Content-Length")[0])
ssc="KB"
fss=file_size/1024.0
if(fss>=1024):
	fss/=1024
	ssc="MB"
	if(fss>=1024):
		fss/=1024
		ssc="GB"
print("File size is : %0.3f %s \n"%(fss,ssc))

def check_speed():
	global lastsave,lastdwnld,count,gl_flag,speed,peak_speed
	while gl_flag:
		time.sleep(1)
		with lock:
			c=time.time()
			speed=(lastdwnld)/(c-lastsave)
			lastdwnld=0.0
			lastsave=c
			peak_speed=max(speed,peak_speed)
def print_it():
	sdt="KB"
	global downloaded,speed,st,div,lock,file_size,threads_running,count
	
	file_size_dl=downloaded/div
	spd=speed/1024
	if(spd>=1024):
		spd/=1024.0
		sdt="MB"
	tim_rem=10000000
	if(speed>0):
		tim_rem=int((file_size-downloaded)/speed)
	done=downloaded*100/file_size
	if(file_size_dl>=1024):
    			file_size_dl/=1024.0
    			div*=1024.0
    			if(st==" KB"):
    				st=" MB"
    			elif(st==" MB"):
    				st=" GB"
    	print("Downloaded : %.3f %s                             "%(file_size_dl,st))
	print("Downloading speed %.2f %s/S ....                  "%(spd,sdt))
	print("Done  %.2f %%                         "%(done))
	if(speed>0):
		print("Time remaining %d m : %d sec                      "%(tim_rem/60,tim_rem%60))
	else:
		print("Time remaining ...............            ")
	print("Threads running %d...              "%(threads_running))
	print("Total threads %d...              "%(count))
    	sys.stdout.write("\033[F")
    	sys.stdout.write("\033[F")
    	sys.stdout.write("\033[F")
    	sys.stdout.write("\033[F")
    	sys.stdout.write("\033[F")
    	sys.stdout.write("\033[F")
    	
    	
def downloader_func(url,start,end,file_name,block_sz=8192):
	global speed,downloaded,lock,fin_th,lastsave,lastdwnld,count,context,threads_running,file_size,stopped_threads
	hdr = {'User-Agent': 'Mozilla/5.0'}
	req = urllib2.Request(site,headers=hdr)
	req.add_header('Range', 'bytes=' + str(start) + '-' + str(end))
	connection=False
	f = open(file_name, 'wb')
	stopped_threads+=1
	while(connection==False):
		try:
			u = urllib2.urlopen(req,context=context,timeout=5)
			z=u.info()
			if(len(z.getheaders('Content-Length'))>0 ):
				connection=True
				if(z.getheaders('Content-Length')[0]==file_size and start!=0):
					count-=1
					return
		except :
			time.sleep(3)
    			connection=False
	
	dwnld=0
	threads_running+=1
	stopped_threads-=1
	while True:
		try:
    			buffer = u.read(block_sz)
    		except:
    			threads_running-=1
    			stopped_threads+=1
			req = urllib2.Request(site,headers=hdr)
			req.add_header('Range', 'bytes=' + str(start+dwnld) + '-' + str(end))
			connection=False
			
			while(connection==False):
				try:
					u = urllib2.urlopen(req,context=context,timeout=5)
					z=u.info()
					if(len(z.getheaders('Content-Length'))>0 ):
						connection=True
				except :
    					time.sleep(3)
    					connection=False
    			threads_running+=1
    			stopped_threads-=1
			continue
    			
    		if not buffer:
       			 break
       		lastdwnld+=(len(buffer))
       		dwnld += (len(buffer))
    		downloaded += (len(buffer))
    		
    		f.write(buffer)	
    		with lock:
    			print_it()
    		
    	
    	threads_running-=1
    	count-=1
	
	
per_thread=max(102400,file_size/no_of_threads)

start=0
files=[]
time_start=time.time()
t=threading.Thread(target=check_speed)
t.start()
ind=0
while(start<=file_size):
	name=folder+"/dummy"+str(ind)
	t=threading.Thread(target=downloader_func,args=(site,start,min(file_size-1,start+per_thread),name))
	files.append(name)
	start+=(per_thread+1)
	t.start()
	count+=1
	ind+=1
	


while(count>0):
	time.sleep(2)
gl_flag=False
tot_tim=time.time()-time_start

for i in  range(5):
	print "                                                   "
sys.stdout.write("\033[F")
sys.stdout.write("\033[F")
print("Time to download : %d m : %d s                          "%(tot_tim/60,tot_tim%60))
print("average speed :  %0.4f  KB/s                    "%(file_size/(1024.0*tot_tim)))
print("Peak speed:  %0.4f  MB/s                    "%(peak_speed/(1024*1024.0)))
if(os.path.exists(file_name)==True):
	count=1
	while(os.path.exists(file_name)==True):
		file_name=str(count)+file_name
with open(file_name, 'w') as outfile:
    for fname in files:
        with open(fname) as infile:
            print("please wait , joining file %s .....                         "%(fname))
            sys.stdout.write("\033[F")
            for line in infile:
                outfile.write(line)
        os.remove(fname)
os.rmdir(folder)
print("                                                  ")
movies.write(str(time.asctime( time.localtime(time.time()) ))+"   "+file_name+"  "+str(file_size/(1024*1024))+" mb \n ")

	
  	
