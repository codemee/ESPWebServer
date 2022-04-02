import ESPWebServer
import network
import machine

GPIO_NUM = 2 # Builtin led (D4)
# Get pin object for controlling builtin LED
pin = machine.Pin(GPIO_NUM, machine.Pin.OUT)
pin.on() # Turn LED off (it use sinking input)

# Dictionary for template file
ledData = {
    "title":"Remote LED",
    "color":"red",
    "status":"Off",
    "switch":"on"
}

# Update information
def updateInfo(socket):
    global ledData, color, status, switch
    ledData["color"] = "red" if pin.value() else "green"
    ledData["status"] = "Off" if pin.value() else "On"
    ledData["switch"] = "on" if pin.value() else "off"
    ESPWebServer.ok(
        socket,
        "200",
        ledData["status"])

def handleStop(socket):
    ESPWebServer.ok(
        socket,
        "200",
        "stopped")
    running = False
    ESPWebServer.close()

def handlePost(socket, args, contenttype, content):
    ESPWebServer.ok(
        socket,
        "200",
        method+" "+contenttype+" "+content.decode('UTF-8'))

# Handler for path "/cmd?led=[on|off]"
def handleCmd(socket, args):
    if 'led' in args:
        if args['led'] == 'on':
            pin.off()
        elif args['led'] == 'off':
            pin.on()
        updateInfo(socket)
    else:
        ESPWebServer.err(socket, "400", "Bad Request")

# handler for path "/switch"
def handleSwitch(socket, args):
    pin.value(not pin.value()) # Switch back and forth
    updateInfo(socket)

# Start the server @ port 8899
# ESPWebServer.begin(8899)
ESPWebServer.begin() # use default 80 port

# Register handler for each path
# ESPWebServer.onPath("/", handleRoot)
ESPWebServer.onPath("/cmd", handleCmd)
ESPWebServer.onPath("/switch", handleSwitch)
ESPWebServer.onPostPath("/post", handlePost)

# Setting the path to documents
ESPWebServer.setDocPath("/")

# Setting data for template
ESPWebServer.setTplData(ledData)

# Setting maximum Body Content Size. Set to 0 to disable posting. Default: 1024
ESPWebServer.setMaxContentLength(1024)

def checkForClients():
    try:
        while True:
            # Let server process requests
            ESPWebServer.handleClient()
    except:
        ESPWebServer.close()

checkForClients()

