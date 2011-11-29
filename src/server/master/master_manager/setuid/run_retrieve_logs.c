//
// Run deploy.  Must be setuid root.
//
#include "run.h"

MAIN("retrieve_logs.py")

int is_trusted_user(uid_t uid)
{
    return (uid == ROOT_UID);
}
