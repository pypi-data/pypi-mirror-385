from typing import Optional, List
from ..connector import execute_mikrotik_command
from ..logger import app_logger
import re

def mikrotik_add_user(
    name: str,
    password: str,
    group: str = "read",
    address: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: bool = False
) -> str:
    app_logger.info(f"Adding user: name={name}, group={group}")
    
    cmd = f'/user add name="{name}" password="{password}" group={group}'
    
    if address:
        cmd += f" address={address}"
    
    if comment:
        cmd += f' comment="{comment}"'
    
    if disabled:
        cmd += " disabled=yes"
    
    result = execute_mikrotik_command(cmd)
    
    if result.strip():
        if "*" in result or result.strip().isdigit():
            user_id = result.strip()
            details_cmd = f"/user print detail where .id={user_id}"
            details = execute_mikrotik_command(details_cmd)
            
            if details.strip():
                # Remove password from output for security
                details = re.sub(r'password="[^"]*"', 'password="***"', details)
                return f"User created successfully:\n\n{details}"
            else:
                return f"User created with ID: {result}"
        else:
            return f"Failed to create user: {result}"
    else:
        details_cmd = f'/user print detail where name="{name}"'
        details = execute_mikrotik_command(details_cmd)
        
        if details.strip():
            details = re.sub(r'password="[^"]*"', 'password="***"', details)
            return f"User created successfully:\n\n{details}"
        else:
            return "User creation completed but unable to verify."

def mikrotik_list_users(
    name_filter: Optional[str] = None,
    group_filter: Optional[str] = None,
    disabled_only: bool = False,
    active_only: bool = False
) -> str:
    app_logger.info(f"Listing users with filters: name={name_filter}, group={group_filter}")
    
    cmd = "/user print"
    
    filters = []
    if name_filter:
        filters.append(f'name~"{name_filter}"')
    if group_filter:
        filters.append(f'group="{group_filter}"')
    if disabled_only:
        filters.append("disabled=yes")
    
    if filters:
        cmd += " where " + " ".join(filters)
    
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No users found matching the criteria."
    
    # Remove passwords from output
    result = re.sub(r'password="[^"]*"', 'password="***"', result)
    
    return f"USERS:\n\n{result}"

def mikrotik_get_user(name: str) -> str:
    app_logger.info(f"Getting user details: name={name}")
    
    cmd = f'/user print detail where name="{name}"'
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "":
        return f"User '{name}' not found."
    
    # Remove password from output
    result = re.sub(r'password="[^"]*"', 'password="***"', result)
    
    return f"USER DETAILS:\n\n{result}"

def mikrotik_update_user(
    name: str,
    new_name: Optional[str] = None,
    password: Optional[str] = None,
    group: Optional[str] = None,
    address: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: Optional[bool] = None
) -> str:
    app_logger.info(f"Updating user: name={name}")
    
    cmd = f'/user set [find name="{name}"]'
    
    updates = []
    if new_name:
        updates.append(f'name="{new_name}"')
    if password:
        updates.append(f'password="{password}"')
    if group:
        updates.append(f'group={group}')
    if address is not None:
        if address == "":
            updates.append("!address")
        else:
            updates.append(f"address={address}")
    if comment is not None:
        updates.append(f'comment="{comment}"')
    if disabled is not None:
        updates.append(f'disabled={"yes" if disabled else "no"}')
    
    if not updates:
        return "No updates specified."
    
    cmd += " " + " ".join(updates)
    
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update user: {result}"
    
    details_name = new_name if new_name else name
    details_cmd = f'/user print detail where name="{details_name}"'
    details = execute_mikrotik_command(details_cmd)
    
    # Remove password from output
    details = re.sub(r'password="[^"]*"', 'password="***"', details)
    
    return f"User updated successfully:\n\n{details}"

def mikrotik_remove_user(name: str) -> str:
    app_logger.info(f"Removing user: name={name}")
    
    # Don't allow removal of admin user
    if name.lower() == "admin":
        return "Cannot remove the admin user."
    
    check_cmd = f'/user print count-only where name="{name}"'
    count = execute_mikrotik_command(check_cmd)
    
    if count.strip() == "0":
        return f"User '{name}' not found."
    
    cmd = f'/user remove [find name="{name}"]'
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove user: {result}"
    
    return f"User '{name}' removed successfully."

def mikrotik_disable_user(name: str) -> str:
    return mikrotik_update_user(name, disabled=True)

def mikrotik_enable_user(name: str) -> str:
    return mikrotik_update_user(name, disabled=False)

def mikrotik_add_user_group(
    name: str,
    policy: List[str],
    skin: Optional[str] = None,
    comment: Optional[str] = None
) -> str:
    app_logger.info(f"Adding user group: name={name}")
    
    # Valid policies
    valid_policies = [
        "local", "telnet", "ssh", "ftp", "reboot", "read", "write", 
        "policy", "test", "winbox", "password", "web", "sniff",
        "sensitive", "api", "romon", "dude", "tikapp", "rest-api"
    ]
    
    # Validate policies
    for p in policy:
        if p not in valid_policies:
            return f"Invalid policy: {p}. Valid policies: {', '.join(valid_policies)}"
    
    cmd = f'/user group add name="{name}" policy={",".join(policy)}'
    
    if skin:
        cmd += f' skin="{skin}"'
    
    if comment:
        cmd += f' comment="{comment}"'
    
    result = execute_mikrotik_command(cmd)
    
    if result.strip():
        if "*" in result or result.strip().isdigit():
            group_id = result.strip()
            details_cmd = f"/user group print detail where .id={group_id}"
            details = execute_mikrotik_command(details_cmd)
            
            if details.strip():
                return f"User group created successfully:\n\n{details}"
            else:
                return f"User group created with ID: {result}"
        else:
            return f"Failed to create user group: {result}"
    else:
        details_cmd = f'/user group print detail where name="{name}"'
        details = execute_mikrotik_command(details_cmd)
        
        if details.strip():
            return f"User group created successfully:\n\n{details}"
        else:
            return "User group creation completed but unable to verify."

