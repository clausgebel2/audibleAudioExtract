import sys
import subprocess
import re
import shutil
import os

def ffprobe_exists():
    path = shutil.which("ffprobe")

    if path is None:
        return False
    else:
        return True


def get_activation_bytes(aax_file):
    if ffprobe_exists():
        program = "ffprobe"
        args = [aax_file]

        # Execution of ffprobe application and options
        try:
            completed_process = subprocess.run([program] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               text=True)

            # ffprobe exits with an error -> output is in stderr
            output = completed_process.stderr

        except subprocess.CalledProcessError as e:
            print("Error:", e)

        # Find combination of numbers and letters following 'checksum == '
        pattern = r'\bfile checksum ==\s*([a-fA-F0-9]+)'
        match = re.search(pattern, output)

        if match:
            # Save pattern element in brackets
            activation_bytes = match.group(1)
            print("Audible activation bytes: " + activation_bytes)
            return activation_bytes
        else:
            print("Error: no activation bytes found.")
            return "Error: no activation bytes found."
    else:
        print("Please install 'ffmpeg'.")


def get_authentication_code(aax_name):
    authentication_code = get_activation_bytes(aax_name)
    if authentication_code == -1:
        print("Error: could not read activation byte.")
        exit(-1)

    os.chdir("tables")
    program = "./rcrack"
    args = [".", "-h", authentication_code]
    # Execution of rcrack application and options
    try:
        completed_process = subprocess.run([program] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        output = completed_process.stdout

    except subprocess.CalledProcessError as e:
        print("Error:", e)

    # Find combination of numbers and letters following 'hex: '
    pattern = r'hex:([0-9]+)'
    match = re.search(pattern, output)
    os.chdir("..")

    if match:
        # Save pattern element in brackets
        authentication_code = match.group(1)
        print("Audible authentication code: " + authentication_code)
        return(authentication_code)
    else:
        print("Error: no authentication code found.")
        return "Error: no authentication code found."


def create_mp3(aax_path):
    # make aax2mp3 file executable
    os.chmod("aax2mp3/aax2mp3", 0o755)

    authentication_code = get_authentication_code(aax_path)

    # Create output folder
    if not os.path.exists("output"):
        os.mkdir("output")

    # Copy aax file to output folder
    shutil.copy(aax_path, "output/")

    # Get aax filename
    aax_file = aax_path
    if "/" in aax_path:
        pattern = r'\/([^\/]+)$'
        match = re.search(pattern, aax_path)
        if match:
            aax_file = match.group(1)

    # aax2mp3 application and options to be executed
    programm = "aax2mp3/aax2mp3"
    options = ["-i", "output/" + aax_file, "-a", authentication_code]

    command = [programm] + options

    # Start process
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, text=True)

    # Read output of the processes
    stdout, stderr = process.communicate()

    # Show output on terminal
    print(stdout)
    print(stderr)
    returnval = process.returncode
    if returnval == 0:
        print("Successfully converted!")

    # Delete copied aax_file
    os.remove("output/" + aax_file)


if len(sys.argv) < 2:
    print("Please add the name of the aax files as argument.")
    sys.exit(1)
file_name = sys.argv[1]
create_mp3(file_name)




