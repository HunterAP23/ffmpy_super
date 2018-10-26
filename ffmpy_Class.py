import ffmpy
from pymediainfo import MediaInfo

class ffmpy_Class:
    def __init__(self, thisFile):
        # MediaInfo object.
        self.fileName = thisFile
        self.fileInfo = MediaInfo.parse(thisFile)
        self.probe = get_ffprobe_info(thisFile)

    def if_video():
        trackCount = len(fileInfo.tracks)
        if trackCount == 0:
            return False
        for track in fileInfo.tracks:
            if track.track_type == "Video":
                isTrue = True
            elif trackCount == 1:
                return False
            else:
                return True

    # Gets stream data from ffprobe and MediaInfo for later use.
    def get_ffprobe_info(fileName):
        #probeCommands = shlex.split(" -select_streams v:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1")
        probeCommands = shlex.split(" -select_streams v:0 -show_entries -of default=noprint_wrappers=1:nokey=1")
        probeCommands.append(repr(fileName))

        thePipe = subprocess.PIPE

        myProbe = ffmpy.FFprobe(r"ffprobe.exe", probeCommands) #Put the path to ffmpeg here

        myTuple = myProbe.run(None, thePipe, thePipe)
        self.probe = myTuple
        #return myTuple

    def get_bitrate():


        if tmpRate1 == b'N/A\r\nN/A\r\n' or tmpRate1 == "" or tmpRate1 == b'N/A\r\n':
            print_both("ffprobe got N/A for bitrate. Attempting alternate method.\n")

            media_info = MediaInfo.parse(fileName)
            for track in media_info.tracks:
                if track.track_type == 'Video':
                    print_both("bit_rate: " + str(track.bit_rate / 1000))
                    return track.bit_rate / 1000
        else:
            tmpRate = []
            tmpRate = tmpRate1.split(b'\r')[0].decode()

            bitrate = ''.join(tmpRate)
            bitrate = math.ceil(int(bitrate) / 1024)

            sys.stderr.write("Original Video Stream Bitrate: " + str(int(bitrate)) + ".\n")
            return bitrate


        if isTrue:
            print_both("File is confirmed as video.")
            if fileName.endswith("_comp.mp4"):
                print_both("File is already compressed, skipping.")
                return (False, None)
            else:
                tmpName = fileName.split(".")
                if "_comp" in tmpName[-2]:
                    print_both("Compressed file already exists, skipping.")
                    return (False, None)
                else:
                    tmpName[-1] = "comp"
                    tmpName.append("mp4")
                    exportedName = []
                    count = 0
                    for element in tmpName:
                        if element == "comp":
                            exportedName.append(str("_" + element + ".mp4"))
                            break
                        else:
                            if count == 0:
                                newFileName = str(element)
                                count += 1
                            else:
                                newFileName = str("_" + element)
                            exportedName.append(newFileName)
                    exportedName = "".join(exportedName)
                    return (True, exportedName)
        else:
            print_both("Skipping non-video file " + str(filename) + ".")
            return (False, None)
