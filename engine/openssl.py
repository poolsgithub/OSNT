# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Run OpenSSL commands to set up TLS or DTLS client/server."""

import subprocess
import os
from .exec import exec_exp_commands, exec_subprocess_in_background

current_dir = os.getcwd()
files = f"{current_dir}/temp/"
os.makedirs(os.path.dirname(files), exist_ok=True)


def run_openssl_client(ns_id, destination_ip, run_time, protocol="tls", out=None, err=None):
    """
    Run OpenSSL client inside a network namespace.

    Parameters
    ----------
    ns_id : str
        Network namespace to run the client from
    destination_ip : str
        IP address of the destination namespace
    run_time : int
        Duration to run the client
    protocol : str
        "tls" (TCP) or "dtls" (UDP)
    """

    assert protocol in ("tls", "dtls"), "Protocol must be 'tls' or 'dtls'"

    # Generate private key and certificate for the client
    exec_exp_commands(f"openssl genrsa -out {files}/client.key 2048")
    exec_exp_commands(
        f"""openssl req -new -key {files}/client.key -out {files}/client.csr \
        -subj /C=IN/ST=./L=./O=./OU=./CN=./emailAddress=."""
    )
    exec_exp_commands(
        f"openssl x509 -req -in {files}/client.csr -signkey {files}/client.key -out {files}/client.crt"
    )

    # Select OpenSSL mode and port based on protocol
    flag = "-dtls" if protocol == "dtls" else ""
    port = 4433 if protocol == "dtls" else 443

    # Message loop (works for both TCP and UDP)
    command = f"""
    ip netns exec {ns_id} timeout {run_time}s bash -c '
        while true; do echo "Test message"; sleep 1; done |
        openssl s_client {flag} -connect {destination_ip}:{port} \
        -cert {files}/client.crt -key {files}/client.key -quiet'
    """

    with subprocess.Popen(command, shell=True, stdout=out, stderr=err) as process:
        process.communicate()
        return process.returncode


def run_openssl_server(ns_id, protocol="tls"):
    """
    Run OpenSSL server inside a network namespace.

    Parameters
    ----------
    ns_id : str
        Network namespace to run the server from
    protocol : str
        "tls" (TCP) or "dtls" (UDP)
    """

    assert protocol in ("tls", "dtls"), "Protocol must be 'tls' or 'dtls'"

    # Generate private key and certificate for the server
    exec_exp_commands(f"openssl genrsa -out {files}/server.key 2048")
    exec_exp_commands(
        f"""openssl req -new -x509 -key {files}/server.key -out {files}/server.crt \
        -days 365 -subj /C=IN/ST=./L=./O=./OU=./CN=./emailAddress=."""
    )

    # Select OpenSSL mode and port based on protocol
    flag = "-dtls" if protocol == "dtls" else ""
    port = 4433 if protocol == "dtls" else 443

    # Run server in background
    return exec_subprocess_in_background(
        f"""ip netns exec {ns_id} openssl s_server {flag} \
        -key {files}/server.key -cert {files}/server.crt \
        -accept {port} -quiet"""
    )
