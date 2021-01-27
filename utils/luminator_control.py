import serial
import  time

class LuminatorControl():
    cmd_list = {"open_ch1": "$11000",
                "close_ch1":  "$21000",
                "open_ch2": "$12000",
                "close_ch2": "$22000",
                "open_ch3": "$13000",
                "close_ch3": "$23000",
                "initial_setting": ("$31064","$32028","$33028"),
                "set_part": ("$11000","$12000","$23000"),
                "set_doc": ("$21000","$12000","$23000"),
                #"set_normal": ("$21000","$22000","$23000")
                }

    def __init__(self,port_name="COM7"):
        try:
            portx = port_name
            bps = 9600
            timex = 5
            self.ser = serial.Serial(portx, bps, timeout=timex)
        except Exception as e:
            self.ser = None
            print("---异常---：",e)
        self.init_luminator()

    def set_part(self):
        self.runCMD(self.cmd_list["set_part"])

    def set_doc(self):
        self.runCMD(self.cmd_list["set_doc"])

    def init_luminator(self):
        self.runCMD(self.cmd_list["initial_setting"])

    def runCMD(self,cmd_list:list):
        if self.ser is None: return
        for cmd_str in cmd_list:
            check_str = self.checkcode(cmd_str)
            send_str = cmd_str+check_str
            self.ser.write(send_str.encode("gbk"))
            time.sleep(0.1)
            out = self.ser.read()
            print("out: ",out)

    def UseCH(self,ptime=0.1,cmd_str=""):
        if self.ser is None: return
        self.ser.write("$1100014".encode("gbk"))
        time.sleep(ptime)
        out = self.ser.read()
        print("out:",out)
        self.ser.write("$2100017".encode("gbk"))
        time.sleep(ptime)
        out = self.ser.read()
        print("out:",out)
        pass

    @staticmethod
    def checkcode(serial_str):
        bytes = bytearray(serial_str,"gbk")
        check_code = bytes[0]
        for i in range(1,len(bytes)):
            check_code = check_code ^ bytes[i]
        str_code = "{:x}".format(check_code)
        return str_code

    def __del__(self):
        if self.ser is not None: self.close()


if __name__ == "__main__":
    lc = LuminatorControl()
    lc.runCMD(lc.cmd_list["set_part"])
    # while True:
    #     sc.UseCH(ptime=0.5)