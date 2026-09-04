import time

from src.manager.cache.cache_manager import NovaCacheManager

cache = NovaCacheManager()

cache.set("test", "Hello Redis!", 10)
cache.set("test2", "Hello Redis 1")
cache.set("test1", "Hello Redis 2", 30)

print(f"test = {cache.get("test")} after 0 sec")
print(f"test1 = {cache.get("test1")} after 0 sec")
print(f"test2 = {cache.get("test2")} after 0 sec")

time.sleep(11)

print(f"test = {cache.get("test")} after 11 sec")
print(f"test1 = {cache.get("test1")} after 11 sec")
print(f"test2 = {cache.get("test2")} after 11 sec")

time.sleep(31)

print(f"test = {cache.get("test")} after 42 sec")
print(f"test1 = {cache.get("test1")} after 42 sec")
print(f"test2 = {cache.get("test2")} after 42 sec")


time.sleep(17)

print(f"test = {cache.get("test")} after 59 sec")
print(f"test1 = {cache.get("test1")} after 59 sec")
print(f"test2 = {cache.get("test2")} after 59 sec")


time.sleep(2)

print(f"test = {cache.get("test")} after 61 sec")
print(f"test1 = {cache.get("test1")} after 61 sec")
print(f"test2 = {cache.get("test2")} after 61 sec")
