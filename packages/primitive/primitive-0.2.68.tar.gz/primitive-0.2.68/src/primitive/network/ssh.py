import paramiko
import socket
import time


def test_ssh_connection(hostname, username, password=None, key_filename=None, port=22):
    """
    Tests an SSH connection to a remote host.

    Args:
        hostname (str): The hostname or IP address of the remote SSH server.
        username (str): The username for authentication.
        password (str, optional): The password for authentication. Defaults to None.
        key_filename (str, optional): Path to the private key file for authentication. Defaults to None.
        port (int, optional): The SSH port. Defaults to 22.

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )  # Auto-add new host keys

    try:
        if password:
            ssh_client.connect(
                hostname=hostname, port=port, username=username, password=password
            )
        elif key_filename:
            ssh_client.connect(
                hostname=hostname,
                port=port,
                username=username,
                key_filename=key_filename,
            )
        else:
            print(
                "Error: Either password or key_filename must be provided for authentication."
            )
            return False

        print(f"Successfully connected to {hostname} as {username}")
        return True
    except paramiko.AuthenticationException:
        print(f"Authentication failed for {username} on {hostname}")
        return False
    except paramiko.SSHException as e:
        print(f"SSH error connecting to {hostname}: {e}")
        return False
    except socket.error as e:
        print(f"Socket error connecting to {hostname}: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    finally:
        ssh_client.close()


TEN_MINUTES = 60 * 10


def wait_for_ssh(
    hostname, username, password=None, key_filename=None, port=22, timeout=TEN_MINUTES
):
    """
    Waits until an SSH connection to a remote host can be established.

    Args:
        hostname (str): The hostname or IP address of the remote SSH server.
        username (str): The username for authentication.
        password (str, optional): The password for authentication. Defaults to None.
        key_filename (str, optional): Path to the private key file for authentication. Defaults to None.
        port (int, optional): The SSH port. Defaults to 22.
        timeout (int, optional): Maximum time to wait in seconds. Defaults to 300.

    Returns:
        bool: True if the connection is successful within the timeout, False otherwise.
    """

    start_time = time.time()
    while time.time() - start_time < timeout:
        if test_ssh_connection(
            hostname, username, password=password, key_filename=key_filename, port=port
        ):
            return True
        print(f"Waiting for SSH to become available on {hostname}...")
        time.sleep(10)

    print(
        f"Timeout reached: Unable to connect to {hostname} via SSH within {timeout} seconds."
    )
    return False