def mikrotik_list_user_groups(
    name_filter: Optional[str] = None,
    policy_filter: Optional[str] = None
) -> str:
    app_logger.info(f"Listing user groups with filters: name={name_filter}")
    
    cmd = "/user group print"
    
    filters = []
    if name_filter:
        filters.append(f'name~"{name_filter}"')
    if policy_filter:
        filters.append(f'policy~"{policy_filter}"')
    
    if filters:
        cmd += " where " + " ".join(filters)
    
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No user groups found matching the criteria."
    
    return f"USER GROUPS:\n\n{result}"

def mikrotik_get_user_group(name: str) -> str:
    app_logger.info(f"Getting user group details: name={name}")
    
    cmd = f'/user group print detail where name="{name}"'
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "":
        return f"User group '{name}' not found."
    
    return f"USER GROUP DETAILS:\n\n{result}"

def mikrotik_update_user_group(
    name: str,
    new_name: Optional[str] = None,
    policy: Optional[List[str]] = None,
    skin: Optional[str] = None,
    comment: Optional[str] = None
) -> str:
    app_logger.info(f"Updating user group: name={name}")
    
    # Don't allow modification of built-in groups
    if name in ["read", "write", "full"]:
        return f"Cannot modify built-in group '{name}'."
    
    cmd = f'/user group set [find name="{name}"]'
    
    updates = []
    if new_name:
        updates.append(f'name="{new_name}"')
    if policy:
        updates.append(f'policy={",".join(policy)}')
    if skin is not None:
        if skin == "":
            updates.append("!skin")
        else:
            updates.append(f'skin="{skin}"')
    if comment is not None:
        updates.append(f'comment="{comment}"')
    
    if not updates:
        return "No updates specified."
    
    cmd += " " + " ".join(updates)
    
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update user group: {result}"
    
    details_name = new_name if new_name else name
    details_cmd = f'/user group print detail where name="{details_name}"'
    details = execute_mikrotik_command(details_cmd)
    
    return f"User group updated successfully:\n\n{details}"

def mikrotik_remove_user_group(name: str) -> str:
    app_logger.info(f"Removing user group: name={name}")
    
    # Don't allow removal of built-in groups
    if name in ["read", "write", "full"]:
        return f"Cannot remove built-in group '{name}'."
    
    check_cmd = f'/user group print count-only where name="{name}"'
    count = execute_mikrotik_command(check_cmd)
    
    if count.strip() == "0":
        return f"User group '{name}' not found."
    
    # Check if group is in use
    users_cmd = f'/user print count-only where group="{name}"'
    users_count = execute_mikrotik_command(users_cmd)
    
    if users_count.strip() != "0":
        return f"Cannot remove group '{name}': {users_count.strip()} users are using this group."
    
    cmd = f'/user group remove [find name="{name}"]'
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove user group: {result}"
    
    return f"User group '{name}' removed successfully."

def mikrotik_get_active_users() -> str:
    app_logger.info("Getting active users")
    
    cmd = "/user active print"
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "":
        return "No active users found."
    
    return f"ACTIVE USERS:\n\n{result}"

def mikrotik_disconnect_user(user_id: str) -> str:
    app_logger.info(f"Disconnecting user: user_id={user_id}")
    
    cmd = f"/user active remove {user_id}"
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to disconnect user: {result}"
    
    return f"User session {user_id} disconnected successfully."

def mikrotik_export_user_config(filename: Optional[str] = None) -> str:
    app_logger.info("Exporting user configuration")
    
    if not filename:
        filename = "user_config"
    
    cmd = f"/user export file={filename}"
    result = execute_mikrotik_command(cmd)
    
    if not result.strip():
        return f"User configuration exported to {filename}.rsc"
    else:
        return f"Export result: {result}"

def mikrotik_set_user_ssh_keys(
    username: str,
    key_file: str
) -> str:
    app_logger.info(f"Setting SSH keys for user: {username}")
    
    cmd = f'/user ssh-keys import user="{username}" public-key-file="{key_file}"'
    result = execute_mikrotik_command(cmd)
    
    if not result.strip() or "imported" in result.lower():
        return f"SSH key imported successfully for user '{username}'."
    else:
        return f"Failed to import SSH key: {result}"

def mikrotik_list_user_ssh_keys(username: str) -> str:
    app_logger.info(f"Listing SSH keys for user: {username}")
    
    cmd = f'/user ssh-keys print where user="{username}"'
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "":
        return f"No SSH keys found for user '{username}'."
    
    return f"SSH KEYS for {username}:\n\n{result}"

def mikrotik_remove_user_ssh_key(key_id: str) -> str:
    app_logger.info(f"Removing SSH key: key_id={key_id}")
    
    cmd = f"/user ssh-keys remove {key_id}"
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove SSH key: {result}"
    
    return f"SSH key {key_id} removed successfully."