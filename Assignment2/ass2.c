#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>

#define SIZE 3000

typedef struct filename{

    char old[300];
    char new[300];

}filename;

pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;

void* copy(void *arg);
int main(){

    filename* name;
    int size = 1000;
    pthread_t *pid;
    int cnt = 0;
    int i;

    pid = (pthread_t*)malloc(size*sizeof(pthread_t));

    while(1){

        name = (filename*)malloc(sizeof(filename));

        printf("\nInput the file name: ");
        scanf("%s", name->old);
        printf("Input the new name: ");
        scanf("%s", name->new);

        if(cnt>=size){
            size *=2;
            pid = (pthread_t*)realloc(pid, size*sizeof(pthread_t));
            printf("here");
        }

        pthread_create(&pid[cnt++], NULL, copy, (void*)name);

    }

    for(i=0; i<cnt; i++){
        pthread_join(pid[i], NULL);
    }

    return 0;

}

void* copy(void *arg){

    filename *name = (filename*)arg;

    int fdold;
    int fdnew;
    int cnt;
    char temp[SIZE+1];
    FILE *fdlog;

    clock_t start, end;

    pthread_mutex_lock(&m);
    start = clock();
    fdlog = fopen("log.txt", "a");
    fprintf(fdlog, "%.2lf Strat copying %s to %s\n", (double)start/CLOCKS_PER_SEC, name->old, name->new);
    fclose(fdlog);
    pthread_mutex_unlock(&m);

    fdold = open(name->old, O_RDONLY);
    if(fdold == -1){
        printf("file open error: %s\n", strerror(errno));
        return 0;
    }

    fdnew = open(name->new, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if(fdnew == -1){
        printf("new file open error: %s\n", strerror(errno));
        return 0;
    }


    for(int i=0; ; i++){

        cnt = read(fdold, temp, SIZE);

        write(fdnew, temp, cnt);

        if(cnt < SIZE)
            break;

    }

    pthread_mutex_lock(&m);
    end = clock();
    fdlog = fopen("log.txt", "a");
    fprintf(fdlog, "%.2lf %s is copied completely\n", (double)end/CLOCKS_PER_SEC, name->new);
    fclose(fdlog);
    pthread_mutex_unlock(&m);


    close(fdnew);
    close(fdold);

    free(name);

}
