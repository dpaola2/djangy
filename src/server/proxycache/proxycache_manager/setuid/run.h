#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>

#include "config.h"

int is_trusted_user(uid_t uid);

#define MAIN(PROGRAM) \
int main(int argc, char *argv[]) \
{ \
    char *envp[] = {"PATH=" PATH, \
                    "VIRTUAL_ENV=" VIRTUAL_ENV, \
                    NULL}; \
    const char *program_name = argv[0]; \
    if (is_trusted_user(getuid())) { \
        setuid(0); \
    } \
    argv[0] = PROGRAM_DIR PROGRAM; \
    execve(argv[0], argv, envp); \
    perror(program_name); \
}
