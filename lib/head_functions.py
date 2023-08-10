import sys

def initialize_macro(macro):
    user_input = dict()
    user_input["debug"] = False
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg == "-h" or arg == "--help":
                print_macro_info(macro)
                print("Usage: python3 %s.py config_file"%macro)
                exit()
            
            if arg == "-d" or arg == "--debug":
                debug = True
                user_input["debug"] = debug
                print("Debug mode activated")
            
            if arg == "-i" or arg == "--input":
                input_file = sys.argv[sys.argv.index(arg)+1]
                user_input["input_file"] = input_file
                print("Input file: %s"%input_file)
            
            if arg == "-r" or arg == "--run":
                run = sys.argv[sys.argv.index(arg)+1].split(",")
                user_input["runs"] = run
                print("Run: %s"%run)

            if arg == "-c" or arg == "--channel":
                channel = sys.argv[sys.argv.index(arg)+1].split(",")
                user_input["channels"] = channel
                print("Channel: %s"%channel)
    else: 
        user_input["input_file"] = input("Please select input File: ")
        debug_answer = input("Debug mode? (y/n): ")
        if debug_answer == "y":
            user_input["debug"] = True
            print("Debug mode activated")
        else:
            print("Debug mode deactivated")
            
    print_header()
    return user_input

def print_macro_info(macro,debug=False):
    f = open('../info/'+macro+'.txt', 'r')
    file_contents = f.read()
    print (file_contents+"\n")
    f.close
    if debug: print("----- Debug mode activated -----")

def print_header():
    f = open('../info/header.txt', 'r')
    file_contents = f.read()
    print (file_contents)
    f.close
    print("----- Starting macro -----")