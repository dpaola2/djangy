//
// Run deploy.  Must be setuid root.
//
#include <pwd.h>
#include <sys/types.h>
#include <unistd.h>
#include "config.h"

int is_trusted_user(uid_t uid)
{
    struct passwd *pw = getpwnam("shell");
    return (uid == ROOT_UID) || (uid == pw->pw_uid);
}

int main(int argc, char *argv[])
{
    const char *program_name = argv[0];
    if (is_trusted_user(getuid())) {
        setuid(0);
    }
    argv[0] = PROGRAM_DIR "shell_serve.py";
    close(1);
    dup2(2, 1);
    execv(argv[0], argv);
    perror(program_name);
}
