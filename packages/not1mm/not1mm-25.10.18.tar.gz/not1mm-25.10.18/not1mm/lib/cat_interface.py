"""
K6GTE, CAT interface abstraction
Email: michael.bridak@gmail.com
GPL V3

rig.cwio_set_wpm          n:i  set cwio WPM
rig.cwio_text             i:s  send text via cwio interface
rig.cwio_send             n:i  cwio transmit 1/0 (on/off)
command lines to test the CW API via XMLRPC

Setting WPM
curl -d "<?xml version='1.0'?><methodCall><methodName>rig.cwio_set_wpm</methodName><params><param><value><i4>28</i4></value></param></params></methodCall>" http://localhost:12345

Setting the text to send
curl -d "<?xml version='1.0'?><methodCall><methodName>rig.cwio_text</methodName><params><param><value><string>test test test</string></value></param></params></methodCall>" http://localhost:12345

Enable send
curl -d "<?xml version='1.0'?><methodCall><methodName>rig.cwio_send</methodName><params><param><value><i4>1</i4></value></param></params></methodCall>" http://localhost:12345
"""

import logging
import socket
import xmlrpc.client
import http

if __name__ == "__main__":
    print("I'm not the program you are looking for.")

logger = logging.getLogger("cat_interface")


class CAT:
    """CAT control rigctld or flrig"""

    def __init__(self, interface: str, host: str, port: int) -> None:
        """
        Computer Aided Tranceiver abstraction class.
        Offers a normalized rigctld or flrig interface.

        Takes 3 inputs to setup the class.

        A string defining the type of interface, either 'flrig' or 'rigctld'.

        A string defining the host, example: 'localhost' or '127.0.0.1'

        An interger defining the network port used.
        Commonly 12345 for flrig, or 4532 for rigctld.

        Exposed methods are:

        get_vfo()

        get_mode()

        get_power()

        get_ptt()

        set_vfo()

        set_mode()

        set_power()

        A variable 'online' is set to True if no error was encountered,
        otherwise False.
        """
        self.server = None
        self.rigctrlsocket = None
        self.interface = interface.lower()
        self.host = host
        self.port = port
        self.online = False
        self.rigctld_bw = "0"
        self.fake_radio = {
            "vfo": "14032000",
            "mode": "CW",
            "bw": "500",
            "power": "100",
            "modes": ["CW", "USB", "LSB", "RTTY"],
            "ptt": False,
        }

        if self.interface == "flrig":
            if not self.__check_sane_ip(self.host):
                self.online = False
                return

            target = f"http://{self.host}:{self.port}"
            logger.debug("%s", target)
            self.server = xmlrpc.client.ServerProxy(target)
            self.online = True
            try:
                _ = self.server.main.get_version()
            except (
                ConnectionRefusedError,
                xmlrpc.client.Fault,
                http.client.BadStatusLine,
                socket.error,
                socket.gaierror,
            ):
                self.online = False
        elif self.interface == "rigctld":
            if not self.__check_sane_ip(self.host):
                self.online = False
                return
            self.__initialize_rigctrld()
        elif self.interface == "fake":
            self.online = True
            logger.debug("Using Fake Rig")
        return

    def __check_sane_ip(self, ip: str) -> bool:
        """check if IP address look normal"""
        x = ip.split(".")
        if len(x) != 4:
            return False
        for y in x:
            if not y.isnumeric():
                return False
        return True

    def __initialize_rigctrld(self):
        try:
            logger.debug("Connecting to rigctrld")
            self.rigctrlsocket = socket.socket()
            self.rigctrlsocket.settimeout(0.1)
            self.rigctrlsocket.connect((self.host, self.port))
            logger.debug("Connected to rigctrld")
            self.online = True
        except (
            ConnectionRefusedError,
            TimeoutError,
            OSError,
            socket.error,
            socket.gaierror,
        ) as exception:
            self.rigctrlsocket = None
            self.online = False
            logger.debug("%s", f"{exception}")

    def reinit(self):
        """reinitialise rigctl"""
        if self.interface == "rigctld":
            self.__initialize_rigctrld()

    def __get_serial_string(self):
        """Gets any serial data waiting"""
        dump = ""
        thegrab = ""
        if self.rigctrlsocket is None:
            return ""
        if hasattr(self.rigctrlsocket, "settimeout"):
            self.rigctrlsocket.settimeout(0.1)
            try:
                while True and hasattr(self.rigctrlsocket, "recv"):
                    thegrab = self.rigctrlsocket.recv(1024).decode()
                    dump += thegrab
                    if thegrab == "":
                        break
            except (socket.error, UnicodeDecodeError):
                ...
            # self.rigctrlsocket.settimeout(0.1)
        # logger.debug("%s", dump)
        return dump

    def sendvoicememory(self, memoryspot=1):
        """..."""
        if self.interface == "rigctld":
            return self.__sendvoicememory_rigctld(memoryspot)

    def __sendvoicememory_rigctld(self, memoryspot=1):
        """..."""
        try:
            self.online = True
            self.rigctrlsocket.send(bytes(f"+\\send_voice_mem {memoryspot}\n", "utf-8"))
            info = self.__get_serial_string()
            logger.debug("%s", info)
            return
        except socket.error as exception:
            self.online = False
            logger.debug("%s", f"{exception}")
            self.rigctrlsocket = None
            return

    def sendcw(self, texttosend):
        """..."""
        logger.debug(f"{texttosend=} {self.interface=}")
        if self.interface == "flrig":
            self.sendcwxmlrpc(texttosend)
        elif self.interface == "rigctld":
            self.sendcwrigctl(texttosend)

    def sendcwrigctl(self, texttosend):
        """Send text via rigctld"""
        if self.rigctrlsocket is not None:
            try:
                self.online = True
                if hasattr(self.rigctrlsocket, "send"):
                    self.rigctrlsocket.send(bytes(f"b{texttosend}\n", "utf-8"))
                else:
                    self.rigctrlsocket = None
                    self.online = False
                    return False
                info = self.__get_serial_string()
                logger.debug("%s", info)
                return True
            except socket.error as exception:
                self.online = False
                logger.debug("setvfo_rigctld: %s", f"{exception}")
                self.rigctrlsocket = None
                return False
        self.__initialize_rigctrld()
        return False

    def stopcwrigctl(self):
        """Stop CW via rigctld"""
        if self.rigctrlsocket is not None:
            try:
                self.online = True
                if hasattr(self.rigctrlsocket, "send"):
                    self.rigctrlsocket.send(bytes("\\stop_morse\n", "utf-8"))
                else:
                    self.rigctrlsocket = None
                    self.online = False
                    return False
                _ = self.__get_serial_string()
                return True
            except socket.error as exception:
                self.online = False
                logger.debug("setvfo_rigctld: %s", f"{exception}")
                self.rigctrlsocket = None
                return False
        self.__initialize_rigctrld()
        return False

    def set_rigctl_cw_speed(self, speed):
        """Set CW speed via rigctld"""
        if self.rigctrlsocket is not None:
            try:
                self.online = True
                if hasattr(self.rigctrlsocket, "send"):
                    self.rigctrlsocket.send(bytes(f"L KEYSPD {speed}\n", "utf-8"))
                else:
                    self.rigctrlsocket = None
                    self.online = False
                    return
                info = self.__get_serial_string()
                logger.debug("%s", info)
                return
            except socket.error as exception:
                self.online = False
                logger.debug("set_level_rigctld: %s", f"{exception}")
                self.rigctrlsocket = None
                return
        self.__initialize_rigctrld()

    def sendcwxmlrpc(self, texttosend):
        """Add text to flrig's cw send buffer."""
        logger.debug(f"{texttosend=}")
        try:
            self.online = True
            self.server.rig.cwio_text(texttosend)
            return
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
        ) as exception:
            self.online = False
            logger.debug("%s", f"{exception}")
        return False

    def set_flrig_cw_send(self, send: bool) -> None:
        """Turn on flrig cw keyer send flag."""
        if self.interface == "rigctld":
            return
        try:
            self.online = True
            self.server.rig.cwio_send(int(send))
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
            ValueError,
        ) as exception:
            self.online = False
            logger.debug("%s", f"{exception}")

    def set_flrig_cw_speed(self, speed):
        """Set flrig's CW send speed"""
        if self.interface == "rigctld":
            return
        try:
            self.online = True
            self.server.rig.cwio_set_wpm(int(speed))
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
            ValueError,
        ) as exception:
            self.online = False
            logger.debug("%s", f"{exception}")

    def get_vfo(self) -> str:
        """Poll the radio for current vfo using the interface"""
        vfo = ""
        if self.interface == "flrig":
            vfo = self.__getvfo_flrig()
        elif self.interface == "rigctld":
            vfo = self.__getvfo_rigctld()
            if "RPRT -" in vfo:
                vfo = ""
        else:
            vfo = self.fake_radio.get("vfo", "")
        return vfo

    def __getvfo_flrig(self) -> str:
        """Poll the radio using flrig"""
        try:
            self.online = True
            vfo_value = self.server.rig.get_vfo()
            logger.debug(f"{vfo_value=}")
            return vfo_value
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
            AttributeError,
        ) as exception:
            self.online = False
            logger.debug(f"{exception=}")
        return ""

    def __getvfo_rigctld(self) -> str:
        """Returns VFO freq returned from rigctld"""
        if self.rigctrlsocket is not None:
            try:
                self.online = True
                if hasattr(self.rigctrlsocket, "send"):
                    self.rigctrlsocket.send(b"|f\n")
                else:
                    self.rigctrlsocket = None
                    self.online = False
                    return ""
                report = self.__get_serial_string().strip()
                logger.debug("%s", report)
                if "get_freq:|" in report and "RPRT 0" in report:
                    seg_rpt = report.split("|")
                    return seg_rpt[1].split(" ")[1]
            except (socket.error, IndexError) as exception:
                self.online = False
                logger.debug(f"{exception=}")
                self.rigctrlsocket = None
            return ""

        self.__initialize_rigctrld()
        return ""

    def get_mode(self) -> str:
        """Returns the current mode filter width of the radio"""
        mode = ""
        if self.interface == "flrig":
            mode = self.__getmode_flrig()
        elif self.interface == "rigctld":
            mode = self.__getmode_rigctld()
        else:
            mode = self.fake_radio.get("mode")
        return mode

    def __getmode_flrig(self) -> str:
        """Returns mode via flrig"""
        # QMX ['CW-U', 'CW-L', 'DIGI-U', 'DIGI-L']
        # 7300 ['LSB', 'USB', 'AM', 'FM', 'CW', 'CW-R', 'RTTY', 'RTTY-R', 'LSB-D', 'USB-D', 'AM-D', 'FM-D']
        try:
            self.online = True
            mode_value = self.server.rig.get_mode()
            logger.debug(f"{mode_value=}")
            return mode_value
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
            AttributeError,
        ) as exception:
            self.online = False
            logger.debug("%s", f"{exception}")
        return ""

    def __getmode_rigctld(self) -> str:
        """Returns mode vai rigctld"""
        # QMX 'DIGI-U DIGI-L CW-U CW-L' or 'LSB', 'USB', 'CW', 'FM', 'AM', 'FSK'
        # 7300 'AM CW USB LSB RTTY FM CWR RTTYR PKTLSB PKTUSB FM-D AM-D'
        if self.rigctrlsocket is not None:
            try:
                self.online = True
                if hasattr(self.rigctrlsocket, "send"):
                    self.rigctrlsocket.send(b"|m\n")
                else:
                    self.rigctrlsocket = None
                    self.online = False
                    return ""
                # get_mode:|Mode: CW|Passband: 500|RPRT 0
                report = self.__get_serial_string().strip()
                logger.debug("%s", report)
                if "get_mode:|" in report and "RPRT 0" in report:
                    seg_rpt = report.split("|")
                    self.rigctld_bw = seg_rpt[2].split(" ")[1]
                    return seg_rpt[1].split(" ")[1]
            except IndexError as exception:
                logger.debug("%s", f"{exception}")
            except socket.error as exception:
                self.online = False
                logger.debug("%s", f"{exception}")
                self.rigctrlsocket = None
            return ""
        self.__initialize_rigctrld()
        return ""

    def get_bw(self):
        """Get current vfo bandwidth"""
        if self.interface == "flrig":
            return self.__getbw_flrig()
        elif self.interface == "rigctld":
            return self.__getbw_rigctld()
        else:
            return self.fake_radio.get("bw")

    def __getbw_flrig(self):
        """return bandwidth"""
        try:
            self.online = True
            bandwidth = self.server.rig.get_bw()
            logger.debug(f"{bandwidth=}")
            return bandwidth[0]
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
            AttributeError,
        ) as exception:
            self.online = False
            logger.debug("getbw_flrig: %s", f"{exception}")
            return ""

    def __getbw_rigctld(self):
        """return bandwidth"""
        return self.rigctld_bw

    def get_power(self):
        """Get power level from rig"""
        if self.interface == "flrig":
            return self.__getpower_flrig()
        elif self.interface == "rigctld":
            return self.__getpower_rigctld()
        else:
            return self.fake_radio.get("power", "100")

    def __getpower_flrig(self):
        try:
            self.online = True
            return self.server.rig.get_power()
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
        ) as exception:
            self.online = False
            logger.debug("getpower_flrig: %s", f"{exception}")
            return ""

    def __getpower_rigctld(self):
        if self.rigctrlsocket is not None:
            try:
                self.online = True
                if hasattr(self.rigctrlsocket, "send"):
                    self.rigctrlsocket.send(b"|l RFPOWER\n")
                else:
                    self.rigctrlsocket = None
                    self.online = False
                    return ""
                # get_level: RFPOWER|0.000000|RPRT 0
                report = self.__get_serial_string().strip()
                logger.debug("%s", report)
                if "get_level: RFPOWER|" in report and "RPRT 0" in report:
                    seg_rpt = report.split("|")
                    return int(float(seg_rpt[1]) * 100)
            except socket.error as exception:
                self.online = False
                logger.debug("getpower_rigctld: %s", f"{exception}")
                self.rigctrlsocket = None
            return ""

    def get_ptt(self):
        """Get PTT state"""
        if self.interface == "flrig":
            return self.__getptt_flrig()
        elif self.interface == "rigctld":
            return self.__getptt_rigctld()
        return False

    def __getptt_flrig(self):
        """Returns ptt state via flrig"""
        try:
            self.online = True
            return self.server.rig.get_ptt()
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
        ) as exception:
            self.online = False
            logger.debug("%s", f"{exception}")
        return "0"

    def __getptt_rigctld(self):
        """Returns ptt state via rigctld"""
        if self.rigctrlsocket is not None:
            try:
                self.online = True
                if hasattr(self.rigctrlsocket, "send"):
                    self.rigctrlsocket.send(b"t\n")
                else:
                    self.rigctrlsocket = None
                    self.online = False
                    return "0"
                ptt = self.__get_serial_string()
                logger.debug("%s", ptt)
                ptt = ptt.strip()
                return ptt
            except socket.error as exception:
                self.online = False
                logger.debug("%s", f"{exception}")
                self.rigctrlsocket = None
        return "0"

    def get_mode_list(self):
        "Get a list of modes supported by the radio"
        if self.interface == "flrig":
            return self.__get_mode_list_flrig()
        elif self.interface == "rigctld":
            return self.__get_mode_list_rigctld()
        else:
            return self.fake_radio.get("modes")
        return False

    def __get_mode_list_flrig(self):
        """Returns list of modes supported by the radio"""
        try:
            self.online = True
            mode_list = self.server.rig.get_modes()
            logger.debug(f"{mode_list=}")
            return mode_list
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
            AttributeError,
        ) as exception:
            self.online = False
            logger.debug("%s", f"{exception}")
        return ""

    def __get_mode_list_rigctld(self):
        """Returns list of modes supported by the radio"""
        # Mode list: AM CW USB LSB RTTY FM CWR RTTYR
        if self.rigctrlsocket:
            try:
                self.online = True
                if hasattr(self.rigctrlsocket, "send"):
                    self.rigctrlsocket.send(b"1\n")
                else:
                    self.rigctrlsocket = None
                    self.online = False
                    return ""
                dump = self.__get_serial_string()
                for line in dump.splitlines():
                    if "Mode list:" in line:
                        modes = line.split(":")[1].strip()
                        return modes
                return ""
            except socket.error as exception:
                self.online = False
                logger.debug("%s", f"{exception}")
                self.rigctrlsocket = None
        return ""

    def set_vfo(self, freq: str) -> bool:
        """Sets the radios vfo"""
        try:
            if self.interface == "flrig":
                return self.__setvfo_flrig(freq)
            elif self.interface == "rigctld":
                return self.__setvfo_rigctld(freq)
            else:
                self.fake_radio["vfo"] = str(freq)
                return True
        except ValueError:
            ...
        return False

    def __setvfo_flrig(self, freq: str) -> bool:
        """Sets the radios vfo"""
        try:
            self.online = True
            return self.server.rig.set_frequency(float(freq))
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
            AttributeError,
        ) as exception:
            self.online = False
            logger.debug("setvfo_flrig: %s", f"{exception}")
        return False

    def __setvfo_rigctld(self, freq: str) -> bool:
        """sets the radios vfo"""
        if self.rigctrlsocket is not None:
            try:
                self.online = True
                if hasattr(self.rigctrlsocket, "send"):
                    self.rigctrlsocket.send(bytes(f"|F {freq}\n", "utf-8"))
                else:
                    self.rigctrlsocket = None
                    self.online = False
                    return False
                info = self.__get_serial_string()
                logger.debug("%s", info)
                return True
            except socket.error as exception:
                self.online = False
                logger.debug("setvfo_rigctld: %s", f"{exception}")
                self.rigctrlsocket = None
                return False
        self.__initialize_rigctrld()
        return False

    def set_mode(self, mode: str) -> bool:
        """Sets the radios mode"""
        if self.interface == "flrig":
            return self.__setmode_flrig(mode)
        elif self.interface == "rigctld":
            return self.__setmode_rigctld(mode)
        else:
            self.fake_radio["mode"] = mode
            return True

    def __setmode_flrig(self, mode: str) -> bool:
        """Sets the radios mode"""
        try:
            self.online = True
            logger.debug(f"{mode=}")
            set_mode_result = self.server.rig.set_mode(mode)
            logger.debug(f"self.server.rig.setmode(mode) = {set_mode_result}")
            return set_mode_result
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
            AttributeError,
        ) as exception:
            self.online = False
            logger.debug(f"{exception=}")
        return False

    def __setmode_rigctld(self, mode: str) -> bool:
        """sets the radios mode"""
        if self.rigctrlsocket:
            try:
                self.online = True
                # logger.debug(f"\nM {mode} 0\n")
                if hasattr(self.rigctrlsocket, "send"):
                    self.rigctrlsocket.send(bytes(f"\n|M {mode} 0\n", "utf-8"))
                else:
                    self.rigctrlsocket = None
                    self.online = False
                    return False
                info = self.__get_serial_string()
                logger.debug("%s", info)
                return True
            except socket.error as exception:
                self.online = False
                logger.debug("setmode_rigctld: %s", f"{exception}")
                self.rigctrlsocket = None
                return False
        self.__initialize_rigctrld()
        return False

    def set_power(self, power):
        """Sets the radios power"""
        if self.interface == "flrig":
            return self.__setpower_flrig(power)
        elif self.interface == "rigctld":
            return self.__setpower_rigctld(power)
        else:
            self.fake_radio["power"] = str(power)
            return True

    def __setpower_flrig(self, power):
        try:
            self.online = True
            return self.server.rig.set_power(power)
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
            AttributeError,
        ) as exception:
            self.online = False
            logger.debug("setpower_flrig: %s", f"{exception}")
            return False

    def __setpower_rigctld(self, power):
        if power.isnumeric() and int(power) >= 1 and int(power) <= 100:
            rig_cmd = bytes(f"|L RFPOWER {str(float(power) / 100)}\n", "utf-8")
            try:
                self.online = True
                if hasattr(self.rigctrlsocket, "send"):
                    self.rigctrlsocket.send(rig_cmd)
                else:
                    self.rigctrlsocket = None
                    self.online = False
                    return
                info = self.__get_serial_string()
                logger.debug("%s", info)
            except socket.error:
                self.online = False
                self.rigctrlsocket = None

    def ptt_on(self):
        """turn ptt on/off"""
        if self.interface == "flrig":
            return self.__ptt_on_flrig()
        elif self.interface == "rigctld":
            return self.__ptt_on_rigctld()
        else:
            self.fake_radio["ptt"] = True
            return True

    def __ptt_on_rigctld(self):
        """Toggle PTT state on"""

        # T, set_ptt 'PTT'
        # Set 'PTT'.
        # PTT is a value: ‘0’ (RX), ‘1’ (TX), ‘2’ (TX mic), or ‘3’ (TX data).

        # t, get_ptt
        # Get 'PTT' status.
        # Returns PTT as a value in set_ptt above.

        rig_cmd = bytes("|T 1\n", "utf-8")
        logger.debug("%s", f"{rig_cmd}")
        try:
            self.online = True
            if hasattr(self.rigctrlsocket, "send"):
                self.rigctrlsocket.send(rig_cmd)
            else:
                self.rigctrlsocket = None
                self.online = False
                return
            info = self.__get_serial_string()
            logger.debug("%s", info)
        except socket.error:
            self.online = False
            self.rigctrlsocket = None

    def __ptt_on_flrig(self):
        """Toggle PTT state on"""
        try:
            self.online = True
            return self.server.rig.set_ptt(1)
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
            AttributeError,
        ) as exception:
            self.online = False
            logger.debug("%s", f"{exception}")
        return "0"

    def ptt_off(self):
        """turn ptt on/off"""
        if self.interface == "flrig":
            return self.__ptt_off_flrig()
        elif self.interface == "rigctld":
            return self.__ptt_off_rigctld()
        else:
            self.fake_radio["ptt"] = False
            return True

    def __ptt_off_rigctld(self):
        """Toggle PTT state off"""
        rig_cmd = bytes("|T 0\n", "utf-8")
        logger.debug("%s", f"{rig_cmd}")
        try:
            self.online = True
            if hasattr(self.rigctrlsocket, "send"):
                self.rigctrlsocket.send(rig_cmd)
            else:
                self.rigctrlsocket = None
                self.online = False
                return
            into = self.__get_serial_string()
            logger.debug("%s", into)
        except socket.error:
            self.online = False
            self.rigctrlsocket = None

    def __ptt_off_flrig(self):
        """Toggle PTT state off"""
        try:
            self.online = True
            return self.server.rig.set_ptt(0)
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
            AttributeError,
        ) as exception:
            self.online = False
            logger.debug("%s", f"{exception}")
        return "0"

    def send_cat_string(self, cmdstr=""):
        """send a raw cat string to radio"""
        cmdstr = cmdstr.strip()
        test1 = cmdstr.replace(" ", "")
        if test1 == "":
            return True
        working = cmdstr
        test2 = [" ", " x", " X", "\\"]
        test3 = "0123456789ABCDEF "  # trailing space
        ishex = False
        # does this look like hex?
        for c2 in test2:
            if c2 in working:
                ishex = True
        if ishex:
            working = working.replace("x", "")
            working = working.replace("X", "")
            working = working.replace("\\", "")
            working = working.upper()
            # should be space-delimited now
            # any illegal chars?
            for c3 in working:
                if c3 not in test3:
                    logger.debug(f"Bad char in command string: [{cmdstr}]")
                    return True
            # hex checks out so far
            spacesok = True
            for i in range(len(working)):
                if (i + 1) % 3 == 0:  # every 3rd char
                    if working[i] != " ":
                        spacesok = False
            if not spacesok:
                logger.debug(f"Bad delimiters in cmd string: [{cmdstr}]")
                return True
        else:
            """not hex, but plain ascii text - do nothing"""

        if self.interface == "flrig":
            return self.__send_cat_string_flrig(working, ishex)
        elif self.interface == "rigctld":
            return self.__send_cat_string_rigctld(working, ishex)
        else:
            return True

    def __send_cat_string_flrig(self, cmd, thisishex):
        """convert string to flrig format, send to flrig"""
        if thisishex:
            # make string " x" delimited (again) for flrig
            cmd = "x" + cmd
            cmd = cmd.replace(" ", " x")
        else:
            """ascii - do nothing"""
        logger.debug("%s", f"Sending rig command: [{cmd}]")
        try:
            return self.server.rig.cat_string(cmd)
        except (
            ConnectionRefusedError,
            xmlrpc.client.Fault,
            http.client.BadStatusLine,
            http.client.CannotSendRequest,
            http.client.ResponseNotReady,
            AttributeError,
        ) as exception:
            self.online = False
            logger.debug("%s", f"{exception}")
        return "0"

    def __send_cat_string_rigctld(self, cmd, thisishex):
        """convert string to rigctld format, send to rigctld"""
        if not self.rigctrlsocket:
            return 0
        if thisishex:
            # make string "\0x" delimited for rigctld
            cmd = cmd.replace(" ", "\\0x")
            cmd = "|w \\0x" + cmd
        else:
            cmd = "|w " + cmd
        bcmd = bytes(cmd, "utf-8")
        logger.debug("%s", f"Sending rig command: [{bcmd}]")

        try:
            if hasattr(self.rigctrlsocket, "send"):
                self.rigctrlsocket.send(bcmd)
        except socket.error:
            logger.debug("Socket error!")
            self.online = False
            self.rigctrlsocket = None
            return 0
