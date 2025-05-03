# ACS OPC File Encoder

This application encodes the CNC user parameters within each `.nc` file of a directory using a map of identification integers which relate the file with a specific: 1. Customer, 2. Blade, 3. Cycle, 4. ACS Revision, 5. Customer Revision. There are a dozen more of these variables that are cuurently unused.

## QT-based interface
In the `dist` directory you will find the executable for the application. This will open a QT UI which enables the user to select a particular file and encode all `.nc` files within it. The current system automatically picks up on certain keywords within the hard-coded maps to assign the user-parameter integers for the CNC. 

## Multiprocessing
Upon encoding, the system utilizes `concurrents.futures` to handle the encoding of multiple files at once. This significantly increases the speed at which files are encoded.

## Error-handling and Success
Upon encoding any directory, the user will be informed by a `QMessageBox` detailing the results of the encoding instance. If any errors are encountered, it will list the particular files it faced issues with. 

# Support
If you have any issues or need assistance, please do not hestitate to reach out.
**Phone**: (504) 451-9114
**Email**: dfallo@acskits.com