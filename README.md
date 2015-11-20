# parallel-cli
Executing network device commands on multiple devices.
usage: pcli.py [-h] [-u USER] -c COMMAND [COMMAND ...] switch [switch ...]

Execute command on multiple switches.

positional arguments:
  switch                The switch list or file the list of switches to run command on.

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  User to use in order to log into switches. By default admin.
  -c COMMAND [COMMAND ...], --command COMMAND [COMMAND ...]
                        [REQUIRED] Command to perform on the switches.Commands can be read from the file (preffered)or from command line example: -c "show clock" "show interfaces" "etc ..".
                        File should contain all the commands that you would type on the switch to obtain desired output.\nExample:\n
                            conf t\n
                            int vlan 30\n
                            no ip addr\n
                            shutdown\n
                            end\n
TAGS: network, ios, cisco, force10, dell, hp, configuration, automated configuration
