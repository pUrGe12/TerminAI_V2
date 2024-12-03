import subprocess

try:
    ans = subprocess.check_output(["python3", "--version"], text=True)
    print(ans)

except subprocess.CalledProcessError as e:
    print(f"Command failed with return code {e.returncode}")

try:
    command = "echo 'abcd' > file.txt"
    output = subprocess.run(command, shell=True, text=True, check = True, capture_output=True)
    print(output.stdout)
except Exception as e:
    print(e)