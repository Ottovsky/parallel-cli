'''
Created on Nov 9, 2015

@author: aotto
'''

import pexpect, logging
import argparse
import getpass
import sys, os

prompt ='#'
linesep = '\r'
more="--More--"
error="% Error: "

def gracefully_exit():    
    os._exit(1)

def switch_connect(hostname, user, password):
    try: 
        child = pexpect.spawn('ssh %s@%s'%(user,hostname))
        child.logfile_read =sys.stdout  # open("pexpect.log",'w')
        err  = child.expect('assword:')
        if err==0:
            child.sendline(password)
            try:
                child.expect_exact('Permission denied, please try again.',0.2)
                logging.error("\n%s@%s: Wrong password."%(user,hostname))
                close_connection(child)
                gracefully_exit()
            except: 
                pass
            #child.readline()
            enable = child.expect('%s#'%hostname)
            if enable == 0:
               logging.debug("\n%s@%s: Succesfully logged."%(user,hostname))
        elif err==1:
            logging.error("\n%s@%s:Something went wrong (unknown host?) or connection timed out.\n"%(user,hostname))
            pass
    except Exception as e:
        logging.exception("\n%s@%s: Please check this error:"%(user,hostname))
        exit(0)
    return child
        
    
def command_to_send(command,datalist=None, iteration=1):
     commands =[]
     if is_nested(command):
         command = unnest(command)   
     #commands =  linesep.join(i for i in command) + linesep
     for i in command:
         i = i + linesep
         commands.append(i)
         
     return commands
     
def send_command(connectionid, commands,hostname='',user=''):
    for command in commands:
        connectionid.sendline(command)
        err = connectionid.expect([prompt,more, error])
        #print err
        if err==1:
            while err==1:
                connectionid.send(linesep)
                err = connectionid.expect([prompt,more, error])
        if err==2:
            logging.error("\n%s@%s: Incorrect command. Probably unsupported by switch OS."%(hostname,user))
            continue
        if err==0:
            continue

def close_connection(connectionid,user='',hostname=''):
        logging.debug("%s@%s: Closing connection."%(user,hostname))
        connectionid.close()
        
def is_file(parser, arg):
    if not os.path.isfile(arg):
        return arg
    else:
        with open(arg,'r') as file:
            content = file.readlines()
        return content

def is_nested(list_to_check):
    return any(isinstance(i, list) for i in list_to_check)
    

def unnest(nested_list):
    single_list=[]
    for i in nested_list:   
        if isinstance(i, list):
            for switch in i:
                single_list.append(switch.replace('\n',''))
        else:
            single_list.append(i)                       
    return single_list

def get_argument():
    parser = argparse.ArgumentParser(description="Execute command on multiple switches.", formatter_class=argparse.RawTextHelpFormatter,epilog="Current version(0.1) assumes one password for all used devices.")
    parser.add_argument('-u','--user',help='User to use in order to log into switches. By default admin.',default='admin')
    parser.add_argument('-v','--verbose',help='Turn on verbose.',action='store_true')
    parser.add_argument('-c','--command',nargs='+',required=True,help='[REQUIRED] Command to perform on the switches.\
Commands can be read from the file (preffered)or from command line example: -c "show clock" "show interfaces" "etc ..".\nFile should contain all the commands that you would type on the switch to obtain desired output. Example:\n\
    conf t\n\
    int vlan 30\n\
    no ip addr\n\
    shutdown\n\
    end',type= lambda x: is_file(parser,x))
    parser.add_argument('switch', nargs='+', help="The switch list or file the list of switches to run command on.",type = lambda x: is_file(parser,x))
    args = parser.parse_args()
    switch = args.switch
    user = args.user
    command = args.command
    debug = args.verbose
    if is_nested(switch):
        return unnest(switch), user, command, debug         
    return switch, user, command, debug

def debug_logging(debug_on):
    #FORMAT="%(user)s@%(hostname)s: %(message)s"
    debug_lvl=logging.ERROR
    if debug_on:
        debug_lvl=logging.DEBUG
        
    FORMAT="%(message)s"
    logging.basicConfig(format=FORMAT, level=debug_lvl)
    
    

if __name__ == '__main__':
    
    switch, user, command, debug = get_argument()
    
    command = command_to_send(command)
    #exit(1)
    debug_logging(debug)
    logging.debug("User: %s\nSwitches: %s\nCommands: %s\nDebug: %s\n"%(user,switch,command,debug))
    #exit(1)
    passwd = getpass.getpass('Please provide password for user %s:'%user)
    
    for host in switch:
        connection = switch_connect(host, user, passwd)
        send_command(connection, command,user,host)
        close_connection(connection,user,host)
    
    gracefully_exit()
