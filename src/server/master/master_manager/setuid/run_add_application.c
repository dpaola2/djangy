//
// Run deploy.  Must be setuid root.
//
#include "run.h"

MAIN("add_application.py")

int is_trusted_user(uid_t uid)
{
    return (uid == ROOT_UID) || (uid == WWW_DATA_UID);
}
