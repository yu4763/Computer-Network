#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>

#define SIZE 3000

int main(){

    char old[300], new[300];
    int fdold, fdnew;
    int cnt;
    char temp[SIZE+1];
    int fdlog;

    printf("Input the file name: ");
    scanf("%s", old);
    printf("Input the new name: ");
    scanf("%s", new);

    fdold = open(old, O_RDONLY);
    if(fdold == -1){
        printf("file open error: %s\n", strerror(errno));
        return 0;
    }

    fdnew = open(new, O_WRONLY | O_CREAT | O_TRUNC, 0644);
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

    fdlog = open("log.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    write(fdlog, "file copy is done", 17);
    close(fdlog);

    close(fdnew);
    close(fdold);


    return 0;

}
