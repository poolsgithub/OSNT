# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Unified OpenSSL client/server supporting both TLS (TCP) and DTLS (UDP)."""

import subprocess
import os
from .exec import exec_exp_commands, exec_subprocess_in_background

# Create a temp directory to store keys/certs
current_dir = os.getcwd()
temp_dir = os.path.join(current_dir, "temp")
os.makedirs(temp_dir, exist_ok=True)


def run_openssl_client(ns_id, destination_ip, run_time, protocol="tls", out=None, err=None):
    """
    Run OpenSSL client inside a network namespace, supporting TLS or DTLS.

    Parameters
    ----------
    ns_id : str
        Network namespace to run the client from
    destination_ip : str
        IP address of the server
    run_time : int
        Duration to run the client
    protocol : str
        "tls" for TCP, "dtls" for UDP
    """
    protocol = protocol.lower()
    assert protocol in ("tls", "dtls"), "Protocol must be 'tls' or 'dtls'"

    client_key = os.path.join(temp_dir, "client.key")
    client_csr = os.path.join(temp_dir, "client.csr")
    client_crt = os.path.join(temp_dir, "client.crt")

    # Generate key and certificate
    exec_exp_commands(f"openssl genrsa -out {client_key} 2048")
    exec_exp_commands(
        f"""openssl req -new -key {client_key} -out {client_csr} \
            -subj /C=IN/ST=./L=./O=./OU=./CN=Client/emailAddress=."""
    )
    exec_exp_commands(
        f"openssl x509 -req -in {client_csr} -signkey {client_key} -out {client_crt}"
    )

    # Set OpenSSL flags and port
    flags = "-dtls" if protocol == "dtls" else ""
    port = 4433 if protocol == "dtls" else 443

    # Prepare the client command
    message_loop = 'while true; do echo "Test message"; sleep 1; done'
    command = f"""
    ip netns exec {ns_id} timeout {run_time}s bash -c '
        {message_loop} | openssl s_client {flags} -connect {destination_ip}:{port} \
        -cert {client_crt} -key {client_key} -quiet'
    """

    with subprocess.Popen(command, shell=True, stdout=out, stderr=err) as process:
        process.communicate()
        return process.returncode


def run_openssl_server(ns_id, protocol="tls"):
    """
    Run OpenSSL server inside a network namespace, supporting TLS or DTLS.

    Parameters
    ----------
    ns_id : str
        Network namespace to run the server in
    protocol : str
        "tls" for TCP, "dtls" for UDP
    """
    protocol = protocol.lower()
    assert protocol in ("tls", "dtls"), "Protocol must be 'tls' or 'dtls'"

    server_key = os.path.join(temp_dir, "server.key")
    server_crt = os.path.join(temp_dir, "server.crt")

    # Generate key and certificate
    exec_exp_commands(f"openssl genrsa -out {server_key} 2048")
    exec_exp_commands(
        f"""openssl req -new -x509 -key {server_key} -out {server_crt} \
            -days 365 -subj /C=IN/ST=./L=./O=./OU=./CN=Server/emailAddress=."""
    )

    # Set OpenSSL flags and port
    flags = "-dtls" if protocol == "dtls" else ""
    port = 4433 if protocol == "dtls" else 443

    # Start the server in background
    return exec_subprocess_in_background(
        f"""ip netns exec {ns_id} openssl s_server {flags} \
            -key {server_key} -cert {server_crt} -accept {port} -quiet"""
    )
