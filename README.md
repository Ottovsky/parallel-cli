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

The structure of the parameters file. In the current version, this file must have a csv like structure, each entry in the row is separated by **;**. So the table look as follows:

|Parameter 1|   Parameter 2    | Parameter 3  |
| ---- |:-------------:| -----:|
|210   |"entry for the switch1"   |10.10.10.10 |
|220   |"entry for the switch2"   |12.1.2.1    |
|212   |"entry for the switch3"   |2.3.4.5     |

As you can see the order of the parameters is exactly the same as there appear in the command file. Each row stands for parameters for one switch, they also must be in the same order as they are in the switch list, otherwise, you can execute commands on other switch than you expected.

Parameters file structure:
```
210;"entry for the switch1";10.10.10.10
220;"entry for the switch2";12.1.2.1
212;"entry for the switch3";2.3.4.5
```


