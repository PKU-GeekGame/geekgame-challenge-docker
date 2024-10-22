import base64
import OpenSSL
import os
import time
import fcntl
import signal
import tempfile
import hashlib
import flaglib
import atexit
import subprocess
from datetime import datetime
import threading
import select
import sys
import random
import math

def getenv(envn,default=""):
    ret=os.environ.get(envn,default).strip()
    if ret=="":
        ret=default
    return ret

tmp_path = "/dev/shm/hackergame"
tmp_flag_path = "/dev/shm"
conn_interval = int(os.environ["hackergame_conn_interval"])
token_timeout = int(os.environ["hackergame_token_timeout"])
challenge_timeout = int(os.environ["hackergame_challenge_timeout"])
pids_limit = int(os.environ["hackergame_pids_limit"])
mem_limit = os.environ["hackergame_mem_limit"]
flag_path = os.environ["hackergame_flag_path"]
flag_rule = os.environ["hackergame_flag_rule"]
challenge_docker_name = os.environ["hackergame_challenge_docker_name"]
readonly = int(getenv("hackergame_readonly", "0"))
mount_points = getenv("hackergame_mount_points", "[]")
mount_points=eval(mount_points)
use_network = int(getenv("hackergame_use_network","0"))
cpus = float(getenv("hackergame_cpus", "0.1"))
disk_limit = getenv("hackergame_disk_limit","4G")

lxcfs_opts = '-v /var/lib/lxcfs/proc/cpuinfo:/proc/cpuinfo:ro -v /var/lib/lxcfs/proc/diskstats:/proc/diskstats:ro -v /var/lib/lxcfs/proc/meminfo:/proc/meminfo:ro -v /var/lib/lxcfs/proc/stat:/proc/stat:ro -v /var/lib/lxcfs/proc/swaps:/proc/swaps:ro -v /var/lib/lxcfs/proc/uptime:/proc/uptime:ro -v /var/lib/lxcfs/proc/slabinfo:/proc/slabinfo:ro -v /var/lib/lxcfs/sys/devices/system/cpu:/sys/devices/system/cpu:ro'

with open("cert.pem") as f:
    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())


def validate(token):
    try:
        id, sig = token.split(":", 1)
        sigr = base64.urlsafe_b64decode(sig)
        assert sig==base64.urlsafe_b64encode(sigr).decode()
        OpenSSL.crypto.verify(cert, sigr, id.encode(), "sha256")
        return id
    except Exception:
        return None


def try_login(id):
    os.makedirs(tmp_path, mode=0o700, exist_ok=True)
    fd = os.open(os.path.join(tmp_path, id), os.O_CREAT | os.O_RDWR)
    fcntl.flock(fd, fcntl.LOCK_EX)
    with os.fdopen(fd, "r+") as f:
        data = f.read()
        now = int(time.time())
        if data:
            last_login, balance = data.split()
            last_login = int(last_login)
            balance = int(balance)
            last_login_str = (
                datetime.fromtimestamp(last_login).isoformat().replace("T", " ")
            )
            balance += now - last_login
            if balance > conn_interval * 3:
                balance = conn_interval * 3
        else:
            balance = conn_interval * 3
        wait = conn_interval - balance
        if wait>0:
            print(f'\n--- 连接失败 [wait={wait}] ---')
            print(f'连接频率过快，请等待 {wait} 秒后重试。')
            return False
        balance -= conn_interval
        f.seek(0)
        f.truncate()
        f.write(str(now) + " " + str(balance))
        return True


def check_token():
    signal.alarm(token_timeout)
    token = input("Please input your token: ").strip()
    id = validate(token)
    if not id:
        print("Invalid token")
        exit(-1)
    if not try_login(id):
        exit(-1)
    signal.alarm(0)
    return token, id


def generate_flags(token):
    functions = {}
    for method in ["partitioned", "leet"]:
        def wrap(func):
            def f(*args):
                return func(*args, token=token)
            return f
        functions[method] = wrap(getattr(flaglib, method))

    if flag_path:
        flag = eval(flag_rule, functions, {"token": token})
        if isinstance(flag, tuple):
            return dict(zip(flag_path.split(","), flag))
        else:
            return {flag_path: flag}
    else:
        return {}


