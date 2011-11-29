//
// Run allocate.  Must be setuid root.
//
#include "run.h"

MAIN("allocate.py")

int is_trusted_user(uid_t uid)
{
    return (uid == ROOT_UID);
}
