import nessaid_readline.key as key
from nessaid_readline.readkey import readkey
from nessaid_readline.readline import NessaidReadline


def help():
    print("Press 'q'/ESC to exit")
    print("Press 'h' for help")
    print("Press 'i' for input")
    print("Press 'r' for readline")
    print("Press 'm' for toggling masked mode")


def main():

    masked = False
    readline = NessaidReadline()

    help()

    while True:
        ch = readkey()
        if ch.lower() == 'h':
            help()
        elif ch.lower() in ['q', key.ESC]:
            break
        elif ch.lower() == 'i':
            i = readline.input("Bare input: ", mask_input=masked)
            print(i)
            print("Read: ", i)
        elif ch.lower() == 'm':
            masked = not masked
            print("Masked mode:", masked)
        elif ch.lower() == 'r':
            r = readline.readline("Readline: ")
            print("Read: ", r)

if __name__ == '__main__':
    main()