# cloudshell-L1-Telescent

## Installation
Copy to c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers on CloudShell machine:
- Telescent.exe
- telescent_runtime_configuration.json

To customize SSH port and resource family and model names, edit:
- telescent_runtime_configuration.json
- telescent_datamodel.xml

Import telescent_datamodel.xml into Resource Manager

## Usage
- Import telescent_datamodel.xml into Resource Manager
- Create L1 switch resource and set IP address, username, password
- In Configuration view in Resource Manager, push Auto Load
- Create multiple DUTs each with a port subresource
- In Connections view of the L1 switch resource, connect the DUT ports
- Create an empty reservation and add DUTs
- Create a route between two DUTs
- Connect the route
- See log files in c:\Program Files (x86)\QualiSystems\CloudShell\Server\Logs\Telescent_*\


## Port Representation

### Telescent Overview

Each physical Telescent port has a number from 0 to 1055. This number can be obtained by multiplying the row number in the output of "switchstate" by 12 and adding the zero-based column number. Note that there are alwasy 12 columns and the label "C12" is shown erroneously.

Within each port are an input and an output that are connected to other ports, independent of each other. The input of one port is connected to the output of another port, and vice versa.

For example on port 123 the input can be connected to the output of port 321 and the output can be connected to the input of 654.

A port can be connected to loop back to itself. For example the input of port 123 can be connected to the output of port 123.

### CloudShell Representation
For each Telescent port number, there is a CloudShell resource. The input and output are encompassed by the single resource.

The port resource name is the logical port number. The physical port numbers of the associated input and output are stored in the address.

By default, the resource for port 123 represents the input connection for port 123 and the output connection for port 123.  The address field of the port resource in this case will simply be 123.

### CloudShell Logical Port Remapping

It is possible to remap the CloudShell Telescent port resource.
The input and output of the logical port can be remapped independently.

The logical port number is stored in the resource name.
The remapped addresses are stored in the address of the port resource.

For example, if port resource 123 is redefined to refer to the input of 456 and the output of port 789,
the port resource will be named 123 and the address will be "456-789".

The mapping is defined in telescent_runtime_configuration.json.

For example:

     1 {
     2   // ...
     3  "driver_variable": {
     4    // ...
     5    "dict_logical_port_to_physical_input_port": {
     6      "1047": "1048",
     7      "1048": "1047",
     8      "1050": "1053",
     9      "1051": "1054"
    10    },
    11    "dict_logical_port_to_physical_output_port": {
    12      "1047": "1048",
    13      "1048": "1047",
    14      "1049": "1052"
    15    }
    16
    17 }

In this example, ports 1047 and 1048 are completely swapped. This requires 4 lines:
- Line 6: The INPUT for logical port 1047 is now the INPUT connection of physical port 1048
- Line 7: The INPUT for logical port 1048 is now the INPUT connection of physical port 1047
- Line 12: The OUTPUT for logical port 1047 is now the OUTPUT connection of physical port 1048
- Line 13: The OUTPUT for logical port 1048 is now the OUTPUT connection of physical port 1047

Whenever the port resource 1047 is used in CloudShell, the port number 1048 will be passed to the switch, and vice versa.

In lines 8, 9, and 14, some other arbitrary substitutions are performed, demonstrating that it is not necessary to remap the input and output together.

The administrator is responsible for defining a mapping that does not associate the input or output of any port
with more than one logical port resource. The example does not meet this condition.

This mapping implicitly exists until specific ports are overridden:

    "dict_logical_port_to_physical_input_port": {
        "0": "0",
        "1": "1",
        ...
        "1055": "1055"
    },
    "dict_logical_port_to_physical_output_port": {
        "0": "0",
        "1": "1",
        ...
        "1055": "1055"
    },





## Development

- Python must be in PATH
- PyInstaller must be installed
  - http://www.pyinstaller.org/
  - Download and extract the zip
  - python setup.py install
- git must be installed
  - https://git-scm.com/
  - Enable Git Bash if asked
- In Git Bash:
  - git clone https://github.com/QualiSystems/cloudshell-core.git
  - git clone https://github.com/QualiSystems/cloudshell-L1-networking-core.git
  - git clone https://github.com/QualiSystems/cloudshell-L1-Telescent.git

compile_driver.bat
- Run from a regular command prompt
- Kills all Telescent.exe 
- Copies to c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers:
  - .\dist\Telescent.exe 
  - .\telescent_runtime_configuration.json
- Copies to compiled_driver folder:
  - .\dist\Telescent.exe
  - .\telescent_runtime_configuration.json
  - .\telescent_datamodel.xml

## Notes
Note that the unidirectional MapClearTo must perform a bidirectional "unlock" on the port because of an apparent bug in the switch (or at least the simulator) where "unallocate" fails on a port that was only unidirectionally unlocked.

### Login with RSA key
To log in to the switch with an RSA private key:

- Store it in this filename: C:\Windows\System32\Config\systemprofile\.ssh\id_rsa
- Ensure that the Paramiko connect() function in CloudShell-L1-networking-core ssh_session.py is called with look_for_keys=True
 
If id_rsa is found, the Password attribute of the switch will be used to decrypt the key file, and Username will still be used directly during login.
