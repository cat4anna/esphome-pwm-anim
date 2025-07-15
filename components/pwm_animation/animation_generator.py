import math, random
import datetime
import zlib
import argparse
import zlib

from generator.animation_info import AnimInfo


def sin_anim(x, x_frac, power, **kw):
    value = math.pow(math.sin(math.pi*x_frac), power)
    return value

def linear(x, offset, steep, **kw):
    x = (x-offset) * steep
    return x


def modulo_signum(x, modulo, **kw):
    x = (x % modulo ) - modulo/2
    if x < 0:
        return -1
    if x > 0:
        return 1
    return 0

def saw_test(x, arg):
    modulo = 20

    base_x = math.trunc(x / modulo) * modulo
    delta = x - base_x

    s = modulo_signum(x, modulo=modulo)
    if s == 1:
        s=2

    v = base_x + delta * s
    # / MAX_VALUE

    return v


def random_color(name):
    random.seed(zlib.crc32(name.encode("utf-8")))
    r = random.randrange(64, 200)
    g = random.randrange(64, 200)
    b = random.randrange(64, 200)
    return f"#{r:02x}{g:02x}{b:02x}"

def make_plot(func, name, arg={}, hide=False):
    return AnimInfo(
        func = func,
        name = name,
        arg = arg,
        hide = hide,
    )

def init_plot_data():
    return [
        make_plot(sin_anim, "Sin10",    hide=False,  arg={"power": 5}),
        # make_plot(linear,   "Steep2",   hide=False,  arg={"steep": 2, "offset":MAX_VALUE/8}),
        # make_plot(linear,   "Steep1_5", hide=False,  arg={"steep": 1.5, "offset":MAX_VALUE/8}),
        # make_plot(saw_test, "Saw",      hide=False,  arg={"steep": 1.5, "offset":MAX_VALUE/8}),
    ]


def write_plots_to_file(plots, fname):
    now = datetime.datetime.now()
    with open(fname, "w") as f:
        f.write("// Do not edit. This file is generated.\n")
        f.write(f"// Date: {now}\n")
        f.write("\n")
        f.write("#pragma once\n")
        f.write("\n")
        f.write("#include \"plot_header.h\"\n")
        f.write("\n")
        f.write("namespace AnimationData {\n")
        f.write("\n")
        for i in plots:
            i.write_c_data(f)
        f.write("\n")
        f.write(f"static constexpr unsigned kAnimationCount = {len(plots)};\n")
        f.write("\n")
        f.write("enum class AnimationType : uint16_t {\n")
        for i in plots:
            f.write(f"    {i.full_name},\n")
        f.write("    Count,\n")
        f.write("    Custom,\n")
        f.write("    Default = 0,\n")
        f.write("};\n")
        f.write("static_assert(static_cast<unsigned>(AnimationType::Count) == kAnimationCount);\n")
        f.write("\n")
        f.write("static constexpr std::array<AnimationInfo, kAnimationCount> kAnimationArray = {\n")
        for i in plots:
            f.write(f"    AnimationInfo{{{i.c_full_name_data}, {i.c_full_name_size}, \"{i.name}\"}},\n")
        f.write("};\n")
        f.write("\n")
        f.write("}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('--write', help='Description for write argument', action="store_true")
    args = vars(parser.parse_args())

    plots = init_plot_data()

    if args['write']:
        f = "generated_plots.h"
        write_plots_to_file(plots, f)
        print(f"Writing to file {f}")
