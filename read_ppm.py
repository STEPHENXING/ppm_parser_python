import matplotlib.pyplot as plt
import numpy as np
from itertools import groupby


def read_ppm_p6(path_to_ppm_file):
    arr = np.fromfile(path_to_ppm_file, dtype=np.uint8)
    height, max_val, desc_info_len, width = dump_desc_info(arr)

    if max_val > 255: # 10 bits, need more logit
        buf = arr[desc_info_len:]
        img = buf.reshape(-1, width, 3, 2)
        print(img.shape)

        img10 = np.ones((height, width, 3), dtype=np.uint16)

        img10[:, :, :] = img[:, :, :, 0] * 256 + img[:, :, :, 1]

        # print(np.max(img10), np.min(img10), img10.size, img10.shape)
        assert np.max(img10) <= max_val

        return img10, width, height, max_val
    else: # 8 bits is easy
        buf = arr[desc_info_len:]
        img = buf.reshape(-1, width, 3)
        print(img.shape)
        return img, width, height, max_val


def dump_desc_info(arr):
    a = arr[:1024]  # desc info will not be more than 1024 bytes

    # 10 is the ascii code for enter/new line
    sections = [list(g) for k, g in groupby(a, lambda x: x != 10) if k]
    # read desc sections
    my_len = 0
    has_comments = False
    for i, section in enumerate(sections):
        # print(f"Section {i + 1}: {section}")
        my_len += len(section)
        if i == 1:
            if section[0] == 35:  # ascii code for '#'
                has_comments = True

        if i >= 2:
            break


    if has_comments:
        i += 1
        my_len += len(sections[i])
        total_len = my_len + 4
    else:
        total_len = my_len + 3

    # push the desc info back into txt
    desc = arr[:total_len]
    desc.tofile("desc_temp.txt")

    # open it as text
    type, comment, resolution, max_val, width, height = None, None, None, None, None, None
    with open("desc_temp.txt", 'r') as f:
        type = f.readline()
        assert type.startswith("P6")
        if has_comments:
            comment = f.readline()
            assert comment[0].startswith("#")
        resolution = f.readline()
        width, height = resolution.split()
        width = int(width)
        height = int(height)
        max_val = f.readline()
        max_val = int(max_val)
    return height, max_val, total_len, width


def show_10bit_image(img, width, height, max_val):
    img_show = np.zeros((height, width, 3), dtype=np.float64)
    img_show = img * 1.0 / (max_val + 1)

    plt.imshow(img_show, interpolation='nearest')
    plt.show()


def show_8bit_image(img, width, height, max_val):
    # img_show = np.zeros((height, width, 3), dtype=np.float64)
    # img_show = img * 1.0 / (max_val + 1)

    plt.imshow(img, interpolation='nearest')
    plt.show()


def export_rgb(img, width, height, new_name):
    img.tofile(new_name)


if __name__ == '__main__':
    path_to_ppm_file = "samples/kangaroo_p6_replicated.ppm"
    img, width, height, max_val = read_ppm_p6(path_to_ppm_file)
    if max_val > 255:
        show_10bit_image(img, width, height, max_val)
    else:
        show_8bit_image(img, width, height, max_val)

    #
    # new_name = path_to_ppm_file.replace(".ppm", f"_{width}x{height}_10b.rgb").replace("_P420_", "_")
    # export_rgb(img, width, height, new_name)
