//
// Run stop.  Must be setuid root.
//
#include "run.h"

MAIN("stop.py")

int is_trusted_user(uid_t uid)
{
    return (uid == ROOT_UID);
}
