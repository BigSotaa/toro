"""
MAIN MODULE
"""
import argparse
import socket
import socks

from modules.analyzer import LinkTree
from modules.getweblinks import get_links
from modules.color import color
from modules.pagereader import display_ip
from modules.getemails import get_mails
from modules.updater import updateTor
from modules.savefile import saveJson
from modules.info import execute_all

# GLOBAL CONSTS
LOCALHOST = "127.0.0.1"
DEFPORT = 9050

# TorBot VERSION
__VERSION = "1.2"


def connect(address, port):
    """ Establishes connection to port

    Assumes port is bound to localhost, if host that port is bound to changes
    then change the port

    Args:
        address: address for port to bound to
        port: Establishes connect to this port
    """

    if address and port:
        socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, address, port)
    elif address:
        socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, address, DEFPORT)
    elif port:
        socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, LOCALHOST, port)
    else:
        socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, LOCALHOST, DEFPORT)

    socket.socket = socks.socksocket  # Monkey Patch our socket to tor socket

    def getaddrinfo(*args):
        """
        Overloads socket function for std socket library
        Check socket.getaddrinfo() documentation to understand parameters.
        Simple description below:
        argument - explanation (actual value)
        socket.AF_INET - the type of address the socket can speak to (IPV4)
        sock.SOCK_STREAM - creates a stream connecton rather than packets
        6 - protocol being used is TCP
        Last two arguments should be a tuple containing the address and port
        """
        return [(socket.AF_INET, socket.SOCK_STREAM, 6,
                 '', (args[0], args[1]))]
    socket.getaddrinfo = getaddrinfo


def header():
    """
    Prints out header ASCII art
    """
    license_msg = color("LICENSE: GNU Public License", "red")
    banner = r"""
                           __  ____  ____  __        ______
                          / /_/ __ \/ __ \/ /_  ____/_  __/
                         / __/ / / / /_/ / __ \/ __ \/ /
                        / /_/ /_/ / _, _/ /_/ / /_/ / /
                        \__/\____/_/ |_/_____/\____/_/  V{VERSION}
              """.format(VERSION=__VERSION)
    banner = color(banner, "red")

    title = r"""
                                    {banner}
                    #######################################################
                    #  TorBot - An OSINT Tool for Deep Web                #
                    #  GitHub : https://github.com/DedsecInside/TorBot    #
                    #  Help : use -h for help text                        #
                    #######################################################
                                  {license_msg} 
              """

    title = title.format(license_msg=license_msg, banner=banner)
    print(title)


def get_args():
    """
    Parses user flags passed to TorBot
    """
    parser = argparse.ArgumentParser(prog="TorBot",
                                     usage="Gather and analayze data from Tor sites.")
    parser.add_argument("-v", "--version", action="store_true",
                        help="Show current version of TorBot.")
    parser.add_argument("--update", action="store_true",
                        help="Update TorBot to the latest stable version")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-u", "--url", help="Specifiy a website link to crawl")
    parser.add_argument("--ip", help="Change default ip of tor")
    parser.add_argument("-p", "--port", help="Change default port of tor")
    parser.add_argument("-s", "--save", action="store_true",
                        help="Save results in a file")
    parser.add_argument("-m", "--mail", action="store_true",
                        help="Get e-mail addresses from the crawled sites")
    parser.add_argument("-e", "--extension", action='append', dest='extension',
                        default=[],
                        help=' '.join(("Specifiy additional website",
                                       "extensions to the list(.com , .org, .etc)")))
    parser.add_argument("-l", "--live", action="store_true",
                        help="Check if websites are live or not (slow)")
    parser.add_argument("-i", "--info", action="store_true",
                        help=' '.join(("Info displays basic info of the",
                                       "scanned site, (very slow)")))
    parser.add_argument("--visualize", action="store_true",
                        help="Visualizes tree of data gathered.")
    parser.add_argument("--download", action="store_true",
                        help="Downloads tree of data gathered.")
    return parser.parse_args()


def main():
    """
    TorBot's Core
    """
    args = get_args()
    connect(args.ip, args.port)
    link = args.url

    # If flag is -v, --update, -q/--quiet then user only runs that operation
    # because these are single flags only
    if args.version:
        print("TorBot Version:" + __VERSION)
        exit()
    if args.update:
        updateTor()
        exit()
    if not args.quiet:
        header()
    # If url flag is set then check for accompanying flag set. Only one
    # additional flag can be set with -u/--url flag
    if args.url:
        display_ip()
        # -m/--mail
        if args.mail:
            emails = get_mails(link)
            print(emails)
            if args.save:
                saveJson('Emails', emails)
        # -i/--info
        elif args.info:
            execute_all(link)
            if args.save:
                print('Nothing to save.\n')
        elif args.visualize:
            tree = LinkTree(link, args.extension)
            tree.show()
        elif args.download:
            tree = LinkTree(link, args.extension)
            file_name = str(input("File Name (.pdf/.png/.svg): "))
            tree.save(file_name)
        else:
            # Golang library isn't being used.
            # links = go_linker.GetLinks(link, LOCALHOST, PORT, 15)
            links = get_links(link, ext=args.extension, display_status=args.live)
            if args.save:
                saveJson("Links", links)
    else:
        print("usage: torBot.py [-h] [-v] [--update] [-q] [-u URL] [-s] [-m]",
              "[-e EXTENSION] [-l] [-i]")

    print("\n\n")


if __name__ == '__main__':

    try:
        main()

    except KeyboardInterrupt:
        print("Interrupt received! Exiting cleanly...")
