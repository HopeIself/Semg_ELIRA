import queue

# 全局唯一的UDP数据队列
UDP_DATA_QUEUE = queue.Queue(maxsize=1000)
