# -*- coding: utf-8 -*-
"""
使用多进程和tqdm对大文件进行快速XOR加密/解密.
"""
import binascii
import multiprocessing
import os

from tqdm import tqdm


def _xor_worker(args):
    """
    由进程池中的每个子进程执行的工作函数.

    Args:
        args (tuple): 包含以下元素的元组:
            - input_path (str): 输入文件的路径.
            - output_path (str): 输出文件的路径.
            - key (int): 用于XOR操作的密钥 (0-255).
            - chunk_start (int): 当前块在文件中的起始偏移量.
            - chunk_size (int): 当前块的大小.

    Returns:
        int: 处理的字节数.
    """
    input_path, output_path, key, chunk_start, chunk_size = args
    try:
        # 以二进制只读方式打开输入文件
        with open(input_path, 'rb') as f_in:
            f_in.seek(chunk_start)
            chunk = f_in.read(chunk_size)

            # 执行XOR操作
            processed_chunk = bytes(b ^ key for b in chunk)

            # 以二进制读写方式打开输出文件, 'r+b' 允许在不截断文件的情况下写入
            with open(output_path, 'r+b') as f_out:
                f_out.seek(chunk_start)
                f_out.write(processed_chunk)

        return chunk_size
    except Exception as e:
        # 在实际应用中, 更完善的错误处理是必要的
        print(f"Error processing chunk at offset {chunk_start}: {e}")
        return 0


def xor_file_multiprocess(input_path: str, output_path: str, key: int = 26):
    """
    使用多进程对大文件进行XOR加密/解密,并显示进度条.

    Args:
        input_path (str): 输入文件的路径.
        output_path (str): 输出文件的路径.
        key (int): 用于XOR操作的单个数字密钥 (0-255).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not (0 <= key <= 255):
        raise ValueError("Key must be an integer between 0 and 255.")

    file_size = os.path.getsize(input_path)
    if file_size == 0:
        # 创建一个空文件并返回
        open(output_path, 'wb').close()
        print("Input file is empty, created an empty output file.")
        return

    # 1. 预先创建并分配输出文件的大小, 避免多进程写入冲突
    with open(output_path, 'wb') as f_out:
        f_out.seek(file_size - 1)
        f_out.write(b'\0')

    # 2. 确定进程数和每个进程处理的块大小
    # 使用所有可用的CPU核心
    num_processes = multiprocessing.cpu_count()
    chunk_size = file_size // num_processes

    tasks = []
    # 3. 创建任务列表
    for i in range(num_processes):
        chunk_start = i * chunk_size
        # 对于最后一个进程, 确保它处理到文件末尾
        if i == num_processes - 1:
            current_chunk_size = file_size - chunk_start
        else:
            current_chunk_size = chunk_size

        tasks.append((input_path, output_path, key, chunk_start, current_chunk_size))

    # 4. 使用进程池并行处理任务, 并用tqdm显示进度
    print(f"Starting XOR process with {num_processes} processes...")
    with multiprocessing.Pool(processes=num_processes) as pool:
        with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Processing {os.path.basename(input_path)}") as pbar:
            # 使用 imap_unordered, 它可以按完成顺序返回结果, 使进度条更新更平滑
            for processed_bytes in pool.imap_unordered(_xor_worker, tasks):
                pbar.update(processed_bytes)

    print(f"Process finished. Output saved to: {output_path}")


def xor_with_filename(input_path: str, output_dir: str, key: int = 26):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not (0 <= key <= 255):
        raise ValueError("Key must be an integer between 0 and 255.")

    filename = os.path.basename(input_path)
    output_filename = ''.join([chr(ord(x) ^ ord(chr(key))) for x in filename])
    output_filename = binascii.b2a_hex(output_filename.encode()).decode()
    output_path = os.path.join(output_dir, output_filename)
    xor_file_multiprocess(input_path, output_path, key)
    return output_path
