import ESPWebServer
import network
import machine

GPIO_NUM = 2 # Builtin led (D4)

# Wi-Fi configuration
STA_SSID = "MEE_MI"
STA_PSK = "PinkFloyd1969"

# Disable AP interface
ap_if = network.WLAN(network.AP_IF)
if ap_if.active():
    ap_if.active(False)
  
# Connect to Wi-Fi if not connected
sta_if = network.WLAN(network.STA_IF)
if not ap_if.active():
    sta_if.active(True)
if not sta_if.isconnected():
    sta_if.connect(STA_SSID, STA_PSK)
    # Wait for connecting to Wi-Fi
    while not sta_if.isconnected(): 
        pass

# Show IP address
print("Server started @", sta_if.ifconfig()[0])

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

# Setting the path to documents
ESPWebServer.setDocPath("/")

# Setting data for template
ESPWebServer.setTplData(ledData)

try:
    while True:
        # Let server process requests
        ESPWebServer.handleClient()
except:
    ESPWebServer.close()
