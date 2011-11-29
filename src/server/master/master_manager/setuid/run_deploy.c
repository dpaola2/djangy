//
// Run deploy.  Must be setuid root.
//
#include "run.h"

MAIN("deploy.py")

int is_trusted_user(uid_t uid)
{
    return (uid == ROOT_UID);
}
