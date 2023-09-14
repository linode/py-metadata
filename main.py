import os

from metadata import MetadataClient


def main():
    client = MetadataClient()
    # All of these responses are handled as DataClasses,
    # allowing IDEs to properly use completions.
    instance_info = client.get_instance()
    network_info = client.get_network()
    ssh_info = client.get_ssh_keys()
    user_data = client.get_user_data()
    print("Instance ID:", instance_info)
    print("Public IPv4:", network_info)
    print("SSH Keys:", "; ".join(ssh_info.users.root))
    #print("SSH Keys:", "; ", ssh_info.users)
    print("User Data:", user_data)


if __name__ == "__main__":
    main()