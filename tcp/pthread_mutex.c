#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

int sharei = 0;
void* increase_num(void*); // 正确声明 increase_num 作为线程函数
// 添加互斥锁
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
static int count = 0;

int main() {
    int ret;
    pthread_t thread1, thread2, thread3;
    
    // 使用正确的线程函数签名
    ret = pthread_create(&thread1, NULL, increase_num, NULL);
    ret = pthread_create(&thread2, NULL, increase_num, NULL);
    ret = pthread_create(&thread3, NULL, increase_num, NULL);

    // pthread_join(thread1, NULL);
    // pthread_join(thread2, NULL);
    // pthread_join(thread3, NULL);

    printf("sharei = %d\n", sharei);
    printf("%d\n", count);
    return 0;
}

void* increase_num(void* arg) {
    long i, tmp;

    count = count + 1;
    for (i = 0; i <= 10000; ++i) {
        // 上锁
        if (pthread_mutex_lock(&mutex) != 0) {
            perror("pthread_mutex_lock");
            exit(EXIT_FAILURE);
        }
        tmp = sharei;
        tmp = tmp + 1;
        sharei = tmp;
        // 解锁
        if (pthread_mutex_unlock(&mutex) != 0) {
            perror("pthread_mutex_unlock");
            exit(EXIT_FAILURE);
        }
    }


    pthread_exit(NULL);
}
