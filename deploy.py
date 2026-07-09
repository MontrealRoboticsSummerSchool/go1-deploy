from policy_runner import PolicyRunner

from argparse import ArgumentParser
import time
import paramiko
import sys

SLEEP_TIME = 3  # seconds


def is_sport_mode_running(ip="192.168.123.161", username="pi", password="123"):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ip, username=username, password=password, timeout=3)

        # Check if there is a sport mode process
        stdin, stdout, stderr = ssh.exec_command("pgrep -f Legged_sport")
        output = stdout.read().decode().strip()

        ssh.close()
        return len(output) > 0

    except Exception as e:
        print(f"[WARNING] Could not connect to pi ({ip}): {e}")
        return True


def main(args):
    if is_sport_mode_running():
      print("[ERROR] Sport Mode is on! Terminate it before continuing.")
      sys.exit(1)
    else:
      print("[SUCCESS] Sport Mode is off. Safe to execute deploy script.")

    print(f"Sleeping for {SLEEP_TIME} seconds...")
    for i in range(SLEEP_TIME, 0, -1):
        print(f"{i}...", end="", flush=True)
        time.sleep(1)
    print()

    print("Starting Go1 Agent with the following parameters:")
    print(f"  Server: {args.server}")
    print(f"  Port: {args.port}")
    print(f"  External Policy: {'Enabled' if args.external_policy else 'Disabled'}")
    print(f"  Model Path: {args.model}")

    go_1 = PolicyRunner(
        path=args.model,
        server=args.server,
        port=args.port,
        external_policy=args.external_policy,
    )
    go_1.init_pose()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--server", action="store_true", help="use a command server")
    parser.add_argument(
        "--external-policy", action="store_true", help="use external policy (actions from command server)"
    )
    parser.add_argument("-p", "--port", type=int, default=9292, help="port to receive commands from")
    parser.add_argument("-m", "--model", type=str, default="weights/base_policy.pt")
    arguments = parser.parse_args()

    # Validate arguments
    if arguments.external_policy and not arguments.server:
        parser.error("--external-policy requires --server")

    main(arguments)
