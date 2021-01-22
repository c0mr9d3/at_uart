# at_uart
Send commands on UART to AT device on serial port
<br/><br/>
File commands.db contain aliases on AT commands.<br/>
Usage: at_uart.py [options]<br/><br/>

Options:<br/>
  -h, --help            show this help message and exit<br/>
  -e COMMAND, --execute=COMMAND<br/>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;execute AT command once<br/>
  -b BAUDRATE, --baudrate=BAUDRATE<br/>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;set speed for comport. On default is equal 9600<br/>
  -a alias, --add=alias<br/>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;add alias on command. Use with option --command<br/>
  -c COMMAND, --command=COMMAND<br/>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;used for set alias on command<br/>
  -p PORT, --port=PORT  set comport<br/>
  
