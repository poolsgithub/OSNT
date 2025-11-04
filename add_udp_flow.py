@input_validator
def add_udp_flow(
    self,
    flow: Flow,
    target_bandwidth: Bandwidth = Bandwidth("1mbit"),
    tool: str = "iperf3",
    enable_dtls: bool = False,
    server_options: dict = None,
    client_options: dict = None,
    **kwargs,
):
    """
    Add UDP or DTLS flow to experiment.

    Parameters
    ----------
    flow : Flow
        Flow to be added to experiment
    target_bandwidth : Bandwidth
        Bandwidth for UDP/DTLS stream (Default value = '1mbit')
    tool : str
        Tool to use (iperf3/netperf/openssl)
    enable_dtls : bool
        Whether to enable DTLS (Default False)
    server_options : dict, optional
        Additional server options
    client_options : dict, optional
        Additional client options
    """
    if enable_dtls:
        if tool != "openssl":
            logger.warning(
                "%s will not generate DTLS flow. For DTLS, please use 'openssl' tool.", tool
            )
            tool = "openssl"

        options = {
            "protocol": "dtls",
            "tool": tool,
            "target_bw": target_bandwidth.string_value,
        }

        # Merge user-supplied options
        user_options = {}
        if server_options:
            user_options.update(server_options)
        if client_options:
            user_options.update(client_options)
        options.update(user_options)

        # Assign random port if not provided
        if "port_no" not in options:
            options["port_no"] = random.randrange(1024, 65536)

    else:
        # Standard UDP flow
        options = {
            "protocol": "udp",
            "tool": tool,
            "target_bw": target_bandwidth.string_value,
        }

        user_options = {}
        if server_options:
            user_options.update(server_options)
        if client_options:
            user_options.update(client_options)
        options.update(user_options)

        if tool == "iperf3" and "port_no" not in options:
            options["port_no"] = random.randrange(1024, 65536)

    # Assign options to flow and add it
    flow._options = options  # pylint: disable=protected-access
    self.add_flow(flow)
