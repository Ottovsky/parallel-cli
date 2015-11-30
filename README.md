## Synopsis

Simple script to execute network device commands on multiple hosts in parallel.

## Motivation

To simplify netops job. 

## Installation

No instalaltion needed. 

## Requirements

This script requires preinstalled: **pexpect** and **python>= 2.7**.

##Usage

To execute a simple command on two devices, just run :
```
./pcli.py switch1 switch2 -c "show clock"
```

If you have a file with list of devices, just specify this file: 
```
./pcli.py switchlist.txt -c "show clock"
```
You can combine hosts and files:
```
./pcli.py switchlist.txt switch3a -c "show clock"
```
The same thing for commands, you can put them in a file as well:
```
./pcli.py switchlist.txt switch3a -c commands.txt
```
You can parametrize a command file, by replacing all variables by **%s** and providing file with parameters: 
```
./pcli.py switchlist.txt -c commands.txt -p parameters.txt
```
###Files structure:

####File with list of network devices: 
```
switch1
switch2
switch3
```
####Files with list of commands and parameters:
Parametrized command list:

```
conf t
interface vlan %s
description %s
ip address %s 
no shutdown
end
```

The structure of the parameters file. In the current version, this file must have a csv like structure, each entry in the row is separated by **";"**. So the table look as follows:

|Parameter 1|   Parameter 2    | Parameter 3  |
| ---- |:-------------:| -----:|
|210   |"description for the switch1"   |10.10.10.10 |
|220   |"description for the switch2"   |12.1.2.1    |
|212   |"description for the switch3"   |2.3.4.5     |

As you can see the order of the parameters is exactly the same as they appear in the command file. Each row stands for parameters for one switch, they also must be in the same order as they are in the switch list, otherwise, you can execute commands on other switch than expected.

Parameters file structure:
```
210;"description for the switch1";10.10.10.10
220;"description for the switch2";12.1.2.1
212;"description for the switch3";2.3.4.5
```
###Example output:
** python pcli.py switch1 switch2 -c "show clock"  -v **

```
[DEBUG] User: admin
Network devices: ['switch1', 'switch2']
Commands: [['show clock\r'], ['show clock\r']]
Debug: True
Logging: False

Please provide password for user admin:

[DEBUG] admin@switch1: Connecting to the host.

[DEBUG] admin@switch2: Connecting to the host.
Warning: Permanently added 'switch1,8.8.8.8' (RSA) to the list of known hosts.
Warning: Permanently added 'switch2,9.9.9.9' (RSA) to the list of known hosts.
admin@switch1's password: admin@switch2's password: 

switch1#switch2#
[DEBUG] admin@switch1: Succesfully logged.

[DEBUG] admin@switch2: Succesfully logged.
show clock
15:59:39.373 CET Mon Nov 30 2015
show clock
15:59:39.396 CET Mon Nov 30 2015
switch2#
[DEBUG] admin@switch2: Closing connection.
switch1#
[DEBUG] admin@switch1: Closing connection.

[DEBUG] Exiting.
```
##Help

```
usage: pcli.py [-h] [-u USER] [-v] [-l] -c COMMAND [COMMAND ...]
               [-p PARAMETER]
               switch [switch ...]

Execute command on multiple switches.

positional arguments:
  switch                The switch list or file the list of switches to run command on.

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  User to use in order to log into switches. By default admin.
  -v, --verbose         Turn on verbose.
  -l, --logging         Log connection output to the file, otherwise to stdout.
  -c COMMAND [COMMAND ...], --command COMMAND [COMMAND ...]
                        [REQUIRED] Command to perform on the switches.Commands can be read from the file (preffered)or from command line example: -c "show clock" "show interfaces" "etc ..".
                        File should contain all the commands that you would type on the switch to obtain desired output. Example:
                            conf t
                            int vlan 30
                            no ip addr
                            shutdown
                            end
  -p PARAMETER, --parameter PARAMETER
                        If your command is parametrized, please provide a file with parameters.List of parameters (parameter per column) for specific host per row.     Order must be the same as the switch one. :
                        parameter1 for host1;parameter2 for host1;etc
                        parameter1 for host2;parameter2 for host2;etc

Current version(0.1) assumes one password for all used devices.
```

