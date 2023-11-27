import threading
import sqlite3
import queue
import time

class DBThread:
    def __init__(self):
        self.conn = sqlite3.connect('casedb.sqlite', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.queue = queue.Queue()
        self.results = {}
        self.running = True
        self.thread = threading.Thread(target=self.db_thread)
        self.thread.start()

    def db_thread(self):
        while self.running:
            try:
                query, params, task_id = self.queue.get(timeout=1)
                try:
                    self.cursor.execute(query, params)
                    self.conn.commit()
                    self.results[task_id] = ('Success', None)
                except sqlite3.Error as e:
                    self.results[task_id] = ('Fail', str(e))
            except queue.Empty:
                continue

    def add_task(self, query, params):
        task_id = time.time()
        self.queue.put((query, params, task_id))
        return task_id

    def get_result(self, task_id):
        while task_id not in self.results:
            time.sleep(0.1)
        return self.results.pop(task_id)

    def stop(self):
        self.running = False
        self.thread.join()
        self.conn.close()
        