connect an esp32 to an oled display where SDA -> 14, and SCL goes to 15.\
\
import quadrupy\
\
quadrupy.led(BOOLEAN)\
quadrupy.writeScreen(STRING)\
quadrupy.clearScreen(NULL)\
quadrupy.close()\
\
programs should always end in quadrupy.close()\
programs should always clear the screen before exit.\
\
you can also use time.sleep(INT) to wait before each command.\