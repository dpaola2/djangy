//
// Run configure_proxycache.  Must be setuid root.
//
#include "run.h"

MAIN("configure_proxycache.py")

int is_trusted_user(uid_t uid)
{
    return (uid == ROOT_UID);
}
