from disk import Disk
def main(script, command):
    d = Disk()
    if command == 'upload':
        d.upload()
    elif command == 'download':
        d.download()


if __name__ == '__main__' :
    import sys
    main( * sys.argv)
