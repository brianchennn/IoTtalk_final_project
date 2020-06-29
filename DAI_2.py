# DAI2.py  -- new version of Dummy Device DAI.py, modified by tsaiwn@cs.nctu.edu.tw
# you can get from here:  https://goo.gl/6jtP41   ; Search dummy + iottalk  for other files
import time, DAN, requests, random 
import threading, sys
import re
# ServerURL = 'http://Your_server_IP_or_DomainName:9999' #with no secure connection
# ServerURL = 'http://192.168.20.101:9999' #with no secure connection
#  注意你用的 IoTtalk 伺服器網址或 IP 
ServerURL = 'http://3.iottalk.tw:9999' #with SSL secure connection
# ServerURL = 'https://Your_DomainName' #with SSL connection  (IP can not be used with https)
Reg_addr = "F_Dummy" #if None, Reg_addr = MAC address

mac_addr = 'C860008BD241'  # put here for easy to modify;;  the mac_addr in DAN.py is NOT used
# Copy DAI.py to DAI2.py and then modify the above mac_addr, then you can have two dummy devices
Reg_addr = mac_addr   # Otherwise, the mac addr generated in DAN.py will always be the same !

#DAN.profile['dm_name']='Dummy_Device'   # you can change this but should also add the DM in server
DAN.profile['dm_name']='F_Dummy'
DAN.profile['df_list']=['Dummy_Sensor', 'Dummy_Control', 'Color-I']
DAN.profile['d_name']= "F_Dummy" # None for autoNaming
DAN.device_registration_with_retry(ServerURL, Reg_addr)

# global gotInput, theInput
gotInput=False
theInput="haha"
allDead=False



def showData( ):
   print("current R=", r, ",G=", g, ",B=", b, ",LUM=", Luminance)
def myInt(tmp):
   try:
     ans = int(tmp);
   except:  #ignore the exception
     ans = 0
   return ans

Luminance = 255; r = g = b = 123;
def parse(what):
  global cmd, r, g, b, Luminance, lum
  what += ["-1", "-1", "-1", "-1"]  # append for missing argument
  (cmd, haha, *_) = what   # Luminance value
  cmd = cmd.upper( )
  if cmd[0] == "Q" or cmd[0] == "E": return
  if cmd[0] == "S": return;
  if cmd[0] == "L":
     Luminance = myInt(haha);
     if Luminance < 0: Luminance = 198;  #  no data
  elif cmd[0] == "C":  # Color r, g, b, brightness
     (cmd2, r, g, b, lum, *_) = what
     r=myInt(r); g=myInt(g);  b=myInt(b);  # ignore exception
     if (r < 0): r= 102;  # no data
     if g < 0: g=153;
     if b < 0: b=153;
     lum=myInt(lum);  # Lum NOT specified if got -1
     if lum >= 0: Luminance = lum
  #end of function parse
print("start r=", r, ",g=", g, ",b=", b,",L=", Luminance)






def doRead( ):
    global gotInput, theInput, allDead
    while True:
        if gotInput:
           time.sleep(0.1)
           continue  # go back to while
        try:
           theInput = input("Give me data: ")
        except Exception:    ##  KeyboardInterrupt:
           allDead = True
           print("\n\nDeregister " + DAN.profile['d_name'] + " !!!\n",  flush=True)
           DAN.deregister()
           sys.stdout = sys.__stdout__
           print(" Thread say Bye bye ---------------", flush=True)
           sys.exit( );   ## break  # raise   #  ?
        gotInput=True
        ans = re.split(" ,|, |,| ", theInput)
      ## please try to input: color  55, 168, 33  44  55
        print("Original ans=", ans)

        ans = [ x for x in ans if x]  # remove empty string
        print("new ans=", ans)
        parse(ans);
        if cmd[0] == "Q" or cmd[0] == "E": break;
        if cmd[0] == "S":
           showData( );
           continue;
        if cmd[0] == "L":
           print("cmd=", cmd, "; Luminance=", Luminance)
        elif cmd[0] == "C":
           print("cmd=", cmd, ",R=", r, ",G=", g, ",B=", b, ",LUM=", Luminance)
        else:
           print("Illegal command. Only C / L two commands allowed.")
           print("Please Re-Enter your ", end="");


        if theInput !='quit' and theInput != "exit":
           print("Will send " + theInput, end="   , ")

#creat a thread to do Input data from keyboard, by tsaiwn@cs.nctu.edu.tw
threadx = threading.Thread(target=doRead)
threadx.daemon = True
threadx.start()

while True:
    try:
    #Pull data from a device feature called "Dummy_Control"
        value1=DAN.pull('Dummy_Control')
        if value1 != None:
            print (value1[0])
    #Push data to a device feature called "Dummy_Sensor" 
        if gotInput:
          if cmd[0] =='Q' or cmd[0]=="E":
              break;  #  sys.exit( );
          #value2=random.uniform(1, 10)
          '''try:
              value2=float( theInput )
          except:
              value2=0'''
          gotInput=False   # so that you can input again 
          if(allDead): break;
          if cmd[0] == "L":
              DAN.push ('Dummy_Sensor', Luminance,  Luminance)
              print("Luminance=", Luminance)
          elif cmd[0] == "C":
              DAN.push ('Color-I', r, g, b)
              DAN.push ('Dummy_Sensor', Luminance,  Luminance)
              print("R=", r, ",G=", g, ",B=", b, ",LUM=", Luminance)
          else:
              print("Illegal command. Only C / L two commands allowed.")
              print("Please Re-Enter your ", end="");


    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)    
    try:
       time.sleep(0.2)
    except KeyboardInterrupt:
       break
time.sleep(0.5)
try: 
   DAN.deregister()
except Exception as e:
   print("===")
print("Bye ! --------------", flush=True)
sys.exit( );