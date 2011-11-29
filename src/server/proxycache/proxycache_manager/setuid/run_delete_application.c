//
// Run delete_application.  Must be setuid root.
//
#include "run.h"

MAIN("delete_application.py")

int is_trusted_user(uid_t uid)
{
    return (uid == ROOT_UID);
}