def generate_flag_files(flags):
    flag_files = {}
    for flag_path, flag in flags.items():
        with tempfile.NamedTemporaryFile("w", delete=False, dir=tmp_flag_path) as f:
            f.write(flag + "\n")
            fn = f.name
        # os.chmod(fn, 0o444)
        os.chmod(fn, 0o666)#allow overwrite
        flag_files[flag_path] = fn
    return flag_files


def cleanup():
    if child_docker_id:
        subprocess.run(
            f"docker rm -f {child_docker_id}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    for file in flag_files.values():
        try:
            os.unlink(file)
        except FileNotFoundError:
            pass


def create_docker(flag_files, id):
    cpusets = [str(x) for x in os.sched_getaffinity(0)]
    cpusets = random.sample(cpusets, min(len(cpusets), math.ceil(max(cpus*1.5+.99, 3))))
    cmd = (
        f"docker create --init --rm -i "
        f"--pids-limit {pids_limit} -m {mem_limit} --memory-swap -1 --cpus {cpus} --cpuset-cpus {','.join(cpusets)} "
        f"-e hackergame_token=$hackergame_token "
        f"{lxcfs_opts} "
    )

    if not use_network:
        cmd += "--network none "

    if readonly:
        cmd += "--read-only "
    
    cmd+=f"--storage-opt size={disk_limit} "

    if challenge_docker_name.endswith("-challenge") or challenge_docker_name.endswith("_challenge"):
        name_prefix = challenge_docker_name[:-10]
    else:
        name_prefix = challenge_docker_name

    timestr = datetime.now().strftime("%m%d_%H%M%S_%f")[:-3]
    child_docker_name = f"{name_prefix}_u{id}_{timestr}"
    cmd += f'--name "{child_docker_name}" '

    with open("/etc/hostname") as f:
        hostname = f.read().strip()
    with open("/proc/self/mountinfo") as f:
        for part in f.read().split('/'):
            if len(part) == 64 and part.startswith(hostname):
                docker_id = part
                break
        else:
            raise ValueError('Docker ID not found')
    prefix = f"/var/lib/docker/containers/{docker_id}/mounts/shm/"

    for flag_path, fn in flag_files.items():
        flag_src_path = prefix + fn.split("/")[-1]
        # cmd += f"-v {flag_src_path}:{flag_path}:ro "
        cmd += f"-v {flag_src_path}:{flag_path}:rw "

    for fsrc, fdst in mount_points:
        cmd += f"-v {fsrc}:{fdst} "

    cmd += challenge_docker_name

    return subprocess.check_output(cmd, shell=True).decode().strip()


def run_docker(child_docker_id):
#    cmd = f"timeout -s 9 {challenge_timeout} docker start -i {child_docker_id}"
#    cmd = f"timeout -k 1 {challenge_timeout} docker start -i {child_docker_id}"
#    p = subprocess.run(cmd, shell=True)
    p = subprocess.run(['timeout','-s','9',"{challenge_timeout}",'docker','start','-i',"{child_docker_id}"])
    print(f'\n--- 程序已退出 [retcode={p.returncode}] ---')

def clean_on_socket_close():
    p = select.poll()
    p.register(sys.stdin, select.POLLHUP | select.POLLERR | select.POLLRDHUP)
    p.poll()
    cleanup()

if __name__ == "__main__":
    child_docker_id = None
    flag_files = {}
    atexit.register(cleanup)
    t = threading.Thread(target=clean_on_socket_close, daemon=True)
    t.start()
    timer = threading.Timer(token_timeout+challenge_timeout+5, cleanup)
    timer.start()

    token, id = check_token()
    os.environ["hackergame_token"] = token
    flags = generate_flags(token)
    flag_files = generate_flag_files(flags)
    child_docker_id = create_docker(flag_files, id)
    run_docker(child_docker_id)
