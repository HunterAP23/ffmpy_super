import os
import sys
import ffmpy
import shlex
import contextlib
import math
import time
import shutil
from pymediainfo import MediaInfo

#TO DO:

#Do a check at the end to compare the original file's size to the new file's size:
#If old-size < new-size then delete the new video
#Else move files normally.
#Can make this a while loop to try different CRF values (range from 14-18 for editing, 18-23 for watching)

#Add if statements in checkFile to not check folders as files.

def print_both(phrase):
    print(str(phrase))
    myLog.write(str(phrase))

#Returns a tuple containing the following data:
#The 1st elelement is True if the file is a video, or False if it is not.
#The 2nd returns the name for the exported file if is a video.
def checkFile(fileName):
    fileInfo = MediaInfo.parse(fileName)
    isTrue = None
    trackCount = len(fileInfo.tracks)
    if trackCount == 0:
        return (False, None)
    for track in fileInfo.tracks:
        if track.track_type == "Video":
            isTrue = True
            break
        elif trackCount == 1:
            isTrue = False
        else:
            continue

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

def probe(fileName):
    probeCommands = shlex.split(" -select_streams v:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1")
    probeCommands.append(repr(fileName))

    thePipe = subprocess.PIPE

    myProbe = ffmpy.FFprobe(r"ffprobe.exe", probeCommands) #Put the path to ffmpeg here

    myTuple = myProbe.run(None, thePipe, thePipe)
    tmpRate1 = myTuple[0]

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
        newBitRate = math.ceil(int(bitrate) * 7 / 10)

        sys.stderr.write("Original Video Stream Bitrate: " + str(int(bitrate)) + ".\n")
        #return newBitRate
        return bitrate

if __name__ == '__main__':
    overallTime_Start = time.time()
    fileList = []
    if os.path.isfile("Master.log"):
        myLog = open("Master.log", 'a')
    else:
        myLog = open("Master.log", 'w')

    if not os.path.exists("source"):
        os.makedirs("source")

    if not os.path.exists("output"):
        os.makedirs("output")

    if not os.path.exists("non_comp"):
        os.makedirs("non_comp")

    for filename in os.listdir(os.getcwd()):
        print_both('Checking if file "' + str(filename) + '" is a video file.')
        myCheck = checkFile(filename)
        if myCheck[0] == False:
            print_both('-'*80)
            continue
        else:
            fileList.append([filename, myCheck[1], os.getcwd()])
            print_both("-"*80)

    for vid in fileList:
        print_both("Removing and apostrophees and quotes from file names.\n")
        while "'" in vid[0]:
            newFileName = vid[0].replace("'", "")
            os.rename(vid[0], newFileName)
            vid[0] = newFileName
        while "'" in vid[1]:
            newFileName = vid[1].replace("'", "")
            os.rename(vid[1], newFileName)
            vid[1] = newFileName

        tmpVidZero = vid[0].split('.')
        tmpVidOne = vid[1].split('.')
        tmpVidZeroFinal = []
        tmpVidOneFinal = []
        count = 0
        #tmpVidZero[-1] = "mp4":
        for element in tmpVidZero:
            #print("Element is now: " + str(element))
            if element == "mkv" or element == "mp4" or element == "avi" or element == "flv":
                tmpVidZeroFinal.append("." + str(element))
            else:
                if count == 0:
                    newFileName = str(element)
                    count += 1
                else:
                    newFileName = str("_" + element)
                tmpVidZeroFinal.append(newFileName)

        tmpVidZeroFinal = "".join(tmpVidZeroFinal)
        os.rename(vid[0], tmpVidZeroFinal)
        vid[0] = tmpVidZeroFinal

        print_both("filename is now " + str(vid[0]))

        logName = str(vid[1]).replace('_comp.mp4', '.log')
        envPath = str(vid[2]) + "\\" + str(logName)

        if ("FFREPORT" in os.environ):
            del os.environ['FFREPORT']
        os.environ["FFREPORT"] = str("file=" + str(repr(envPath)))
        #print(os.environ["FFREPORT"])

        #inp = input("Wait...")

        #finalBitrate = probe(vid[0])

        #print_both("New Video Stream Bitrate: " + str(finalBitrate) + ".\n")
        #Beginning of the encoding commands
        encoderCommands = []
        tmpCommands = "-loglevel verbose -hide_banner -report -threads 0 -hwaccel cuda -i " + repr(vid[0]) + " -map 0 -c copy -c:v libx265 -threads 0 -preset slow -crf 21 -max_muxing_queue_size 2048 "
        tmpStuff = shlex.split(tmpCommands)
        for i in range(0, len(tmpStuff), 1):
            encoderCommands.append(tmpStuff[i])

        myPass = ffmpy.FFmpeg(
            executable = r"ffmpeg.exe", #Put the path to ffmpeg here
                outputs = {
                    str(vid[1]): encoderCommands
                }
        )

        print_both("myPass.cmd: \n")
        print_both(str(myPass.cmd) + '\n')

        encodingTime_Start = time.time()
        myPass.run()
        encodingTime_End = time.time()

        print_both("Encoding time for " + str(vid[0]) + " was " + str(encodingTime_End - encodingTime_Start) + " seconds.\n")

        print("Size of original file is " + str(os.path.getsize(vid[0])))
        print("Size of exported file is " + str(os.path.getsize(vid[1])))
        #inp = input("Wait...")

        if os.path.getsize(vid[0]) <= os.path.getsize(vid[1]):
            print_both("Exported file is larger than original file, deleting exported file and moving source file.\n")
            os.remove(vid[1])
            print_both("Moving " + str(vid[0]) + " to " + str(vid[2]) + "\\" + "non_comp" + "\\" + str(vid[0]))
            shutil.move(vid[0], str(vid[2]) + "\\" + "non_comp" + "\\" + str(vid[0]))
            print_both("Moving " + str(logName) + " to " + str(vid[2]) + "\\" + "non_comp" + "\\" + str(logName))
            shutil.move(logName, str(vid[2]) + "\\" + "non_comp" + "\\" + str(logName))
            print_both("-"*80 + "\n")
        else:
            print_both("Moving files.")
            print_both("Moving " + str(vid[0]) + " to " + str(vid[2]) + "\\" + "source" + "\\" + str(vid[0]))
            shutil.move(vid[0], str(vid[2]) + "\\" + "source" + "\\" + str(vid[0]))
            print_both("Moving " + str(vid[1]) + " to " + str(vid[2]) + "\\" + "output" + "\\" + str(vid[1]))
            shutil.move(vid[1], str(vid[2]) + "\\" + "output" + "\\" + str(vid[1]))
            print_both("Moving " + str(logName) + " to " + str(vid[2]) + "\\" + "output" + "\\" + str(logName))
            shutil.move(logName, str(vid[2]) + "\\" + "output" + "\\" + str(logName))
            print_both("-"*80 + "\n")
        #inp = input("Wait...")

    overallTime_End = time.time()
    print_both("Overall time for the program was " + str(overallTime_End - overallTime_Start) + " seconds.\n")
    myLog.close()
