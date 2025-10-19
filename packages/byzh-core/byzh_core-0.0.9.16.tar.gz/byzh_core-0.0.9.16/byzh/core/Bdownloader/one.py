import requests
from pathlib import Path
from ..Btqdm import B_Tqdm

def b_download_file(url: str, save_path: str = None, chunk_size: int = 1024):
    """
    从指定 URL 下载文件。

    参数：
        url (str): 文件下载链接
        save_path (str): 文件保存路径，如果为 None，则保存到当前目录下的文件名与 URL 相同
        chunk_size (int): 每次读取的块大小，单位字节

    返回：
        str: 保存的文件路径
    """
    # 如果没有指定保存路径，则从 URL 获取文件名
    if save_path is None:
        save_path = Path(url).name
    save_path = Path(save_path)

    headers = {
        # 模拟浏览器访问，否则 GitHub 会403
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/117.0.0.0 Safari/537.36"
    }

    # 发送 GET 请求并以流方式下载
    with requests.get(url, stream=True, headers=headers) as r: # 发送 GET 请求下载文件
        r.raise_for_status()  # 检查请求是否成功
        total_size = r.headers.get('content-length')
        my_tqdm = B_Tqdm(range=total_size, type='MB')
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:  # 忽略空块
                    f.write(chunk)
                    my_tqdm.update(chunk_size)


    print(f"文件已保存到: {save_path}")


if __name__ == '__main__':
    b_download_file('https://github.com/FFmpeg/FFmpeg/archive/refs/tags/n7.1.2.zip')
