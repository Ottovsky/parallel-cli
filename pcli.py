'''
Created on Nov 9, 2015

@author: aotto
'''

import pexpect, re
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
                print "\nWrong password."
                close_connection(child)
                gracefully_exit()
            except: 
                pass
            #child.readline()
            enable = child.expect('%s#'%hostname)
            if enable == 0:
                print "Succesfully logged."
        elif err==1:
            print "Something went wrong (unknown host?) or connection timed out.\n"
            pass
    except Exception as e:
        print e
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
     
def send_command(connectionid, commands):
    for command in commands:
        connectionid.sendline(command)
        err = connectionid.expect([prompt,more, error])
        #print err
        if err==1:
            while err==1:
                connectionid.send(linesep)
                err = connectionid.expect([prompt,more, error])
        if err==2:
            print "Incorrect command. Probably unsupported by switch OS.\n"
            continue
        if err==0:
            continue

def close_connection(connectionid):
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
    parser = argparse.ArgumentParser(description="Execute command on multiple switches.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-u','--user',help='User to use in order to log into switches. By default admin.',default='admin')
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
    if is_nested(switch):
        return unnest(switch), user, command           
    return switch, user, command


if __name__ == '__main__':
    
    
    #user=''
    switch, user, command = get_argument()
    print switch, user
    command = command_to_send(command)
    print command
    #exit(1)
    passwd = getpass.getpass('Please provide password for user %s:'%user)

    for host in switch:
        connection = switch_connect(host, user, passwd)
        send_command(connection, command)
        close_connection(connection)
    
    gracefully_exit()
