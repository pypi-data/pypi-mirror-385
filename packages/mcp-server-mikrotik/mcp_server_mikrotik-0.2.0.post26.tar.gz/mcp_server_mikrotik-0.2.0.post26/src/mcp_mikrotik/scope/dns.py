# Save this file as mikrotik_scope/dns.py

from typing import Optional, List
from ..connector import execute_mikrotik_command
from ..logger import app_logger

def mikrotik_set_dns_servers(
    servers: List[str],
    allow_remote_requests: bool = False,
    max_udp_packet_size: Optional[int] = None,
    max_concurrent_queries: Optional[int] = None,
    cache_size: Optional[int] = None,
    cache_max_ttl: Optional[str] = None,
    use_doh: bool = False,
    doh_server: Optional[str] = None,
    verify_doh_cert: bool = True
) -> str:
    app_logger.info(f"Setting DNS servers: {', '.join(servers)}")
    
    cmd = "/ip dns set servers=" + ",".join(servers)
    
    if allow_remote_requests:
        cmd += " allow-remote-requests=yes"
    else:
        cmd += " allow-remote-requests=no"
    
    if max_udp_packet_size:
        cmd += f" max-udp-packet-size={max_udp_packet_size}"
    
    if max_concurrent_queries:
        cmd += f" max-concurrent-queries={max_concurrent_queries}"
    
    if cache_size:
        cmd += f" cache-size={cache_size}"
    
    if cache_max_ttl:
        cmd += f" cache-max-ttl={cache_max_ttl}"
    
    if use_doh and doh_server:
        cmd += f' use-doh-server="{doh_server}"'
        cmd += f' verify-doh-cert={"yes" if verify_doh_cert else "no"}'
    
    result = execute_mikrotik_command(cmd)
    
    if not result.strip() or "failure:" not in result.lower():
        details_cmd = "/ip dns print"
        details = execute_mikrotik_command(details_cmd)
        return f"DNS settings updated successfully:\n\n{details}"
    else:
        return f"Failed to update DNS settings: {result}"

def mikrotik_get_dns_settings() -> str:
    app_logger.info("Getting DNS settings")
    
    cmd = "/ip dns print"
    result = execute_mikrotik_command(cmd)
    
    if not result:
        return "Unable to retrieve DNS settings."
    
    return f"DNS SETTINGS:\n\n{result}"

def mikrotik_add_dns_static(
    name: str,
    address: Optional[str] = None,
    cname: Optional[str] = None,
    mx_preference: Optional[int] = None,
    mx_exchange: Optional[str] = None,
    text: Optional[str] = None,
    srv_priority: Optional[int] = None,
    srv_weight: Optional[int] = None,
    srv_port: Optional[int] = None,
    srv_target: Optional[str] = None,
    ttl: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: bool = False,
    regexp: Optional[str] = None
) -> str:
    app_logger.info(f"Adding static DNS entry: name={name}")
    
    cmd = f'/ip dns static add name="{name}"'
    
    if address:
        cmd += f" address={address}"
    
    if cname:
        cmd += f' cname="{cname}"'
    
    if mx_preference is not None and mx_exchange:
        cmd += f' mx-preference={mx_preference} mx-exchange="{mx_exchange}"'
    
    if text:
        cmd += f' text="{text}"'
    
    if srv_priority is not None and srv_weight is not None and srv_port is not None and srv_target:
        cmd += f" srv-priority={srv_priority} srv-weight={srv_weight} srv-port={srv_port}"
        cmd += f' srv-target="{srv_target}"'
    
    if ttl:
        cmd += f" ttl={ttl}"
    
    if comment:
        cmd += f' comment="{comment}"'
    
    if disabled:
        cmd += " disabled=yes"
    
    if regexp:
        cmd += f' regexp="{regexp}"'
    
    result = execute_mikrotik_command(cmd)
    
    if result.strip():
        if "*" in result or result.strip().isdigit():
            entry_id = result.strip()
            details_cmd = f"/ip dns static print detail where .id={entry_id}"
            details = execute_mikrotik_command(details_cmd)
            
            if details.strip():
                return f"Static DNS entry added successfully:\n\n{details}"
            else:
                return f"Static DNS entry added with ID: {result}"
        else:
            return f"Failed to add static DNS entry: {result}"
    else:
        details_cmd = f'/ip dns static print detail where name="{name}"'
        details = execute_mikrotik_command(details_cmd)
        
        if details.strip():
            return f"Static DNS entry added successfully:\n\n{details}"
        else:
            return "Static DNS entry addition completed but unable to verify."

def mikrotik_list_dns_static(
    name_filter: Optional[str] = None,
    address_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    disabled_only: bool = False,
    regexp_only: bool = False
) -> str:
    app_logger.info(f"Listing static DNS entries with filters: name={name_filter}")
    
    cmd = "/ip dns static print"
    
    filters = []
    if name_filter:
        filters.append(f'name~"{name_filter}"')
    if address_filter:
        filters.append(f'address~"{address_filter}"')
    if type_filter:
        filters.append(f'type="{type_filter}"')
    if disabled_only:
        filters.append("disabled=yes")
    if regexp_only:
        filters.append("regexp!=\"\"")
    
    if filters:
        cmd += " where " + " ".join(filters)
    
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No static DNS entries found matching the criteria."
    
    return f"STATIC DNS ENTRIES:\n\n{result}"

def mikrotik_get_dns_static(entry_id: str) -> str:
    app_logger.info(f"Getting static DNS entry details: entry_id={entry_id}")
    
    cmd = f"/ip dns static print detail where .id={entry_id}"
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "":
        return f"Static DNS entry with ID '{entry_id}' not found."
    
    return f"STATIC DNS ENTRY DETAILS:\n\n{result}"

