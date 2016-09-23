#include <cstdint>
#include <cstdio>
#include <cstdlib>

#include <string>
#include <thread>
#include <vector>

void usage(const char* exe) {
  printf("usage:\n  %s usleep num_threads\n", exe);
}

void waitOn(const uint8_t* kill) {
  while (*kill == 0) {
    std::this_thread::sleep_for(std::chrono::microseconds(100));
  }
  printf("thread done\n");
}

int main(int argc, char** argv) {
  for (int i = 0; i < argc; i++) {
    if ((std::string(argv[i]) == "-h") ||
        (std::string(argv[i]) == "--help") ||
        (argc != 3)) {
      usage(argv[0]);
      return -1;
    }
  }

  char* ep;
  uint64_t usleep = strtoull(argv[1], &ep, 0);
  if (*ep != '\0') {
    printf("invalid usleep: %s\n", argv[1]);
    usage(argv[0]);
    return -1;
  }
  uint64_t numThreads = strtoull(argv[2], &ep, 0);
  if (*ep != '\0') {
    printf("invalid num_blocks: %s\n", argv[2]);
    usage(argv[0]);
    return -1;
  }

  std::vector<std::thread*> ptrs(numThreads, nullptr);
  std::vector<uint8_t> kills(numThreads);
  uint64_t threads = 0;
  printf("+threads=%lu\n", threads);
  for (uint64_t idx = 0; idx < numThreads; idx++) {
    kills[idx] = 0;
    ptrs[idx] = new std::thread(waitOn, &kills[idx]);
    threads++;
    printf("+threads=%lu\n", threads);
    std::this_thread::sleep_for(std::chrono::microseconds(usleep));
  }
  printf("all spawned\n");

  for (uint64_t idx = 0; idx < numThreads; idx++) {
    // tell the thread to stop and join
    kills[idx] = 1;
    ptrs[idx]->join();

    // clean up
    delete ptrs[idx];
    threads--;
    printf("-threads=%lu\n", threads);
    std::this_thread::sleep_for(std::chrono::microseconds(usleep));
  }

  return 0;
}
