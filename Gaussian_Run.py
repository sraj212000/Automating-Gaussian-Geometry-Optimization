import paramiko  # For SSH connections
import os  # For file handling
import time  # For delays in monitoring loop
from scp import SCPClient  # For secure file transfers over SSH

# --- User-defined variables ---
remote_host = "10.103.146.71"
username = "msc3"
password = "newuser123"  # Consider using SSH keys instead for better security
local_dir = "D:\\Gaussian Scripts\\16new\\"
remote_dir = "/home/msc3/opt_desgin/16new/"
scratch_dir = "/scratch/users/msc3"
gaussian_root = "/apps/g16-avx2/"

def create_ssh_client(server, user, passwd):
    """
    Establishes an SSH connection to the remote server using given credentials.
    Returns the connected SSH client object.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=user, password=passwd)
    return ssh

def transfer_files(ssh, local_path, remote_path):
    """
    Transfers a file from the local system to the remote server via SCP.
    """
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(local_path, remote_path)

def generate_gaussian_job_script(gjf_filename):
    """
    Generates a PBS job script to run a Gaussian job on the cluster.
    Takes the Gaussian input filename and returns the script as a string.
    """
    base_name = os.path.splitext(gjf_filename)[0]
    script_content = f"""#!/bin/bash
#PBS -q little
#PBS -e error
#PBS -l nodes=1:ppn=8
cd $PBS_O_WORKDIR

date
echo $PBS_NODEFILE

export g16root={gaussian_root}
export GAUSS_SCRDIR={scratch_dir}
source $g16root/g16/bsd/g16.profile
export PATH=$GAUSS_EXEDIR:$PATH

time g16 < {base_name}.com >{base_name}.log
date
"""
    return script_content

try:
    print("Connecting to server...")
    ssh = create_ssh_client(remote_host, username, password)

    # Get all .com files in the local directory
    gjf_files = [f for f in os.listdir(local_dir) if f.endswith(".com")]

    if not gjf_files:
        print("No .com files found in the directory!")
        ssh.close()
        exit()

    job_ids = []  # Store job IDs for monitoring

    for gjf_file in gjf_files:
        base_name = os.path.splitext(gjf_file)[0]
        local_input_file = os.path.join(local_dir, gjf_file)
        remote_input_file = os.path.join(remote_dir, gjf_file)

        # Generate job script and save locally
        job_script_name = f"{base_name}.sh"
        local_job_script = os.path.join(local_dir, job_script_name)
        remote_job_script = os.path.join(remote_dir, job_script_name)

        with open(local_job_script, "w", newline="\n") as f:
            f.write(generate_gaussian_job_script(gjf_file))

        # Transfer input and job script to remote server
        print(f"Transferring {gjf_file} and its job script...")
        transfer_files(ssh, local_input_file, remote_input_file)
        transfer_files(ssh, local_job_script, remote_job_script)

        # Submit job via qsub
        print(f"Submitting job for {gjf_file}...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_dir} && qsub {job_script_name}")
        job_id = stdout.read().decode().strip()

        if not job_id:
            print(f"Failed to submit job for {gjf_file}.")
            continue

        print(f"Job {job_id} submitted.")
        job_ids.append((gjf_file, job_id))

    # Monitor submitted jobs periodically
    while job_ids:
        for gjf_file, job_id in job_ids[:]:
            stdin, stdout, stderr = ssh.exec_command(f"qstat {job_id}")
            job_status = stdout.read().decode()

            if job_id not in job_status:
                print(f"Job {job_id} for {gjf_file} has finished.")
                job_ids.remove((gjf_file, job_id))

        if job_ids:
            print("Waiting for jobs to complete...")
            time.sleep(30)

    print("All jobs completed.")
    ssh.close()

except Exception as e:
    print(f"Error: {e}")