def mikrotik_update_dns_static(
    entry_id: str,
    name: Optional[str] = None,
    address: Optional[str] = None,
    cname: Optional[str] = None,
    mx_preference: Optional[int] = None,
    mx_exchange: Optional[str] = None,
    text: Optional[str] = None,
    srv_priority: Optional[int] = None,
    srv_weight: Optional[int] = None,
    srv_port: Optional[int] = None,
    srv_target: Optional[str] = None,
    ttl: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: Optional[bool] = None,
    regexp: Optional[str] = None
) -> str:
    app_logger.info(f"Updating static DNS entry: entry_id={entry_id}")
    
    cmd = f"/ip dns static set {entry_id}"
    
    updates = []
    if name:
        updates.append(f'name="{name}"')
    if address is not None:
        if address == "":
            updates.append("!address")
        else:
            updates.append(f"address={address}")
    if cname is not None:
        if cname == "":
            updates.append("!cname")
        else:
            updates.append(f'cname="{cname}"')
    if mx_preference is not None:
        updates.append(f"mx-preference={mx_preference}")
    if mx_exchange is not None:
        if mx_exchange == "":
            updates.append("!mx-exchange")
        else:
            updates.append(f'mx-exchange="{mx_exchange}"')
    if text is not None:
        if text == "":
            updates.append("!text")
        else:
            updates.append(f'text="{text}"')
    if srv_priority is not None:
        updates.append(f"srv-priority={srv_priority}")
    if srv_weight is not None:
        updates.append(f"srv-weight={srv_weight}")
    if srv_port is not None:
        updates.append(f"srv-port={srv_port}")
    if srv_target is not None:
        if srv_target == "":
            updates.append("!srv-target")
        else:
            updates.append(f'srv-target="{srv_target}"')
    if ttl is not None:
        if ttl == "":
            updates.append("!ttl")
        else:
            updates.append(f"ttl={ttl}")
    if comment is not None:
        updates.append(f'comment="{comment}"')
    if disabled is not None:
        updates.append(f'disabled={"yes" if disabled else "no"}')
    if regexp is not None:
        if regexp == "":
            updates.append("!regexp")
        else:
            updates.append(f'regexp="{regexp}"')
    
    if not updates:
        return "No updates specified."
    
    cmd += " " + " ".join(updates)
    
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update static DNS entry: {result}"
    
    details_cmd = f"/ip dns static print detail where .id={entry_id}"
    details = execute_mikrotik_command(details_cmd)
    
    return f"Static DNS entry updated successfully:\n\n{details}"

def mikrotik_remove_dns_static(entry_id: str) -> str:
    app_logger.info(f"Removing static DNS entry: entry_id={entry_id}")
    
    check_cmd = f"/ip dns static print count-only where .id={entry_id}"
    count = execute_mikrotik_command(check_cmd)
    
    if count.strip() == "0":
        return f"Static DNS entry with ID '{entry_id}' not found."
    
    cmd = f"/ip dns static remove {entry_id}"
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove static DNS entry: {result}"
    
    return f"Static DNS entry with ID '{entry_id}' removed successfully."

def mikrotik_enable_dns_static(entry_id: str) -> str:
    return mikrotik_update_dns_static(entry_id, disabled=False)

def mikrotik_disable_dns_static(entry_id: str) -> str:
    return mikrotik_update_dns_static(entry_id, disabled=True)

def mikrotik_get_dns_cache() -> str:
    app_logger.info("Getting DNS cache")
    
    cmd = "/ip dns cache print"
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "":
        return "DNS cache is empty."
    
    return f"DNS CACHE:\n\n{result}"

def mikrotik_flush_dns_cache() -> str:
    app_logger.info("Flushing DNS cache")
    
    cmd = "/ip dns cache flush"
    result = execute_mikrotik_command(cmd)
    
    if not result.strip():
        return "DNS cache flushed successfully."
    else:
        return f"Flush result: {result}"

def mikrotik_get_dns_cache_statistics() -> str:
    app_logger.info("Getting DNS cache statistics")
    
    cmd = "/ip dns cache print stats"
    result = execute_mikrotik_command(cmd)
    
    if not result:
        return "Unable to retrieve DNS cache statistics."
    
    return f"DNS CACHE STATISTICS:\n\n{result}"

def mikrotik_add_dns_regexp(
    regexp: str,
    address: str,
    ttl: str = "1d",
    comment: Optional[str] = None,
    disabled: bool = False
) -> str:
    app_logger.info(f"Adding DNS regexp entry: regexp={regexp}")
    
    return mikrotik_add_dns_static(
        name="dummy",
        address=address,
        regexp=regexp,
        ttl=ttl,
        comment=comment,
        disabled=disabled
    )

def mikrotik_test_dns_query(
    name: str,
    server: Optional[str] = None,
    type: str = "A"
) -> str:
    app_logger.info(f"Testing DNS query: name={name}, type={type}")
    
    cmd = f"/resolve {name}"
    
    if server:
        cmd += f" server={server}"
    
    if type != "A":
        cmd += f" type={type}"
    
    result = execute_mikrotik_command(cmd)
    
    if not result:
        return f"Failed to resolve {name}"
    
    return f"DNS QUERY RESULT for {name}:\n\n{result}"

def mikrotik_export_dns_config(filename: Optional[str] = None) -> str:
    app_logger.info("Exporting DNS configuration")
    
    if not filename:
        filename = "dns_config"
    
    cmd = f"/ip dns export file={filename}"
    result = execute_mikrotik_command(cmd)
    
    if not result.strip():
        return f"DNS configuration exported to {filename}.rsc"
    else:
        return f"Export result: {result}"