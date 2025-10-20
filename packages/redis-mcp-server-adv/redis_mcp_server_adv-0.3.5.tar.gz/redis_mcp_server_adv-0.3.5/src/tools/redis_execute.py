from typing import Any, List, Optional, Union

from redis.exceptions import RedisError

from src.common.connection import RedisConnectionManager
from src.common.server import mcp


@mcp.tool()
async def redis_execute_command(
    command: str,
    args: Optional[List[Union[str, int, float]]] = None
) -> Any:
    """Execute arbitrary Redis command. This tool is available in lite mode for maximum flexibility.

    Args:
        command: Redis command name (e.g., "GET", "SET", "HGET", "ZADD", etc.)
        args: Optional list of command arguments. Can include strings, numbers, or lists.

    Returns:
        Redis server response. The return type depends on the command executed.
        - String commands return strings
        - List commands return lists
        - Hash commands return dictionaries or strings
        - Numeric commands return integers
        - Boolean operations return 0/1
        - Error commands return error messages

    Examples:
        redis_execute_command("GET", ["mykey"])
        redis_execute_command("SET", ["mykey", "myvalue"])
        redis_execute_command("HGET", ["myhash", "myfield"])
        redis_execute_command("ZADD", ["mysortedset", 1, "member1", 2, "member2"])
        redis_execute_command("INCR", ["mycounter"])
    """
    try:
        r = RedisConnectionManager.get_connection()

        # Validate command
        if not command:
            return "Error: Command cannot be empty"

        # Normalize command to uppercase
        command = command.upper()

        # Execute command with or without arguments
        if args is None or len(args) == 0:
            result = r.execute_command(command)
        else:
            # Flatten nested lists for commands like ZADD
            flat_args = []
            for arg in args:
                if isinstance(arg, list):
                    flat_args.extend(arg)
                else:
                    flat_args.append(arg)

            result = r.execute_command(command, *flat_args)

        # Handle different result types appropriately
        if isinstance(result, bytes):
            try:
                return result.decode('utf-8')
            except UnicodeDecodeError:
                return result
        elif isinstance(result, dict):
            # Handle bytes keys/values in dictionaries
            return {
                (k.decode('utf-8') if isinstance(k, bytes) else k):
                (v.decode('utf-8') if isinstance(v, bytes) else v)
                for k, v in result.items()
            }
        elif isinstance(result, list):
            # Handle bytes in lists
            return [
                item.decode('utf-8') if isinstance(item, bytes) else item
                for item in result
            ]
        else:
            return result

    except RedisError as e:
        return f"Redis error executing command '{command}': {str(e)}"
    except Exception as e:
        return f"Error executing command '{command}': {str(e)}"


@mcp.tool()
async def redis_execute_raw_command(command_str: str) -> Any:
    """Execute Redis command from a raw command string. This tool is available in lite mode.

    Args:
        command_str: Complete Redis command as string (e.g., "SET mykey myvalue", "GET mykey")

    Returns:
        Redis server response

    Examples:
        redis_execute_raw_command("SET mykey myvalue")
        redis_execute_raw_command("HGET myhash myfield")
        redis_execute_raw_command("ZADD mysortedset 1 member1 2 member2")
    """
    try:
        # Parse command string
        parts = command_str.strip().split()
        if not parts:
            return "Error: Command string cannot be empty"

        command = parts[0].upper()
        args = parts[1:] if len(parts) > 1 else None

        # Convert numeric strings to appropriate types
        if args:
            converted_args = []
            for arg in args:
                # Try to convert to int, then float, keep as string if both fail
                try:
                    converted_args.append(int(arg))
                except ValueError:
                    try:
                        converted_args.append(float(arg))
                    except ValueError:
                        converted_args.append(arg)
            args = converted_args

        # Execute using the main function
        return await redis_execute_command(command, args)

    except Exception as e:
        return f"Error parsing command string '{command_str}': {str(e)}"