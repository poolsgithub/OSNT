# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

""" Runs openssl command to setup TLS/DTLS flows """

import copy
import logging
from time import sleep
from functools import partial
from .runnerbase import Runner
from ...topology_map import TopologyMap
from ...engine.openssl import run_openssl_client, run_openssl_server

logger = logging.getLogger(__name__)


class OpensslRunner(Runner):
    """
    Runs openssl client and server

    Attributes
    ----------
    ns_id : str
        network namespace to run openssl from
    destination_ip : str
        ip address of the destination namespace
    start_time : num
        time at which openssl is to run
    run_time : num
        total time to run openssl for
    """

    # pylint: disable=too-many-arguments
    def __init__(self, ns_id, destination_ip, start_time, run_time, dst_ns, **kwargs):
        """
        Constructor to initialize openssl runner

        Parameters
        ----------
        ns_id : str
            network namespace to run openssl from
        destination_ip : str
            ip address of the destination namespace
        start_time : num
            time at which openssl is to run
        run_time : num
            total time to run openssl for
        dst_ns : str
            network namespace to run openssl server in
        **kwargs
            optional arguments (e.g., protocol='dtls')
        """
        self.options = copy.deepcopy(kwargs)
        self.protocol = self.options.get("protocol", "tls")  # default to TLS
        super().__init__(ns_id, start_time, run_time, destination_ip, dst_ns)

    def run_openssl_server(self, ns_id):
        """
        OpenSSL s_server is a command-line tool included with the OpenSSL cryptographic
        toolkit. It is used to create a simple SSL/TLS server for testing purposes or
        for basic encryption and authentication needs.

        This function allows you to configure a specific host to function as an
        OpenSSL server, which can handle incoming SSL/TLS connections and provide
        encryption and authentication services.

        Run openssl s_server in `ns_id`

        Parameters
        ----------
        ns_id : str
            namespace to run openssl s_server on
        """
        return_code = run_openssl_server(ns_id, protocol=self.protocol)
        if return_code != 0:
            ns_name = TopologyMap.get_node(ns_id).name
            logger.error("Error running openssl s_server at %s.", ns_name)

    def run(self):
        if self.start_time > 0:
            sleep(self.start_time)

        super().run(
            partial(
                run_openssl_client,
                self.ns_id,
                self.destination_address.get_addr(with_subnet=False),
                self.run_time,
                self.protocol,  # Pass protocol argument to client
            ),
            error_string_prefix=f"Running openssl ({self.protocol.upper()})",
        )
