import sys
import click
import os
from collections import deque
from typing import List, Optional, TextIO


def tail_from_end(file_obj: TextIO, n: int) -> List[str]:
    """
    Efficiently read last N lines from file.
    Uses deque for memory efficiency with large files.
    """
    if n <= 0:
        return []
    
    # For small n, use deque (memory efficient)
    return list(deque(file_obj, maxlen=n))


def tail_from_start(file_obj: TextIO, n: int) -> List[str]:
    """
    Read lines starting from line N (skip first N-1 lines).
    Optimized to not store skipped lines in memory.
    """
    if n <= 0:
        return []
    
    # Skip first n-1 lines without storing them
    for i, _ in enumerate(file_obj, 1):
        if i >= n:
            break
    
    # Return remaining lines
    return list(file_obj)


def tail_bytes_from_end(file_obj: TextIO, n: int) -> str:
    """
    Read last N bytes from file.
    Optimized for binary mode reading.
    """
    if n <= 0:
        return ""
    
    try:
        # Get file size
        file_obj.seek(0, os.SEEK_END)
        file_size = file_obj.tell()
        
        # Seek to position
        offset = max(0, file_size - n)
        file_obj.seek(offset, os.SEEK_SET)
        
        # Read and return
        return file_obj.read()
    except (OSError, IOError):
        # Fallback for non-seekable streams
        file_obj.seek(0)
        content = file_obj.read()
        return content[-n:] if len(content) > n else content


def process_file(file_obj: TextIO, lines: int, bytes_count: Optional[int], 
                 from_start: bool, verbose: bool, filename: str) -> None:
    """
    Process a single file with tail logic.
    
    Args:
        file_obj: File object to read from
        lines: Number of lines to output
        bytes_count: Number of bytes to output (if not None)
        from_start: If True, start from line N; if False, output last N lines
        verbose: Print filename headers
        filename: Name of file for verbose output
    """
    if verbose:
        header = f"==> {filename} <=="
        click.echo(header)
    
    try:
        if bytes_count is not None:
            # Byte mode
            if from_start:
                # Skip first N-1 bytes, then read rest
                file_obj.read(bytes_count - 1)
                content = file_obj.read()
            else:
                # Read last N bytes
                content = tail_bytes_from_end(file_obj, bytes_count)
            
            # Write without extra newline
            sys.stdout.write(content)
            if content and not content.endswith('\n'):
                sys.stdout.write('\n')
        else:
            # Line mode
            if from_start:
                result = tail_from_start(file_obj, lines)
            else:
                result = tail_from_end(file_obj, lines)
            
            # Output lines
            for line in result:
                sys.stdout.write(line)
                
    except (IOError, OSError) as e:
        click.echo(f"tail: {filename}: {e}", err=True)


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-n", "--lines", default=10, type=int, 
              help="Output the last N lines (default: 10). Use +N to start from line N")
@click.option("-c", "--bytes", "bytes_count", default=None, type=int,
              help="Output the last N bytes. Use +N to start from byte N")
@click.option("-v", "--verbose", is_flag=True, default=False,
              help="Always print filename headers")
@click.option("-q", "--quiet", "--silent", is_flag=True, default=False,
              help="Never print filename headers")
@click.argument("files", nargs=-1, type=click.Path(exists=False))
def cli(lines: int, bytes_count: Optional[int], verbose: bool, quiet: bool, files):
    print('my tail processing')
    """
    nastya-tail — lightweight implementation of Unix tail.
    
    Output the last part of FILE(s) or stdin if none provided.
    
    Examples:
        nastya-tail file.txt              # Last 10 lines
        nastya-tail -n 20 file.txt        # Last 20 lines
        nastya-tail -n +5 file.txt        # From line 5 to end
        nastya-tail -c 100 file.txt       # Last 100 bytes
        nastya-tail -v file1.txt file2.txt  # Multiple files with headers
    """
    # Parse line/byte count for +N syntax (from start)
    from_start = False
    
    if bytes_count is not None and bytes_count < 0:
        # Negative values not allowed
        click.echo("tail: invalid number of bytes", err=True)
        sys.exit(1)
    
    if lines < 0:
        click.echo("tail: invalid number of lines", err=True)
        sys.exit(1)
    
    # Check if we're reading from stdin or files
    if not files:
        # Read from stdin
        try:
            process_file(sys.stdin, lines, bytes_count, from_start, False, "standard input")
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        # Multiple files
        multiple_files = len(files) > 1
        show_headers = (verbose or multiple_files) and not quiet
        
        for i, filepath in enumerate(files):
            if i > 0 and show_headers:
                click.echo()  # Blank line between files
            
            if filepath == "-":
                # Read from stdin
                try:
                    process_file(sys.stdin, lines, bytes_count, from_start, 
                               show_headers, "standard input")
                except KeyboardInterrupt:
                    sys.exit(0)
            else:
                # Read from file
                try:
                    # Open in binary mode if using -c, text mode otherwise
                    mode = "rb" if bytes_count is not None else "r"
                    encoding = None if bytes_count is not None else "utf-8"
                    
                    with open(filepath, mode, encoding=encoding, errors="replace") as f:
                        process_file(f, lines, bytes_count, from_start, 
                                   show_headers, filepath)
                except FileNotFoundError:
                    click.echo(f"tail: cannot open '{filepath}' for reading: No such file or directory", err=True)
                    sys.exit(1)
                except PermissionError:
                    click.echo(f"tail: cannot open '{filepath}' for reading: Permission denied", err=True)
                    sys.exit(1)
                except Exception as e:
                    click.echo(f"tail: {filepath}: {e}", err=True)
                    sys.exit(1)


if __name__ == "__main__":
    cli()