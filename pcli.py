'''
Created on Nov 9, 2015

@author: aotto
'''

import pexpect, logging
import argparse, itertools
import getpass
import sys, os
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from symbol import parameters
import commands

prompt ='#'
linesep = '\r'
more="--More--"
error="% Error: "

def gracefully_exit():
    logging.debug("Exiting.")    
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
                logging.error("%s@%s: Wrong password."%(user,hostname))
                close_connection(child)
                gracefully_exit()
            except: 
                pass
            #child.readline()
            enable = child.expect('%s#'%hostname)
            if enable == 0:
               logging.debug("%s@%s: Succesfully logged."%(user,hostname))
        elif err==1:
            logging.error("%s@%s:Something went wrong (unknown host?) or connection timed out.\n"%(user,hostname))
            pass
    except Exception as e:
        logging.exception("%s@%s: Please check this error:"%(user,hostname))
        exit(0)
    return child
    
def command_to_send(command,datalist=None, iteration=1):
     commands =[]
     print datalist
     if is_nested(command):
         command = unnest(command)   
     #commands =  linesep.join(i for i in command) + linesep
     for i in command:
         i = i + linesep
         commands.append(i)
         
     if datalist != None:
         for i in commands:
             nums=i.count('%s')
             if nums > 0 :
                 for it in range(nums):
                     print i
         
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
            logging.error("%s@%s: Incorrect command. Probably unsupported by switch OS."%(hostname,user))
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
    
def open_file(parser, arg):
    try:
        with open(arg,'r') as paramfile:
            content = paramfile.readlines()
    except Exception as e: 
        logging.exception("Parametrized (-p) file does not exists. Aborting.")
        gracefully_exit()
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

def parameters_validate(parameters_list, num_of_hosts):
    parameters = []
    for i in parameters_list:
        tmp = i.split(';')
        parameters.append(tuple(tmp))
        
    if len(parameters) != num_of_hosts:
        logging.error('The number of parameters is not equal to number of hosts. Aborting.')
        gracefully_exit()
        
    return tuple(parameters)
    
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
    parser.add_argument('-p','--parameter',help='If your command is parametrized, please provide a file with parameters.List of parameters for specific host per line.\
     Order must be the same as the switch one. The file structure must be following:\nparameter1 for host1;parameter2 for host1;etc\nparameter1 for host2;parameter2 for host2;etc',type=lambda x: open_file(parser, x))
    parser.add_argument('switch', nargs='+', help="The switch list or file the list of switches to run command on.",type = lambda x: is_file(parser,x))
    args = parser.parse_args()
    switch = args.switch
    user = args.user
    command = args.command
    parameters=args.parameter
    debug = args.verbose
    if is_nested(switch):
        return unnest(switch), user, command, debug, parameters        
    return switch, user, command, debug, parameters

def debug_logging(debug_on):
    #FORMAT="%(user)s@%(hostname)s: %(message)s"
    debug_lvl=logging.ERROR
    if debug_on:
        debug_lvl=logging.DEBUG
        
    FORMAT="\n[%(levelname)5s] %(message)s"
    logging.basicConfig(format=FORMAT, level=debug_lvl)

def connection_star_thread(zipped_data):
    return connection_thread(*zipped_data)

def connection_thread(host,command,user,passwd):
    #print host, command, user, passwd
    connection = switch_connect(host, user, passwd)
    send_command(connection,command,user,host)
    close_connection(connection,user,host)
    #gracefully_exit()

if __name__ == '__main__':
    
    switch, user, command, debug, parameters = get_argument()
    debug_logging(debug)
    if parameters != None:
        parameters=parameters_validate(parameters, len(switch))
    #print parameters
    command = command_to_send(command,parameters,len(switch))
    #exit(1)
    
    logging.debug("User: %s\nNetwork devices: %s\nCommands: %s\nDebug: %s\n"%(user,switch,command,debug))
    exit(1)
    passwd = getpass.getpass('Please provide password for user %s:'%user)
    
    data_holder= itertools.izip(switch,itertools.repeat(command),itertools.repeat(user),itertools.repeat(passwd))
    pool = ThreadPool() 
    
    #print list(data_holder)
    pool.map(connection_star_thread,data_holder)
    pool.close()
    pool.join()

#    for host in switch:
#        connection = switch_connect(host, user, passwd)
#        send_command(connection,command,user,host)
#        close_connection(connection,user,host)
    
    gracefully_exit()
