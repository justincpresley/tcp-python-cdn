from utils.packet_functions import *
from utils.basic_functions import *


def main():
    file = "ip.txt"
    list = file_into_list(file)
    print(list)


if __name__ == '__main__':
    main()