import sys

def initialize_macro(macro):
    debug = False
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg == "-h" or arg == "--help":
                print_macro_info(macro)
                print("Usage: python3 03Integration.py config_file")
                exit()
            
            if arg == "-d" or arg == "--debug":
                debug = True
                print("Debug mode activated")
            
            else:
                input_file = sys.argv[1]

    else: 
        input_file = input("Please select input File: ")
        debug = input("Debug mode? (y/n): ")
        if debug == "y":
            debug = True
            print("Debug mode activated")
        else:
            print("Debug mode deactivated")
            
    print_header()
    return input_file, debug

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