@echo off

for /d %%a in (*) do (
	copy "ffmpy_H265-MP4.py" "%%a"
	pushd "%%a"
	python "ffmpy_H265-MP4.py"
	del "ffmpy_H265-MP4.py"
	popd
)

echo Done!
pause