import struct
import base64
import math, random
import zlib


def clamp_and_round(x, max_value):
    if x < 0:
        x = 0
    if x > 1:
        x = 1
    return round(x * max_value)

class AnimInfo:
    DATA_LENGTH = 256
    MAX_VALUE = 255

    SIGNATURE = 1398030659

    def __init__(self, func, name, arg,
                 hide = False,
                 x = None,
                 ):
        self.func = func
        self.arg = arg

        self.x = list(range(self.DATA_LENGTH))

        self.name = name
        self.full_name = f"Anim{name}"
        self.c_full_name_data = f"kAnim{name}Data"
        self.c_full_name_size = f"kAnim{name}Size"

        self.plot_hide = hide

        self.y = []
        if self.func:
            self.regenerate()

    def regenerate(self):
        self.y = []
        for x in self.x:
            y = self.func(x, x_frac = x/self.DATA_LENGTH, **self.arg)
            self.y.append(clamp_and_round(y, self.MAX_VALUE))

    def get_c_array_data(self):
        return ", ".join([str(i) for i in self.y])

    def data_size(self):
        return len(self.y)

    def get_custom_anim_data(self):
        signature = struct.pack("<I", self.SIGNATURE)
        crc = struct.pack("<H", 0)
        total_size = struct.pack("<H", 0)

        header_size = struct.pack("b", 16)
        name_length = struct.pack("b", len(self.name))
        name_offset = struct.pack("<H", 0)

        name = bytearray(self.name, "ascii") + bytearray([0])
        data = bytearray()
        for item in self.y:
            data = data + struct.pack("<B", item)

        thresholds_offset = struct.pack("<H", len(name))
        thresholds_length = struct.pack("<H", self.data_size())

        def get():
            return signature + crc + total_size + header_size + name_length + name_offset + thresholds_offset + thresholds_length + name + data

        pre_crc_data = get()
        # crc = struct.pack("<H", 0) # zlib.crc32(get())
        total_size = struct.pack("<H", len(pre_crc_data))

        return get()

    def get_encoded_custom_anim_data(self):
        data = self.get_custom_anim_data()
        # print(data.hex())
        # compressed = zlib.compress(data, level=9)
        return base64.b64encode(data).decode("ascii")

    def write_c_data(self, f):
        f.write(f"constexpr uint16_t {self.c_full_name_size} = {self.data_size()};\n")
        f.write(f"constexpr AnimationThresholdType {self.c_full_name_data}[{self.c_full_name_size}] = {{"),
        f.write(self.get_c_array_data())
        f.write("};\n")
        f.write(f"static constexpr char {self.c_full_name_data}Custom[] = R\"==({self.get_encoded_custom_anim_data()})==\";\n")
