//
// Run clear_cache.  Must be setuid root.
//
#include "run.h"

MAIN("clear_cache.py")

int is_trusted_user(uid_t uid)
{
    return (uid == ROOT_UID);
}
