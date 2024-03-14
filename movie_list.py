import csv
import json
import threading
import time
import re

import requests
import tqdm

# csv互斥锁
csv_lock = threading.Lock()
# 控制线程数
MAX_THREADS = 10
# 请求间隔时间
REQUEST_INTERVAL = 0.1


def get_movie_list(page: int, pbar: tqdm.tqdm, get_genre) -> None:
    url = "https://api.themoviedb.org/3/discover/movie"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyZTJiNWVjN2M5NmE5Nzk1MGE1MDJlMzk1MWMzZmRkNCIsInN1YiI6IjY1ZjIzN2RlZmJlMzZmMDE4NWVmZTJjZSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.0xB5s2dJJONa7P9-W5oD5B74DgWf6bZwTiixveJ55po"
    }
    try:
        response = requests.get(url, headers=headers, params={'page': page}).json()
        data: list[tuple[str, float, str]] = []
        for item in response['results']:
            if not check_data(item['genre_ids'], item['popularity'], item['release_date']):
                print(f'page: {page} item: {item} dropped')
                continue
            genres = '/'.join([get_genre[genre_id] for genre_id in item['genre_ids']])
            popularity = item['popularity']
            release_date = item['release_date']
            data.append((genres, popularity, release_date))
        with csv_lock:
            with open(r'./output.csv', 'a', newline='', encoding='utf-8') as output:
                writer = csv.writer(output)
                writer.writerows(data)
        pbar.update(1)
    except requests.exceptions.RequestException as response_err:
        print(f'Request failed for page {page}: {response_err}')
        time.sleep(REQUEST_INTERVAL)  # 增加延迟
        get_movie_list(page, pbar, get_genre)  # 重试请求
    except KeyError:  # 体裁不存在，直接跳过
        print(f'KeyError for page {page}')
        return


# 数据合规性检查
def check_data(genres, popularity, release_date) -> bool:
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if len(genres) > 0 and popularity is not None and date_pattern.match(release_date):
        return True
    else:
        return False


if __name__ == '__main__':
    # 读取体裁字典
    with open('./genres_dict.json', 'r', encoding='utf-8') as file:
        genres_dict = json.load(file, object_hook=lambda x: {int(k): v for k, v in x.items()})  # 将键值转换为int
    # 清空输出文件
    with open('./output.csv', 'w', encoding='utf-8') as file:
        pass
    # 线程列表
    threads = []
    # 多线程进度条显示
    progress_bar = tqdm.tqdm(total=500)
    # 请求500页数据
    for i in range(1, 501):
        while threading.active_count() > MAX_THREADS:  # 控制线程数量
            time.sleep(REQUEST_INTERVAL)
        thread = threading.Thread(target=get_movie_list, args=(i, progress_bar, genres_dict))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    progress_bar.close()
    print('done')
